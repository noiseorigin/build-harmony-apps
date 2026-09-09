#!/usr/bin/env python3
"""Discover a HarmonyOS project and its official or raw DevEco toolchain."""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


MIN_DEVECO_CLI_VERSION = (1, 3, 0)
MIN_DEVECO_CLI_VERSION_TEXT = ".".join(str(part) for part in MIN_DEVECO_CLI_VERSION)
SUPPORTED_DEVECO_CLI_MAJOR = MIN_DEVECO_CLI_VERSION[0]


def first_existing(paths: list[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path.resolve()
    return None


def studio_contents(path: Path) -> Path:
    value = path.expanduser()
    if value.suffix.lower() == ".app":
        value /= "Contents"
    return value


def macos_studio_roots() -> list[tuple[Path, str, str]]:
    values: list[tuple[Path, str, str]] = []
    for directory, source in (
        (Path.home() / "Applications", "auto:~/Applications"),
        (Path("/Applications"), "auto:/Applications"),
    ):
        try:
            apps = sorted(
                (
                    item
                    for item in directory.iterdir()
                    if item.is_dir() and item.suffix.lower() == ".app" and "deveco" in item.name.lower()
                ),
                key=lambda item: item.name.lower(),
            )
        except OSError:
            continue
        values.extend((studio_contents(app), "studio", source) for app in apps)
    return values


def toolchain_candidates() -> list[tuple[Path, str, str]]:
    values: list[tuple[Path, str, str]] = []
    for key, kind in (
        ("DEVECO_CLI_STUDIO_PATH", "studio"),
        ("DEVECO_CLI_CLT_PATH", "clt"),
        ("DEVECO_HOME", "studio"),
        ("DEVECO_STUDIO_HOME", "studio"),
    ):
        raw = os.environ.get(key)
        if raw:
            value = Path(raw).expanduser()
            values.append((studio_contents(value) if kind == "studio" else value, kind, key))
    if sys.platform == "darwin":
        values.extend(macos_studio_roots())
    elif os.name == "nt":
        values.extend(
            (Path(item), "studio", "auto:Program Files")
            for item in (
                r"C:\Program Files\Huawei\DevEco Studio",
                r"C:\Program Files\DevEco Studio",
            )
        )
    return values


def find_toolchain() -> tuple[Path | None, str | None, str | None]:
    for path, kind, source in toolchain_candidates():
        if path.exists():
            return path.resolve(), kind, source
    return None, None, None


def find_project(start: Path) -> Path | None:
    current = start.expanduser().resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / "build-profile.json5").exists():
            return candidate
    return None


def read_json(path: Path | None) -> dict[str, Any] | None:
    if not path or not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def extract_bundle(project: Path | None) -> str | None:
    if not project:
        return None
    path = project / "AppScope/app.json5"
    if not path.exists():
        return None
    match = re.search(r'["\']bundleName["\']\s*:\s*["\']([^"\']+)', path.read_text(encoding="utf-8"))
    return match.group(1) if match else None


def run_probe(command: list[str], timeout: int = 8) -> dict[str, Any]:
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
        output = "\n".join(part.strip() for part in (completed.stdout, completed.stderr) if part.strip())
        return {"exitCode": completed.returncode, "output": output[:8000]}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"exitCode": None, "error": str(exc)}


def parse_version(output: str) -> tuple[str | None, tuple[int, int, int] | None]:
    match = re.search(r"(?<![\d.])v?(\d+)\.(\d+)\.(\d+)(?![\d.])", output, re.IGNORECASE)
    if not match:
        return None, None
    parts = tuple(int(part) for part in match.groups())
    return ".".join(str(part) for part in parts), parts


