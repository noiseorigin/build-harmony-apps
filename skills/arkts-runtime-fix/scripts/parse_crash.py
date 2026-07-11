#!/usr/bin/env python3
"""Extract stable crash anchors from ArkTS/jscrash/faultlogger/hilog text."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ERROR_RE = re.compile(
    r"\b(TypeError|ReferenceError|RangeError|SyntaxError|BusinessError|ParameterError|AssertionError|Error)\b\s*[:\-]?\s*(.*)",
    re.IGNORECASE,
)
FRAME_RE = re.compile(r"(?:\bat\s+.*|[^\s]+\.(?:ets|ts|js|cpp|cc|c|h)(?::\d+){0,2}.*)", re.IGNORECASE)
FILE_RE = re.compile(r"((?:[A-Za-z]:)?[^\s()]+\.(?:ets|ts|js|cpp|cc|c|h)(?::\d+){0,2})", re.IGNORECASE)


def parse(text: str, bundle: str) -> dict[str, object]:
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    error_type = ""
    error_message = ""
    error_index = 0
    for index, line in enumerate(lines):
        match = ERROR_RE.search(line)
        if match:
            error_type = match.group(1)
            error_message = match.group(2).strip() or line.strip()
            error_index = index
            break
    frames = []
    for line in lines[error_index : error_index + 160]:
        if FRAME_RE.search(line):
            cleaned = line.strip()
            if cleaned not in frames:
                frames.append(cleaned)
        if len(frames) >= 12:
            break
    suspected = ""
    candidates: list[tuple[int, str]] = []
    for position, frame in enumerate(frames):
        match = FILE_RE.search(frame)
        if not match:
            continue
        file_name = match.group(1)
        lowered = frame.lower()
        score = 0
        if bundle and bundle.lower() in lowered:
            score += 4
        if "/src/main/" in lowered or "\\src\\main\\" in lowered:
            score += 3
        if any(token in lowered for token in ("/system/", "@ohos.", "@kit.", "node_modules")):
            score -= 3
        score -= position
        candidates.append((score, file_name))
    if candidates:
        suspected = max(candidates, key=lambda item: item[0])[1]
    detected = bool(error_type or frames)
    next_action = (
        f"Inspect {suspected} and reproduce the same flow after a minimal fix."
        if suspected
        else "Collect a matching faultlogger/jscrash artifact or a narrower hilog window."
    )
    return {
        "status": "detected" if detected else "no_crash_signature",
        "error_type": error_type,
        "error_message": error_message,
        "suspected_file": suspected,
        "top_stack": frames[:8],
        "keywords": [item for item in (error_type, bundle) if item],
        "next_action": next_action,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", required=True, help="Log path or - for stdin")
    parser.add_argument("--bundle", default="")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    args = parser.parse_args()
    try:
        text = sys.stdin.read() if args.log == "-" else Path(args.log).expanduser().read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        print(json.dumps({"status": "parse_failed", "error": str(exc)}))
        return 2
    report = parse(text, args.bundle)
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("# ArkTS crash anchor\n")
        for key in ("status", "error_type", "error_message", "suspected_file", "next_action"):
            print(f"- {key}: {report[key]}")
        print("\n## Top stack\n")
        for frame in report["top_stack"]:
            print(f"- `{str(frame).replace('`', '')}`")
    return 0 if report["status"] == "detected" else 1


if __name__ == "__main__":
    raise SystemExit(main())
