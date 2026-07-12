#!/usr/bin/env python3
"""Evaluate recorded agent routing and response results against eval fixtures."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path, help="JSON file containing a results array")
    parser.add_argument("--allow-partial", action="store_true", help="allow a subset of case ids")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    fixtures = json.loads((ROOT / "evals/cases.json").read_text(encoding="utf-8"))
    cases = {case["id"]: case for case in fixtures.get("cases", [])}
    payload = json.loads(args.results.read_text(encoding="utf-8"))
    raw_results = payload.get("results")
    if not isinstance(raw_results, list):
        print("ERROR: results must be a list")
        return 1

    errors: list[str] = []
    seen: set[str] = set()
    for result in raw_results:
        if not isinstance(result, dict):
            errors.append("result entry must be an object")
            continue
        case_id = result.get("id")
        if case_id not in cases:
            errors.append(f"unknown case id: {case_id}")
            continue
        if case_id in seen:
            errors.append(f"duplicate case id: {case_id}")
            continue
        seen.add(case_id)

        selected = result.get("selectedSkills", [])
        response = result.get("response", "")
        if not isinstance(selected, list) or not all(isinstance(value, str) for value in selected):
            errors.append(f"{case_id}: selectedSkills must be a list of strings")
            continue
        if not isinstance(response, str):
            errors.append(f"{case_id}: response must be a string")
            continue

        case = cases[case_id]
        missing_skills = set(case.get("expectedSkills", [])) - set(selected)
        if missing_skills:
            errors.append(f"{case_id}: missing expected skills: {', '.join(sorted(missing_skills))}")

        folded = response.casefold()
        for required in case.get("mustInclude", []):
            if required.casefold() not in folded:
                errors.append(f"{case_id}: response missing required text: {required}")
        for forbidden in case.get("mustNotInclude", []):
            if forbidden.casefold() in folded:
                errors.append(f"{case_id}: response contains forbidden text: {forbidden}")

    if not args.allow_partial:
        missing_cases = set(cases) - seen
        if missing_cases:
            errors.append("missing case results: " + ", ".join(sorted(missing_cases)))

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: {len(seen)} recorded routing results")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
