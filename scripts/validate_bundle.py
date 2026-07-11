#!/usr/bin/env python3
"""Validate Build Harmony Apps content beyond the generic plugin schema."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"


def main() -> int:
    errors: list[str] = []
    manifest = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    if manifest.get("name") != ROOT.name:
        errors.append("plugin name does not match directory")
    mcp = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))
    mcp_text = json.dumps(mcp)
    if "@deveco-codegenie/mcp@1.1.11" not in mcp_text or "@latest" in mcp_text:
        errors.append("CodeGenie MCP must be pinned to 1.1.11")

    eval_data = json.loads((ROOT / "evals/cases.json").read_text(encoding="utf-8"))
    covered = {name for case in eval_data.get("cases", []) for name in case.get("expectedSkills", [])}
    skill_names = set()
    for directory in sorted(path for path in SKILLS.iterdir() if path.is_dir()):
        skill_file = directory / "SKILL.md"
        agent_file = directory / "agents/openai.yaml"
        if not skill_file.is_file():
            errors.append(f"missing SKILL.md: {directory.name}")
            continue
        text = skill_file.read_text(encoding="utf-8")
        frontmatter = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        if not frontmatter:
            errors.append(f"invalid frontmatter: {directory.name}")
            continue
        name_match = re.search(r"^name:\s*(.+)$", frontmatter.group(1), re.MULTILINE)
        description_match = re.search(r"^description:\s*(.+)$", frontmatter.group(1), re.MULTILINE)
        name = name_match.group(1).strip() if name_match else ""
        skill_names.add(name)
        if name != directory.name:
            errors.append(f"name mismatch: {directory.name} -> {name}")
        if not description_match or len(description_match.group(1).strip()) < 60:
            errors.append(f"description too weak: {directory.name}")
        if len(text.splitlines()) > 500:
            errors.append(f"SKILL.md exceeds 500 lines: {directory.name}")
        if "[TODO" in text or "TODO:" in text:
            errors.append(f"placeholder remains: {directory.name}")
        if not agent_file.is_file():
            errors.append(f"missing agents/openai.yaml: {directory.name}")
        else:
            agent = agent_file.read_text(encoding="utf-8")
            if f"${directory.name}" not in agent:
                errors.append(f"default prompt does not name skill: {directory.name}")
    for markdown in ROOT.rglob("*.md"):
        text = markdown.read_text(encoding="utf-8")
        for path_text in re.findall(r"`((?:(?:\.\.?/)+|(?:references|scripts|assets)/)[^`\s]+\.(?:md|py|json))`", text):
            resolved = (markdown.parent / path_text).resolve()
            if not resolved.exists():
                errors.append(f"broken local resource in {markdown.relative_to(ROOT)}: {path_text}")

    missing_evals = skill_names - covered
    if missing_evals:
        errors.append("skills without routing eval: " + ", ".join(sorted(missing_evals)))
    if "2a9a5193c122798a451520cf6a4a5a0553e62f93" not in (ROOT / "upstreams.json").read_text(encoding="utf-8"):
        errors.append("fixed CodeGenie upstream commit missing")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: {len(skill_names)} skills, {len(eval_data.get('cases', []))} routing evals, pinned MCP")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
