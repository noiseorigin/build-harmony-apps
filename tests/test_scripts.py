from __future__ import annotations

import importlib.util
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parent.parent


def run_script(relative: str, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / relative), *args],
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
        env=env,
    )


def make_harmony_project(parent: Path) -> Path:
    project = parent / "Demo"
    (project / "entry/src").mkdir(parents=True)
    (project / "build-profile.json5").write_text("{}", encoding="utf-8")
    app_scope = project / "AppScope"
    app_scope.mkdir()
    (app_scope / "app.json5").write_text('{"app":{"bundleName":"com.example.demo"}}', encoding="utf-8")
    return project


def isolated_detector_env(parent: Path) -> tuple[dict[str, str], Path]:
    bin_dir = parent / "bin"
    bin_dir.mkdir()
    empty_toolchain = parent / "empty-deveco"
    empty_toolchain.mkdir()
    env = os.environ.copy()
    for key in (
        "DEVECO_CLI_STUDIO_PATH",
        "DEVECO_CLI_CLT_PATH",
        "DEVECO_HOME",
        "DEVECO_STUDIO_HOME",
        "JAVA_HOME",
    ):
        env.pop(key, None)
    env.update(
        {
            "PATH": str(bin_dir),
            "DEVECO_HOME": str(empty_toolchain),
            "DEVECO_CLI_DISABLE_TELEMETRY": "1",
            "DEVECO_CLI_SKIP_VERSION_CHECK": "1",
        }
    )
    return env, bin_dir


def write_fake_devecocli(bin_dir: Path, output: str, exit_code: int = 0) -> Path:
    executable = bin_dir / "devecocli"
    executable.write_text(f"#!/bin/sh\nprintf '%s\\n' '{output}'\nexit {exit_code}\n", encoding="utf-8")
    executable.chmod(0o755)
    return executable


def make_raw_toolchain(root: Path, kind: str) -> None:
    hdc = root / "sdk/default/openharmony/toolchains/hdc"
    prefix = root / "tools" if kind == "studio" else root
    hvigor = prefix / "hvigor/bin/hvigorw"
    hdc.parent.mkdir(parents=True)
    hvigor.parent.mkdir(parents=True)
    hdc.touch()
    hvigor.touch()


