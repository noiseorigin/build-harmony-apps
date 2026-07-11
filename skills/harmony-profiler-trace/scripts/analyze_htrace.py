#!/usr/bin/env python3
"""Convert DevEco htrace/bytrace to SQLite and summarize duration-bearing tables."""

from __future__ import annotations

import argparse
import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path


SQLITE_MAGIC = b"SQLite format 3\x00"
NAME_COLUMNS = ("name", "state", "type", "event_name", "category", "value")
DURATION_COLUMNS = ("dur", "duration", "wall_duration", "cost", "time")
PRIORITY = ("slice", "thread_state", "sched_slice", "app_startup", "callstack", "perf_sample")


def quote(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def is_sqlite(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            return handle.read(len(SQLITE_MAGIC)) == SQLITE_MAGIC
    except OSError:
        return False


def find_trace_streamer(explicit: str | None) -> Path | None:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit).expanduser())
    env = os.environ.get("TRACE_STREAMER")
    if env:
        candidates.append(Path(env).expanduser())
    if sys.platform == "darwin":
        candidates.append(Path("/Applications/DevEco-Studio.app/Contents/tools/profiler/dic_server/trace_streamer"))
    elif os.name == "nt":
        for root in (r"C:\Program Files\Huawei\DevEco Studio", r"C:\Program Files\DevEco Studio"):
            candidates.append(Path(root) / "tools/profiler/dic_server/trace_streamer.exe")
    found = shutil.which("trace_streamer")
    if found:
        candidates.append(Path(found))
    for path in candidates:
        if path.is_file():
            return path.resolve()
    return None


def convert(source: Path, database: Path, executable: Path) -> None:
    database.parent.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        [str(executable), str(source), "-e", str(database)], capture_output=True, text=True, timeout=300, check=False
    )
    if completed.returncode != 0 or not is_sqlite(database):
        detail = (completed.stderr or completed.stdout).strip()
        raise RuntimeError(f"trace_streamer conversion failed ({completed.returncode}): {detail[:4000]}")


def table_columns(connection: sqlite3.Connection, table: str) -> list[str]:
    return [str(row[1]) for row in connection.execute(f"PRAGMA table_info({quote(table)})")]


def scalar(connection: sqlite3.Connection, query: str) -> int:
    row = connection.execute(query).fetchone()
    return int(row[0]) if row and row[0] is not None else 0


def summarize(database: Path, raw: Path, top: int) -> str:
    connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    try:
        tables = [str(row[0]) for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        if not tables:
            raise RuntimeError("trace database contains no tables")
        ordered = sorted(tables, key=lambda item: (PRIORITY.index(item) if item in PRIORITY else len(PRIORITY), item))
        lines = [
            "# HarmonyOS trace summary",
            "",
            f"- Raw input: `{raw}`",
            f"- SQLite: `{database}`",
            f"- Tables: {len(tables)}",
            "- Durations are reported in the database's raw unit; confirm the trace schema before converting them to time.",
            "",
            "## Schema inventory",
            "",
            "| Table | Rows | Key columns |",
            "| --- | ---: | --- |",
        ]
        duration_tables = []
        for table in ordered:
            columns = table_columns(connection, table)
            count = scalar(connection, f"SELECT COUNT(*) FROM {quote(table)}")
            keys = [item for item in columns if item in NAME_COLUMNS or item in DURATION_COLUMNS or item in ("ts", "pid", "tid", "id")]
            if count or keys:
                lines.append(f"| {table.replace('|', '/')} | {count:,} | {', '.join(keys[:10])} |")
            name_column = next((item for item in NAME_COLUMNS if item in columns), None)
            duration_column = next((item for item in DURATION_COLUMNS if item in columns), None)
            if name_column and duration_column and count:
                duration_tables.append((table, name_column, duration_column))

        lines.extend(("", "## Top duration groups", ""))
        if not duration_tables:
            lines.append("No table with both a recognized name/state and duration column was found. Use the inventory for a version-specific query.")
        for table, name_column, duration_column in duration_tables[:10]:
            query = (
                f"SELECT CAST({quote(name_column)} AS TEXT), COUNT(*), "
                f"SUM(CASE WHEN {quote(duration_column)} > 0 THEN {quote(duration_column)} ELSE 0 END) AS total "
                f"FROM {quote(table)} WHERE {quote(name_column)} IS NOT NULL "
                f"GROUP BY {quote(name_column)} ORDER BY total DESC LIMIT ?"
            )
            try:
                rows = connection.execute(query, (top,)).fetchall()
            except sqlite3.DatabaseError as exc:
                lines.append(f"### {table}\n\nQuery failed: `{exc}`\n")
                continue
            lines.extend((f"### {table}", "", f"Grouped by `{name_column}`, summed `{duration_column}` (raw units).", "", "| Name/state | Rows | Total duration |", "| --- | ---: | ---: |"))
            for name, count, total in rows:
                label = str(name).replace("|", "/").replace("\n", " ")[:180]
                lines.append(f"| {label} | {int(count):,} | {float(total or 0):,.0f} |")
            lines.append("")
        lines.extend(
            (
                "## Interpretation gate",
                "",
                "Map a candidate to the target process/thread and app-owned code before calling it a hotspot. "
                "This generic summary is schema discovery and prioritization, not automatic root-cause proof.",
            )
        )
        return "\n".join(lines) + "\n"
    finally:
        connection.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace")
    parser.add_argument("--db", help="Output SQLite path when conversion is needed")
    parser.add_argument("--trace-streamer")
    parser.add_argument("--out")
    parser.add_argument("--top", type=int, default=12)
    args = parser.parse_args()
    source = Path(args.trace).expanduser().resolve()
    if not source.is_file():
        parser.error(f"trace not found: {source}")
    database = source
    if not is_sqlite(source):
        executable = find_trace_streamer(args.trace_streamer)
        if not executable:
            parser.error("trace_streamer not found; pass --trace-streamer or install DevEco Studio")
        database = Path(args.db).expanduser().resolve() if args.db else source.with_suffix(source.suffix + ".sqlite")
        convert(source, database, executable)
    try:
        report = summarize(database, source, max(args.top, 1))
    except (sqlite3.DatabaseError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.out:
        output = Path(args.out).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8")
        print(output)
    else:
        print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
