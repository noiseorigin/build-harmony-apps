#!/usr/bin/env python3
"""Discover a HarmonyOS project and the DevEco-bundled command-line tools."""

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


def first_existing(paths: list[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path.resolve()
    return None


def deveco_roots() -> list[Path]:
    values: list[Path] = []
    for key in ("DEVECO_HOME", "DEVECO_STUDIO_HOME"):
        raw = os.environ.get(key)
        if raw:
            value = Path(raw).expanduser()
            if value.suffix == ".app":
                value = value / "Contents"
            values.append(value)
    if sys.platform == "darwin":
        values.append(Path("/Applications/DevEco-Studio.app/Contents"))
    elif os.name == "nt":
        values.extend(
            Path(item)
            for item in (
                r"C:\Program Files\Huawei\DevEco Studio",
                r"C:\Program Files\DevEco Studio",
            )
        )
    else:
        values.extend((Path.home() / "devecostudio/Contents", Path.home() / "DevEco-Studio/Contents"))
    return values


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
        output = (completed.stdout or completed.stderr).strip()
        return {"exitCode": completed.returncode, "output": output[:8000]}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"exitCode": None, "error": str(exc)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=os.getcwd(), help="Project path or a child path")
    parser.add_argument("--probe", action="store_true", help="Run version and device-list probes")
    parser.add_argument("--strict", action="store_true", help="Fail if project or core DevEco tools are missing")
    args = parser.parse_args()

    root = first_existing(deveco_roots())
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
        sdk = root / "sdk/default"
        hdc = first_existing([sdk / "openharmony/toolchains/hdc", sdk / "openharmony/toolchains/hdc.exe"])
        hvigor = first_existing([root / "tools/hvigor/bin/hvigorw", root / "tools/hvigor/bin/hvigorw.bat"])
        ohpm = first_existing([root / "tools/ohpm/bin/ohpm", root / "tools/ohpm/bin/ohpm.bat"])
        trace_streamer = first_existing(
            [root / "tools/profiler/dic_server/trace_streamer", root / "tools/profiler/dic_server/trace_streamer.exe"]
        )
        java_home = first_existing([root / "jbr/Contents/Home", root / "jbr"])
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

    result: dict[str, Any] = {
        "platform": platform.platform(),
        "projectRoot": str(project) if project else None,
        "bundleName": extract_bundle(project),
        "devecoHome": str(root) if root else None,
        "sdkRoot": str(sdk) if sdk and sdk.exists() else None,
        "devecoSdkHome": str(root / "sdk") if root and (root / "sdk").exists() else None,
        "javaHome": str(java_home) if java_home else None,
        "sdk": metadata.get("data") if metadata else None,
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
        if devecocli:
            probes["devecocliVersion"] = run_probe([str(devecocli), "--version"])
        if trace_streamer:
            probes["traceStreamerVersion"] = run_probe([str(trace_streamer), "-v"])
        if java:
            probes["javaVersion"] = run_probe([str(java), "-version"])
        result["probes"] = probes

    print(json.dumps(result, ensure_ascii=False, indent=2))
    missing = []
    if not project:
        missing.append("projectRoot")
    if not root:
        missing.append("devecoHome")
    if not hdc:
        missing.append("hdc")
    if not hvigor:
        missing.append("hvigorw")
    return 2 if args.strict and missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