def inspect_devecocli(path: Path | None) -> tuple[dict[str, Any], dict[str, Any] | None]:
    if not path:
        return (
            {
                "path": None,
                "version": None,
                "minimumVersion": MIN_DEVECO_CLI_VERSION_TEXT,
                "supportedMajor": SUPPORTED_DEVECO_CLI_MAJOR,
                "ready": False,
                "error": "devecocli not found on PATH",
                "probe": None,
            },
            None,
        )

    probe = run_probe([str(path), "--version"])
    output = str(probe.get("output", ""))
    version, version_parts = parse_version(output)
    error: str | None = None
    if probe.get("exitCode") is None:
        error = f"devecocli version probe failed: {probe.get('error', 'unknown error')}"
    elif probe["exitCode"] != 0:
        error = f"devecocli version probe exited with code {probe['exitCode']}"
    elif version_parts is None:
        error = "devecocli version probe returned no semantic version"
    elif version_parts < MIN_DEVECO_CLI_VERSION:
        error = f"devecocli {version} is older than required {MIN_DEVECO_CLI_VERSION_TEXT}"
    elif version_parts[0] != SUPPORTED_DEVECO_CLI_MAJOR:
        error = f"devecocli {version} has unsupported major version {version_parts[0]}"

    return (
        {
            "path": str(path),
            "version": version,
            "minimumVersion": MIN_DEVECO_CLI_VERSION_TEXT,
            "supportedMajor": SUPPORTED_DEVECO_CLI_MAJOR,
            "ready": error is None,
            "error": error,
            "probe": probe,
        },
        probe,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=os.getcwd(), help="Project path or a child path")
    parser.add_argument("--probe", action="store_true", help="Run version and device-list probes")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail unless a project and either compatible devecocli or the raw DevEco toolchain are available",
    )
    args = parser.parse_args()

    root, toolchain_kind, toolchain_source = find_toolchain()
    project = find_project(Path(args.project))
    sdk = None
    hdc = None
    hvigor = None
    ohpm = None
    trace_streamer = None
    java_home = None
    java = None
    metadata = None
    if root:
        sdk_home = root / "sdk"
        sdk = sdk_home / "default"
        hdc = first_existing([sdk / "openharmony/toolchains/hdc", sdk / "openharmony/toolchains/hdc.exe"])
        tool_prefix = root / "tools" if toolchain_kind == "studio" else root
        hvigor = first_existing(
            [
                tool_prefix / "hvigor/bin/hvigorw",
                tool_prefix / "hvigor/bin/hvigorw.bat",
                tool_prefix / "hvigor/bin/hvigorw.js",
            ]
        )
        ohpm = first_existing(
            [
                tool_prefix / "ohpm/bin/ohpm",
                tool_prefix / "ohpm/bin/ohpm.bat",
                tool_prefix / "ohpm/bin/pm-cli.js",
            ]
        )
        if toolchain_kind == "studio":
            trace_streamer = first_existing(
                [root / "tools/profiler/dic_server/trace_streamer", root / "tools/profiler/dic_server/trace_streamer.exe"]
            )
        java_home = first_existing([root / "jbr/Contents/Home", root / "jbr"])
        if not java_home and os.environ.get("JAVA_HOME"):
            java_home = first_existing([Path(os.environ["JAVA_HOME"]).expanduser()])
        if java_home:
            java = first_existing([java_home / "bin/java", java_home / "bin/java.exe"])
        metadata = read_json(sdk / "sdk-pkg.json")

    if not hdc:
        found = shutil.which("hdc")
        hdc = Path(found) if found else None
    if not hvigor:
        found = shutil.which("hvigorw")
        hvigor = Path(found) if found else None
    found_cli = shutil.which("devecocli")
    devecocli = Path(found_cli) if found_cli else None
    cli, cli_probe = inspect_devecocli(devecocli)
    raw_toolchain_ready = bool(root and hdc and hvigor)
    if not toolchain_source and raw_toolchain_ready:
        toolchain_source = "PATH"

    result: dict[str, Any] = {
        "platform": platform.platform(),
        "projectRoot": str(project) if project else None,
        "bundleName": extract_bundle(project),
        "devecoHome": str(root) if root else None,
        "sdkRoot": str(sdk) if sdk and sdk.exists() else None,
        "devecoSdkHome": str(root / "sdk") if root and (root / "sdk").exists() else None,
        "javaHome": str(java_home) if java_home else None,
        "sdk": metadata.get("data") if metadata else None,
        "cli": cli,
        "toolchain": {
            "source": toolchain_source,
            "kind": toolchain_kind,
            "root": str(root) if root else None,
            "ready": raw_toolchain_ready,
        },
        "tools": {
            "hdc": str(hdc) if hdc else None,
            "hvigorw": str(hvigor) if hvigor else None,
            "ohpm": str(ohpm) if ohpm else None,
            "traceStreamer": str(trace_streamer) if trace_streamer else None,
            "java": str(java) if java else None,
            "devecocli": str(devecocli) if devecocli else None,
        },
    }
    if args.probe:
        probes: dict[str, Any] = {}
        if hdc:
            probes["hdcVersion"] = run_probe([str(hdc), "version"])
            probes["targets"] = run_probe([str(hdc), "list", "targets", "-v"])
        if hvigor:
            probes["hvigorVersion"] = run_probe([str(hvigor), "--version"])
        if cli_probe:
            probes["devecocliVersion"] = cli_probe
        if trace_streamer:
            probes["traceStreamerVersion"] = run_probe([str(trace_streamer), "-v"])
        if java:
            probes["javaVersion"] = run_probe([str(java), "-version"])
        result["probes"] = probes

    print(json.dumps(result, ensure_ascii=False, indent=2))
    strict_ready = bool(project and (cli["ready"] or raw_toolchain_ready))
    return 2 if args.strict and not strict_ready else 0


if __name__ == "__main__":
    raise SystemExit(main())