class ScriptTests(unittest.TestCase):
    def test_detect_environment_and_project(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            project = make_harmony_project(root)
            env, _ = isolated_detector_env(root)
            result = run_script(
                "skills/harmony-debugger-agent/scripts/detect_harmony_env.py",
                "--project",
                str(project / "entry/src"),
                env=env,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data["projectRoot"], str(project.resolve()))
            self.assertEqual(data["bundleName"], "com.example.demo")

    def test_devecocli_missing_is_not_ready(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            project = make_harmony_project(root)
            env, _ = isolated_detector_env(root)
            result = run_script(
                "skills/harmony-debugger-agent/scripts/detect_harmony_env.py",
                "--project",
                str(project),
                "--strict",
                env=env,
            )
            self.assertEqual(result.returncode, 2, result.stderr)
            data = json.loads(result.stdout)
            self.assertIsNone(data["cli"]["path"])
            self.assertIsNone(data["cli"]["version"])
            self.assertFalse(data["cli"]["ready"])
            self.assertIn("not found", data["cli"]["error"])
            self.assertIsNone(data["tools"]["devecocli"])
            self.assertFalse(data["toolchain"]["ready"])

    def test_devecocli_older_than_130_is_not_ready(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            project = make_harmony_project(root)
            env, bin_dir = isolated_detector_env(root)
            executable = write_fake_devecocli(bin_dir, "devecocli 1.2.9")
            result = run_script(
                "skills/harmony-debugger-agent/scripts/detect_harmony_env.py",
                "--project",
                str(project),
                "--strict",
                env=env,
            )
            self.assertEqual(result.returncode, 2, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data["cli"]["path"], str(executable))
            self.assertEqual(data["cli"]["version"], "1.2.9")
            self.assertFalse(data["cli"]["ready"])
            self.assertIn("older", data["cli"]["error"])
            self.assertEqual(data["tools"]["devecocli"], str(executable))

    def test_devecocli_130_version_formats_are_ready(self) -> None:
        for output in ("1.3.0", "v1.3.0"):
            with self.subTest(output=output), tempfile.TemporaryDirectory() as raw:
                root = Path(raw)
                project = make_harmony_project(root)
                env, bin_dir = isolated_detector_env(root)
                write_fake_devecocli(bin_dir, output)
                result = run_script(
                    "skills/harmony-debugger-agent/scripts/detect_harmony_env.py",
                    "--project",
                    str(project),
                    "--strict",
                    env=env,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                data = json.loads(result.stdout)
                self.assertEqual(data["cli"]["version"], "1.3.0")
                self.assertEqual(data["cli"]["minimumVersion"], "1.3.0")
                self.assertTrue(data["cli"]["ready"])
                self.assertIsNone(data["cli"]["error"])
                self.assertFalse(data["toolchain"]["ready"])

    def test_devecocli_new_major_requires_contract_review(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            project = make_harmony_project(root)
            env, bin_dir = isolated_detector_env(root)
            write_fake_devecocli(bin_dir, "2.0.0")
            result = run_script(
                "skills/harmony-debugger-agent/scripts/detect_harmony_env.py",
                "--project",
                str(project),
                "--strict",
                env=env,
            )
            self.assertEqual(result.returncode, 2, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data["cli"]["supportedMajor"], 1)
            self.assertFalse(data["cli"]["ready"])
            self.assertIn("unsupported major", data["cli"]["error"])

    def test_devecocli_version_probe_failure_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            project = make_harmony_project(root)
            env, bin_dir = isolated_detector_env(root)
            executable = write_fake_devecocli(bin_dir, "sandbox denied", exit_code=7)
            result = run_script(
                "skills/harmony-debugger-agent/scripts/detect_harmony_env.py",
                "--project",
                str(project),
                "--probe",
                "--strict",
                env=env,
            )
            self.assertEqual(result.returncode, 2, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data["cli"]["path"], str(executable))
            self.assertIsNone(data["cli"]["version"])
            self.assertFalse(data["cli"]["ready"])
            self.assertIn("code 7", data["cli"]["error"])
            self.assertEqual(data["cli"]["probe"]["output"], "sandbox denied")
            self.assertEqual(data["probes"]["devecocliVersion"], data["cli"]["probe"])

    def test_explicit_studio_and_clt_toolchain_sources(self) -> None:
        for kind, env_key in (("studio", "DEVECO_CLI_STUDIO_PATH"), ("clt", "DEVECO_CLI_CLT_PATH")):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as raw:
                parent = Path(raw)
                project = make_harmony_project(parent)
                env, _ = isolated_detector_env(parent)
                env.pop("DEVECO_HOME")
                if kind == "studio":
                    configured_root = parent / "Custom-DevEco.app"
                    detected_root = configured_root / "Contents"
                else:
                    configured_root = parent / "command-line-tools"
                    detected_root = configured_root
                make_raw_toolchain(detected_root, kind)
                env[env_key] = str(configured_root)
                result = run_script(
                    "skills/harmony-debugger-agent/scripts/detect_harmony_env.py",
                    "--project",
                    str(project),
                    "--strict",
                    env=env,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                data = json.loads(result.stdout)
                self.assertEqual(data["toolchain"]["source"], env_key)
                self.assertEqual(data["toolchain"]["kind"], kind)
                self.assertEqual(data["toolchain"]["root"], str(detected_root.resolve()))
                self.assertTrue(data["toolchain"]["ready"])
                self.assertEqual(data["devecoHome"], str(detected_root.resolve()))

    def test_macos_user_applications_toolchain_is_discovered(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            parent = Path(raw)
            app = parent / "Applications/DevEco-Studio.app"
            detected_root = app / "Contents"
            make_raw_toolchain(detected_root, "studio")
            detector_path = ROOT / "skills/harmony-debugger-agent/scripts/detect_harmony_env.py"
            spec = importlib.util.spec_from_file_location("detect_harmony_env_test", detector_path)
            self.assertIsNotNone(spec)
            self.assertIsNotNone(spec.loader if spec else None)
            assert spec and spec.loader
            detector = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(detector)
            with mock.patch.object(detector.Path, "home", return_value=parent):
                candidates = detector.macos_studio_roots()
            self.assertTrue(
                any(
                    path.resolve() == detected_root.resolve()
                    and kind == "studio"
                    and source == "auto:~/Applications"
                    for path, kind, source in candidates
                )
            )

    def test_memory_delta(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            before = root / "before.csv"
            after = root / "after.csv"
            before.write_text("type,count,shallow_size,retained_size\nPhotoPage,1,100,200\n", encoding="utf-8")
            after.write_text("type,count,shallow_size,retained_size\nPhotoPage,4,400,900\n", encoding="utf-8")
            result = run_script("skills/harmony-memory-leaks/scripts/compare_memory_snapshots.py", str(before), str(after))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PhotoPage", result.stdout)
            self.assertIn("700", result.stdout)

    def test_crash_parser(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            log = Path(raw) / "jscrash.log"
            log.write_text(
                "TypeError: Cannot read property title of undefined\n"
                " at render (/data/app/el1/bundle/entry/src/main/ets/pages/Index.ets:42:9)\n"
                " at framework (@kit.ArkUI:1:1)\n",
                encoding="utf-8",
            )
            result = run_script("skills/arkts-runtime-fix/scripts/parse_crash.py", "--log", str(log))
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data["error_type"].lower(), "typeerror")
            self.assertIn("Index.ets", data["suspected_file"])

    def test_trace_database_summary(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            database = Path(raw) / "trace.db"
            connection = sqlite3.connect(database)
            connection.execute("CREATE TABLE slice(name TEXT, dur INTEGER, pid INTEGER, tid INTEGER)")
            connection.executemany("INSERT INTO slice VALUES(?,?,?,?)", [("Layout", 120, 1, 2), ("Layout", 80, 1, 2), ("Render", 50, 1, 2)])
            connection.commit()
            connection.close()
            result = run_script("skills/harmony-profiler-trace/scripts/analyze_htrace.py", str(database))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Layout", result.stdout)
            self.assertIn("200", result.stdout)

    def test_preview_gallery(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            image = root / "phone__light.png"
            image.write_bytes(b"not-decoded-by-gallery")
            output = root / "gallery/index.html"
            result = run_script(
                "skills/harmony-runtime-preview/scripts/build_preview_gallery.py",
                "--output",
                str(output),
                str(image),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("phone__light.png", output.read_text(encoding="utf-8"))

    def test_project_generator(self) -> None:
        if not Path("/Applications/DevEco-Studio.app/Contents/sdk/default/sdk-pkg.json").exists():
            self.skipTest("DevEco SDK is not installed")
        with tempfile.TemporaryDirectory() as raw:
            result = run_script(
                "skills/deveco-create-project/scripts/create_project.py",
                "--parent",
                raw,
                "--name",
                "Notes",
                "--bundle",
                "com.example.notes",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertTrue(data["verified"])
            profile = Path(data["projectRoot"]) / "build-profile.json5"
            self.assertNotIn("__TARGET_SDK__", profile.read_text(encoding="utf-8"))

    def test_recorded_routing_results(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            results = Path(raw) / "results.json"
            results.write_text(
                json.dumps(
                    {
                        "results": [
                            {
                                "id": "release-submission",
                                "selectedSkills": ["harmony-release-compliance"],
                                "response": "先核对 Profile 目标；常规 .app 流程使用 assembleApp，并以当前 AGC 要求为准。",
                            }
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            result = run_script("scripts/evaluate_routing_results.py", "--allow-partial", str(results))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            results.write_text(
                json.dumps(
                    {
                        "results": [
                            {
                                "id": "release-submission",
                                "selectedSkills": [],
                                "response": "软著必须。",
                            }
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            result = run_script("scripts/evaluate_routing_results.py", "--allow-partial", str(results))
            self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
