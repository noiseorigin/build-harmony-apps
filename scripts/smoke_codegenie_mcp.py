#!/usr/bin/env python3
"""Initialize the pinned DevEco CodeGenie MCP and verify its required tool surface."""

from __future__ import annotations

import json
import queue
import subprocess
import sys
import threading
import time


EXPECTED = {
    "perform_ui_action",
    "build_project",
    "get_app_ui_tree",
    "check_ets_files",
    "check_cpp_files",
    "verify_ui",
    "save_ui_screenshot",
    "get_ui_verification_log",
    "start_app",
    "init_project_path",
}


def message(identifier: int, method: str, params: dict | None = None) -> str:
    value = {"jsonrpc": "2.0", "id": identifier, "method": method}
    if params is not None:
        value["params"] = params
    return json.dumps(value, separators=(",", ":"))


def main() -> int:
    try:
        process = subprocess.Popen(
            ["npx", "-y", "@deveco-codegenie/mcp@1.1.11"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    assert process.stdin is not None and process.stdout is not None and process.stderr is not None
    received: queue.Queue[dict] = queue.Queue()
    stderr_lines: list[str] = []

    def read_stdout() -> None:
        for line in process.stdout:
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                received.put(value)

    def read_stderr() -> None:
        stderr_lines.extend(process.stderr.readlines())

    threading.Thread(target=read_stdout, daemon=True).start()
    threading.Thread(target=read_stderr, daemon=True).start()

    def send(value: str) -> None:
        process.stdin.write(value + "\n")
        process.stdin.flush()

    def wait_for(identifier: int, timeout: float = 30) -> dict | None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                value = received.get(timeout=min(0.5, max(deadline - time.monotonic(), 0.01)))
            except queue.Empty:
                continue
            if value.get("method") == "roots/list" and "id" in value:
                send(json.dumps({"jsonrpc": "2.0", "id": value["id"], "result": {"roots": []}}, separators=(",", ":")))
                continue
            if value.get("id") == identifier:
                return value
        return None

    send(
        message(
            1,
            "initialize",
            {
                "protocolVersion": "2025-03-26",
                "capabilities": {"roots": {"listChanged": False}},
                "clientInfo": {"name": "build-harmony-apps-smoke", "version": "0.1.0"},
            },
        )
    )
    initialize_response = wait_for(1)
    if not initialize_response:
        process.terminate()
        print("".join(stderr_lines)[-4000:], file=sys.stderr)
        print("error: initialize response not received", file=sys.stderr)
        return 2
    send(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}, separators=(",", ":")))
    send(message(2, "tools/list", {}))
    tool_response = wait_for(2)
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
    if not tool_response:
        print("".join(stderr_lines)[-4000:], file=sys.stderr)
        print("error: tools/list response not received", file=sys.stderr)
        return 2
    names = {item.get("name") for item in tool_response.get("result", {}).get("tools", [])}
    missing = sorted(EXPECTED - names)
    result = {
        "server": "@deveco-codegenie/mcp@1.1.11",
        "protocolVersion": initialize_response.get("result", {}).get("protocolVersion"),
        "toolCount": len(names),
        "tools": sorted(item for item in names if item),
        "missing": missing,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
