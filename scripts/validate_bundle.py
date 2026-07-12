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
    if manifest.get("name") not in {ROOT.name, ROOT.parent.name}:
        errors.append("plugin name does not match directory")
    claude_manifest_path = ROOT / ".claude-plugin/plugin.json"
    if not claude_manifest_path.is_file():
        errors.append("missing .claude-plugin/plugin.json (dual-native packaging)")
    else:
        claude_manifest = json.loads(claude_manifest_path.read_text(encoding="utf-8"))
        if claude_manifest.get("name") != manifest.get("name"):
            errors.append("plugin.json name differs between codex and claude manifests")
        codex_base_version = str(manifest.get("version", "")).split("+", 1)[0]
        if claude_manifest.get("version") != codex_base_version:
            errors.append("plugin.json base version differs between codex and claude manifests")
    claude_marketplace_path = ROOT / ".claude-plugin/marketplace.json"
    if not claude_marketplace_path.is_file():
        errors.append("missing .claude-plugin/marketplace.json")
    else:
        claude_marketplace = json.loads(claude_marketplace_path.read_text(encoding="utf-8"))
        entries = claude_marketplace.get("plugins", [])
        if not any(entry.get("name") == manifest.get("name") for entry in entries if isinstance(entry, dict)):
            errors.append("Claude marketplace does not list this plugin")
    mcp = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))
    mcp_text = json.dumps(mcp)
    if "@deveco-codegenie/mcp@1.1.11" not in mcp_text or "@latest" in mcp_text:
        errors.append("CodeGenie MCP must be pinned to 1.1.11")

    eval_data = json.loads((ROOT / "evals/cases.json").read_text(encoding="utf-8"))
    covered = {name for case in eval_data.get("cases", []) for name in case.get("expectedSkills", [])}
    case_ids: set[str] = set()
    for case in eval_data.get("cases", []):
        case_id = case.get("id", "<no id>")
        if case_id in case_ids:
            errors.append(f"duplicate eval case id: {case_id}")
        case_ids.add(case_id)
        for skill in case.get("expectedSkills", []):
            if not (SKILLS / skill / "SKILL.md").is_file():
                errors.append(f"eval {case_id} expects unknown skill: {skill}")
        for field in ("mustInclude", "mustNotInclude"):
            value = case.get(field)
            if value is not None and (not isinstance(value, list) or not all(isinstance(v, str) for v in value)):
                errors.append(f"eval {case_id} field {field} must be a list of strings")
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
    print(f"OK: {len(skill_names)} skills, {len(eval_data.get('cases', []))} routing fixtures, pinned MCP")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
