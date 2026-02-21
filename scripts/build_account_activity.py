#!/usr/bin/env python3
"""Build full-account GitHub activity stats and chart for showcase."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt

SEGMENT_DAYS = 364  # GitHub GraphQL contributionsCollection max span is <= 1 year.

TRACKED_REPO_PATHS = [
    "als-clarity",
    "altitude-nutrition",
    "browser-tui",
    "commonsensehealth",
    "crosspoint",
    "gmail_ai_org",
    "google-ads",
    "ICA",
    "logos",
    "mnemonic",
    "openclaw-workspace",
    "3js",
    "polymarket",
    "rxionv3",
    "sai-canvas",
    "sai",
    "saibot",
    "zipslim",
    "aifunnel-web",
    "genr8ive",
]

SOURCE_EXTENSIONS = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".rs",
    ".go",
    ".sh",
    ".zsh",
    ".html",
    ".css",
    ".scss",
}

EXCLUDED_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "out",
    ".next",
    "coverage",
    "vendor",
    "google-cloud-sdk",
    "ios",
    "android",
    ".wrangler",
    ".expo",
    "target",
    ".venv",
    "venv",
    "env",
    "site-packages",
}

USER_QUERY = """
query($login:String!){
  user(login:$login){
    login
    createdAt
  }
}
"""

CONTRIB_QUERY = """
query($login:String!, $from:DateTime!, $to:DateTime!){
  user(login:$login){
    contributionsCollection(from:$from, to:$to){
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      contributionCalendar{
        totalContributions
        weeks{
          contributionDays{
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", default="btcjon")
    parser.add_argument("--projects-root", default=str(Path.home() / "Dropbox/Projects"))
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-chart", required=True)
    parser.add_argument("--nbp-note", default="")
    return parser.parse_args()


def run_gh_graphql(query: str, variables: dict[str, str]) -> dict[str, Any]:
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        cmd.extend(["-f", f"{key}={value}"])

    proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "gh api graphql failed")
    return json.loads(proc.stdout)


def iter_segments(start_date: dt.date, end_date: dt.date) -> list[tuple[dt.date, dt.date]]:
    segments: list[tuple[dt.date, dt.date]] = []
    cursor = start_date
    while cursor <= end_date:
        seg_end = min(cursor + dt.timedelta(days=SEGMENT_DAYS), end_date)
        segments.append((cursor, seg_end))
        cursor = seg_end + dt.timedelta(days=1)
    return segments


def build_monthly_counts(daily_counts: dict[dt.date, int]) -> list[dict[str, int | str]]:
    monthly: dict[str, int] = defaultdict(int)
    for day, count in daily_counts.items():
        monthly[day.strftime("%Y-%m")] += count

    return [{"month": month, "count": monthly[month]} for month in sorted(monthly)]


def calculate_streaks(daily_counts: dict[dt.date, int]) -> tuple[int, int]:
    if not daily_counts:
        return 0, 0

    days = sorted(daily_counts)
    longest = 0
    current = 0
    active_days = 0
    prev: dt.date | None = None
    for day in days:
        count = daily_counts[day]
        if count > 0:
            active_days += 1
            if prev is not None and (day - prev).days == 1:
                current += 1
            else:
                current = 1
            longest = max(longest, current)
        else:
            current = 0
        prev = day
    return active_days, longest


def count_loc(projects_root: Path) -> int:
    total = 0
    for rel in TRACKED_REPO_PATHS:
        repo = projects_root / rel
        if not repo.exists():
            continue

        for root, dirs, files in os.walk(repo):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            for name in files:
                path = Path(root) / name
                if path.suffix.lower() not in SOURCE_EXTENSIONS:
                    continue
                try:
                    with path.open("rb") as f:
                        total += sum(chunk.count(b"\n") for chunk in iter(lambda: f.read(1 << 20), b""))
                except (OSError, UnicodeDecodeError):
                    continue
    return total


def render_chart(
    monthly: list[dict[str, int | str]],
    out_chart: Path,
    total: int,
    commits: int,
    active_days: int,
) -> None:
    labels = [str(item["month"]) for item in monthly]
    values = [int(item["count"]) for item in monthly]

    plt.style.use("dark_background")
    fig, (ax, ax_zoom) = plt.subplots(
        2,
        1,
        figsize=(16, 10),
        dpi=140,
        gridspec_kw={"height_ratios": [2.2, 1.2], "hspace": 0.28},
    )
    fig.patch.set_facecolor("#0b1220")
    ax.set_facecolor("#0b1220")
    ax_zoom.set_facecolor("#0b1220")

    x = list(range(len(values)))
    bar_kwargs = {
        "color": "#22d3ee",
        "alpha": 0.85,
        "width": 0.9,
        "edgecolor": "#67e8f9",
        "linewidth": 0.25,
    }
    ax.bar(x, values, **bar_kwargs)
    ax.plot(x, values, color="#a855f7", linewidth=1.5, alpha=0.65)

    # Zoom panel for readability without outlier domination.
    sorted_vals = sorted(values)
    p98_idx = max(0, int(len(sorted_vals) * 0.98) - 1)
    p98 = max(1, sorted_vals[p98_idx]) if sorted_vals else 1
    ax_zoom.bar(x, values, **bar_kwargs)
    ax_zoom.plot(x, values, color="#a855f7", linewidth=1.25, alpha=0.65)
    ax_zoom.set_ylim(0, p98 * 1.12)

    ticks = [i for i, m in enumerate(labels) if m.endswith("-01")]
    if ticks:
        ax.set_xticks(ticks)
        ax.set_xticklabels([labels[i][:4] for i in ticks], fontsize=9, color="#cbd5e1")
        ax_zoom.set_xticks(ticks)
        ax_zoom.set_xticklabels([labels[i][:4] for i in ticks], fontsize=9, color="#cbd5e1")
    else:
        ax.set_xticks(x[:: max(1, len(x) // 8)])
        ax.set_xticklabels([labels[i] for i in ax.get_xticks().astype(int)], fontsize=9, color="#cbd5e1")
        ax_zoom.set_xticks(ax.get_xticks())
        ax_zoom.set_xticklabels([labels[i] for i in ax_zoom.get_xticks().astype(int)], fontsize=9, color="#cbd5e1")

    ax.grid(True, axis="y", color="#1e293b", linestyle="-", linewidth=0.7, alpha=0.75)
    ax_zoom.grid(True, axis="y", color="#1e293b", linestyle="-", linewidth=0.7, alpha=0.75)
    for spine in ax.spines.values():
        spine.set_color("#334155")
    for spine in ax_zoom.spines.values():
        spine.set_color("#334155")

    ax.set_title(
        "GitHub Account Activity (Full History)",
        color="white",
        fontsize=18,
        pad=18,
        fontweight="bold",
    )
    ax.set_ylabel("Contributions / Month (full)", color="#cbd5e1", fontsize=11)
    ax_zoom.set_ylabel("Zoomed (<=98th pct)", color="#cbd5e1", fontsize=10)
    ax_zoom.set_xlabel("Year", color="#cbd5e1", fontsize=11)

    summary = f"Total contributions: {total:,}   |   Commit contributions: {commits:,}   |   Active days: {active_days:,}"
    ax.text(
        0.01,
        1.02,
        summary,
        transform=ax.transAxes,
        color="#94a3b8",
        fontsize=10,
        va="bottom",
    )
    ax_zoom.text(
        0.01,
        1.02,
        f"98th percentile monthly cap: {p98:,}",
        transform=ax_zoom.transAxes,
        color="#94a3b8",
        fontsize=9,
        va="bottom",
    )

    out_chart.parent.mkdir(parents=True, exist_ok=True)
    fig.subplots_adjust(top=0.93, bottom=0.08, left=0.06, right=0.99, hspace=0.28)
    fig.savefig(out_chart, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    args = parse_args()
    out_json = Path(args.out_json)
    out_chart = Path(args.out_chart)
    projects_root = Path(args.projects_root)

    user_resp = run_gh_graphql(USER_QUERY, {"login": args.user})
    user = ((user_resp.get("data") or {}).get("user")) or {}
    created_at = str(user.get("createdAt", "")).strip()
    if not created_at:
        raise RuntimeError("Unable to fetch user createdAt from GitHub.")

    created_date = dt.datetime.fromisoformat(created_at.replace("Z", "+00:00")).date()
    today = dt.date.today()

    total_contributions = 0
    commit_contributions = 0
    pull_request_contributions = 0
    issue_contributions = 0
    review_contributions = 0
    daily_counts: dict[dt.date, int] = {}

    for seg_start, seg_end in iter_segments(created_date, today):
        from_iso = f"{seg_start.isoformat()}T00:00:00Z"
        to_iso = f"{seg_end.isoformat()}T23:59:59Z"
        resp = run_gh_graphql(
            CONTRIB_QUERY,
            {"login": args.user, "from": from_iso, "to": to_iso},
        )
        coll = ((((resp.get("data") or {}).get("user")) or {}).get("contributionsCollection")) or {}

        total_contributions += int(coll.get("contributionCalendar", {}).get("totalContributions", 0) or 0)
        commit_contributions += int(coll.get("totalCommitContributions", 0) or 0)
        pull_request_contributions += int(coll.get("totalPullRequestContributions", 0) or 0)
        issue_contributions += int(coll.get("totalIssueContributions", 0) or 0)
        review_contributions += int(coll.get("totalPullRequestReviewContributions", 0) or 0)

        weeks = coll.get("contributionCalendar", {}).get("weeks", []) or []
        for week in weeks:
            for day in (week or {}).get("contributionDays", []) or []:
                date_str = str(day.get("date", "")).strip()
                if not date_str:
                    continue
                day_date = dt.date.fromisoformat(date_str)
                daily_counts[day_date] = int(day.get("contributionCount", 0) or 0)

    monthly = build_monthly_counts(daily_counts)
    active_days, longest_streak = calculate_streaks(daily_counts)
    cutoff = today - dt.timedelta(days=29)
    contributions_last_30_days = sum(count for day, count in daily_counts.items() if day >= cutoff)

    estimated_source_loc = count_loc(projects_root)

    payload = {
        "generated_at": dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "range_start": created_date.isoformat(),
        "range_end": today.isoformat(),
        "total_contributions": total_contributions,
        "commit_contributions": commit_contributions,
        "pull_request_contributions": pull_request_contributions,
        "issue_contributions": issue_contributions,
        "review_contributions": review_contributions,
        "active_days": active_days,
        "longest_streak_days": longest_streak,
        "contributions_last_30_days": contributions_last_30_days,
        "estimated_source_loc": estimated_source_loc,
        "loc_scope_note": "Estimated from local tracked source files across showcase repos; excludes vendored directories and non-code vault content.",
        "monthly_contributions": monthly,
        "nbp_note": str(args.nbp_note).strip(),
    }

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    render_chart(
        monthly=monthly,
        out_chart=out_chart,
        total=total_contributions,
        commits=commit_contributions,
        active_days=active_days,
    )


if __name__ == "__main__":
    main()
