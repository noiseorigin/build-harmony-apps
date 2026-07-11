#!/usr/bin/env python3
"""Compare normalized or common CSV/JSON memory snapshot exports."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


ALIASES = {
    "type": {"type", "typename", "class", "classname", "objecttype", "name"},
    "count": {"count", "instances", "instancecount", "objects", "objectcount"},
    "shallow_size": {"shallowsize", "selfsize", "size", "bytes"},
    "retained_size": {"retainedsize", "retainedbytes", "retained", "totalsize"},
}


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def number(value: Any) -> float:
    if value in (None, ""):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "")
    match = re.match(r"^-?\d+(?:\.\d+)?", text)
    if not match:
        return 0.0
    result = float(match.group(0))
    lowered = text.lower()
    if "gib" in lowered or re.search(r"\bgb\b", lowered):
        result *= 1024**3
    elif "mib" in lowered or re.search(r"\bmb\b", lowered):
        result *= 1024**2
    elif "kib" in lowered or re.search(r"\bkb\b", lowered):
        result *= 1024
    return result


def rows(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            for key in ("rows", "items", "data", "objects"):
                if isinstance(data.get(key), list):
                    data = data[key]
                    break
        if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
            raise ValueError(f"JSON must contain an array of object rows: {path}")
        return data
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def canonicalize(path: Path) -> dict[str, dict[str, float]]:
    data = rows(path)
    if not data:
        raise ValueError(f"snapshot has no rows: {path}")
    header_map: dict[str, str] = {}
    for original in data[0].keys():
        normalized = norm(str(original))
        for canonical, aliases in ALIASES.items():
            if normalized in aliases and canonical not in header_map:
                header_map[canonical] = str(original)
    if "type" not in header_map:
        raise ValueError(f"snapshot needs a type/class/name column: {path}")
    result: dict[str, dict[str, float]] = defaultdict(lambda: {"count": 0, "shallow_size": 0, "retained_size": 0})
    for item in data:
        type_name = str(item.get(header_map["type"], "")).strip()
        if not type_name:
            continue
        for field in ("count", "shallow_size", "retained_size"):
            if field in header_map:
                result[type_name][field] += number(item.get(header_map[field]))
    return dict(result)


def fmt(value: float) -> str:
    return f"{int(value):,}" if value.is_integer() else f"{value:,.2f}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("before")
    parser.add_argument("after")
    parser.add_argument("--out")
    parser.add_argument("--top", type=int, default=25)
    args = parser.parse_args()
    before_path = Path(args.before).expanduser().resolve()
    after_path = Path(args.after).expanduser().resolve()
    before = canonicalize(before_path)
    after = canonicalize(after_path)
    types = sorted(set(before) | set(after))
    deltas = []
    for name in types:
        old = before.get(name, {"count": 0, "shallow_size": 0, "retained_size": 0})
        new = after.get(name, {"count": 0, "shallow_size": 0, "retained_size": 0})
        delta = {field: new[field] - old[field] for field in ("count", "shallow_size", "retained_size")}
        deltas.append((name, old, new, delta))
    deltas.sort(key=lambda item: (item[3]["retained_size"], item[3]["shallow_size"], item[3]["count"]), reverse=True)
    lines = [
        "# Memory snapshot delta",
        "",
        f"- Before: `{before_path}`",
        f"- After: `{after_path}`",
        "- Positive values mean growth. Sizes are bytes after unit normalization.",
        "",
        "| Type | Count before | Count after | Δ count | Δ shallow | Δ retained |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, old, new, delta in deltas[: max(args.top, 1)]:
        lines.append(
            f"| {name.replace('|', '\\|')} | {fmt(old['count'])} | {fmt(new['count'])} | "
            f"{fmt(delta['count'])} | {fmt(delta['shallow_size'])} | {fmt(delta['retained_size'])} |"
        )
    lines.extend(("", "This delta is not leak proof without intended-lifetime and ownership/repeatability evidence."))
    text = "\n".join(lines) + "\n"
    if args.out:
        output = Path(args.out).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
        print(output)
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
