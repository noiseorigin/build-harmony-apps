from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def run_script(relative: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / relative), *args], capture_output=True, text=True, check=False, timeout=60
    )


class ScriptTests(unittest.TestCase):
    def test_detect_environment_and_project(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw) / "Demo"
            child = project / "entry/src"
            child.mkdir(parents=True)
            (project / "build-profile.json5").write_text("{}", encoding="utf-8")
            app_scope = project / "AppScope"
            app_scope.mkdir()
            (app_scope / "app.json5").write_text('{"app":{"bundleName":"com.example.demo"}}', encoding="utf-8")
            result = run_script("skills/harmony-debugger-agent/scripts/detect_harmony_env.py", "--project", str(child))
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data["projectRoot"], str(project.resolve()))
            self.assertEqual(data["bundleName"], "com.example.demo")

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
