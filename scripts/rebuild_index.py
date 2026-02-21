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

IMAGE_EXTENSIONS = ("png", "jpg", "jpeg", "webp")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--projects-dir", required=True)
    parser.add_argument("--readme-template", required=True)
    parser.add_argument("--readme-output", required=True)
    parser.add_argument("--activity-json", default="assets/stats/account_activity.json")
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


def parse_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def format_int(value: Any) -> str:
    return f"{parse_int(value):,}"


def detect_local_screenshot(stem: str, assets_dir: Path, repo_root: Path) -> str:
    for ext in IMAGE_EXTENSIONS:
        candidate = assets_dir / f"{stem}.{ext}"
        if candidate.exists():
            try:
                return candidate.relative_to(repo_root).as_posix()
            except ValueError:
                return candidate.as_posix()
    return ""


def load_projects(projects_dir: Path, assets_dir: Path, repo_root: Path) -> list[dict[str, Any]]:
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

        screenshot_url = raw.get("screenshot_url")
        if isinstance(screenshot_url, str) and screenshot_url.strip():
            raw["_card_screenshot"] = screenshot_url.strip()
        else:
            raw["_card_screenshot"] = detect_local_screenshot(path.stem, assets_dir, repo_root)

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
    screenshot = str(project.get("_card_screenshot", ""))
    lines = [
        f"### {title}",
        "",
        one_liner,
        "",
    ]

    if screenshot:
        lines.append(f"![{title} screenshot]({screenshot})")
        lines.append("")

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


def load_activity_stats(activity_json_path: Path) -> dict[str, Any]:
    if not activity_json_path.exists():
        return {}
    try:
        raw = json.loads(activity_json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(raw, dict):
        return {}
    return raw


def build_bar(value: int, max_value: int, width: int = 24) -> str:
    if value <= 0 or max_value <= 0:
        return ""
    units = max(1, int(round((value / max_value) * width)))
    return "#" * units


def render_activity_stats(stats: dict[str, Any], chart_path: str = "") -> str:
    if not stats:
        return "_No account activity stats file found at `assets/stats/account_activity.json`._\n"

    range_start = str(stats.get("range_start", "n/a"))
    range_end = str(stats.get("range_end", "n/a"))
    total_contributions = parse_int(stats.get("total_contributions"))
    commit_contributions = parse_int(stats.get("commit_contributions"))
    pr_contributions = parse_int(stats.get("pull_request_contributions"))
    issue_contributions = parse_int(stats.get("issue_contributions"))
    review_contributions = parse_int(stats.get("review_contributions"))
    active_days = parse_int(stats.get("active_days"))
    longest_streak_days = parse_int(stats.get("longest_streak_days"))
    last_30 = parse_int(stats.get("contributions_last_30_days"))
    estimated_source_loc = parse_int(stats.get("estimated_source_loc"))
    loc_scope_note = str(stats.get("loc_scope_note", "")).strip()
    nbp_note = str(stats.get("nbp_note", "")).strip()

    lines = [
        f"- Activity window: {range_start} to {range_end}",
        f"- Total contributions: {format_int(total_contributions)}",
        f"- Commit contributions: {format_int(commit_contributions)}",
        f"- Pull requests: {format_int(pr_contributions)}",
        f"- Issues: {format_int(issue_contributions)}",
        f"- Reviews: {format_int(review_contributions)}",
        f"- Contributions (last 30 days): {format_int(last_30)}",
        f"- Active days: {format_int(active_days)}",
        f"- Longest streak: {format_int(longest_streak_days)} days",
        f"- Estimated source LOC: {format_int(estimated_source_loc)}",
    ]

    if loc_scope_note:
        lines.append(f"- LOC scope: {loc_scope_note}")
    if nbp_note:
        lines.append(f"- NBP note: {nbp_note}")

    if chart_path:
        lines.append("")
        lines.append(f"![Account Activity Chart]({chart_path})")

    monthly_raw = stats.get("monthly_contributions", [])
    monthly: list[tuple[str, int]] = []
    if isinstance(monthly_raw, list):
        for item in monthly_raw:
            if not isinstance(item, dict):
                continue
            month = str(item.get("month", "")).strip()
            if not month:
                continue
            count = parse_int(item.get("count"))
            monthly.append((month, count))

    if monthly:
        recent = monthly[-8:]
        max_count = max(count for _, count in recent)
        lines.append("")
        lines.append("```text")
        lines.append("Monthly Contributions")
        for month, count in recent:
            label = month[2:] if len(month) >= 7 else month
            bar = build_bar(count, max_count)
            lines.append(f"{label:>5} | {bar:<24} {count:>5}")
        lines.append("```")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()

    projects_dir = Path(args.projects_dir)
    template_path = Path(args.readme_template)
    output_path = Path(args.readme_output)
    repo_root = output_path.parent
    assets_dir = repo_root / "assets" / "screenshots"
    stats_chart = repo_root / "assets" / "stats" / "account_activity_chart.png"
    activity_json_path = Path(args.activity_json)
    if not activity_json_path.is_absolute():
        activity_json_path = repo_root / activity_json_path

    projects = load_projects(projects_dir, assets_dir, repo_root)
    cards = "\n".join(render_card(p) for p in projects)
    activity_stats = load_activity_stats(activity_json_path)
    stats_chart_rel = ""
    if stats_chart.exists():
        try:
            stats_chart_rel = stats_chart.relative_to(repo_root).as_posix()
        except ValueError:
            stats_chart_rel = stats_chart.as_posix()

    stats_block = render_activity_stats(activity_stats, chart_path=stats_chart_rel)

    if not cards:
        cards = "_No projects published yet._\n"

    template = template_path.read_text(encoding="utf-8")
    readme = template.replace("{{SHOWCASE_STATS}}", stats_block)
    readme = readme.replace("{{PROJECT_CARDS}}", cards)
    output_path.write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    main()
