#!/usr/bin/env python3
"""Rebuild README index from projects/*.json files."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

EXCLUDED_PROJECT_IDS = {
    "ai-web-design",
    "als-diag",
    "cc-vps",
    "claroty2",
    "clartity1",
    "kestra_dev",
    "moltbot-workspace",
    "rxion-biz",
    "rxionv2",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--projects-dir", required=True)
    parser.add_argument("--readme-template", required=True)
    parser.add_argument("--readme-output", required=True)
    return parser.parse_args()


def parse_date(value: str) -> dt.date:
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        return dt.date(1970, 1, 1)


def parse_datetime(value: str) -> dt.datetime:
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return dt.datetime(1970, 1, 1, tzinfo=dt.UTC)


def load_projects(projects_dir: Path) -> list[dict[str, Any]]:
    projects: list[dict[str, Any]] = []
    for path in sorted(projects_dir.glob("*.json")):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not isinstance(raw, dict):
            continue
        raw["_filename"] = path.name
        raw["_stem"] = path.stem
        project_id = str(raw.get("project_id", path.stem))
        if project_id in EXCLUDED_PROJECT_IDS or path.stem in EXCLUDED_PROJECT_IDS:
            continue
        projects.append(raw)

    projects.sort(
        key=lambda p: (
            parse_date(str(p.get("updated_at", ""))),
            parse_datetime(str(p.get("generated_at", ""))),
        ),
        reverse=True,
    )
    return projects


def render_card(project: dict[str, Any]) -> str:
    title = str(project.get("title", project.get("_stem", "Untitled")))
    one_liner = str(project.get("one_liner", ""))
    status = str(project.get("status", "active"))
    updated_at = str(project.get("updated_at", "unknown"))
    impact = str(project.get("impact", ""))
    stack = project.get("stack", [])
    stack_text = ", ".join(stack) if isinstance(stack, list) else str(stack)
    project_page = f"projects/{project.get('_stem', '')}.md"
    lines = [
        f"### {title}",
        "",
        one_liner,
        "",
    ]

    lines.extend([
        f"- Status: {status}",
        f"- Updated: {updated_at}",
        f"- Stack: {stack_text}",
    ])

    if impact:
        lines.append(f"- Impact: {impact}")

    demo_url = project.get("demo_url")
    article_url = project.get("article_url")
    visibility_note = project.get("visibility_note")

    if isinstance(demo_url, str) and demo_url.strip():
        lines.append(f"- Demo: {demo_url}")

    if isinstance(article_url, str) and article_url.strip():
        lines.append(f"- Write-up: {article_url}")

    lines.append(f"- Details: {project_page}")

    if isinstance(visibility_note, str) and visibility_note.strip():
        lines.append(f"- Visibility: {visibility_note}")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()

    projects_dir = Path(args.projects_dir)
    template_path = Path(args.readme_template)
    output_path = Path(args.readme_output)

    projects = load_projects(projects_dir)
    cards = "\n".join(render_card(p) for p in projects)

    if not cards:
        cards = "_No projects published yet._\n"

    template = template_path.read_text(encoding="utf-8")
    readme = template.replace("{{PROJECT_CARDS}}", cards)
    output_path.write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    main()
