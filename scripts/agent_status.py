"""CLI for keeping AI agent progress in sync with docs/agents/."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AGENTS_DIR = ROOT / "docs" / "agents"
STATE_PATH = AGENTS_DIR / "status.json"
STATUS_BOARD_PATH = AGENTS_DIR / "status-board.md"
HANDOFF_PATH = AGENTS_DIR / "handoff.md"
ACTIVE_DIR = AGENTS_DIR / "active"

VALID_STATUSES = {"todo", "in_progress", "blocked", "review", "done"}
AGENT_SECTIONS = {
    "started": ("summary", "started"),
    "in_progress": ("summary", "in_progress"),
    "completed": ("summary", "completed"),
    "decisions": ("decisions",),
    "blockers": ("blockers",),
    "next_actions": ("next_actions",),
    "depends_on": ("depends_on",),
}
HANDOFF_SECTIONS = {
    "current_blockers": ("handoff", "current_blockers"),
    "pending_decisions": ("handoff", "pending_decisions"),
    "next_recommended_actions": ("handoff", "next_recommended_actions"),
    "entries": ("handoff", "entries"),
}


def now_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def today_date() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "agent"


def unique_items(items: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for item in items:
        normalized = item.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        unique.append(normalized)
    return unique


def load_state() -> dict[str, Any]:
    with STATE_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_state(state: dict[str, Any]) -> None:
    with STATE_PATH.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def touch_state(state: dict[str, Any]) -> None:
    state.setdefault("meta", {})["last_updated"] = now_timestamp()


def ensure_status(status: str) -> str:
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status '{status}'. Expected one of: {sorted(VALID_STATUSES)}")
    return status


def area_keys(state: dict[str, Any]) -> set[str]:
    return {area["key"] for area in state.get("areas", [])}


def validate_area_key(state: dict[str, Any], key: str) -> None:
    if key and key not in area_keys(state):
        raise ValueError(f"Unknown area key '{key}'.")


def find_area(state: dict[str, Any], key: str) -> dict[str, Any] | None:
    for area in state.get("areas", []):
        if area["key"] == key:
            return area
    return None


def default_agent(name: str) -> dict[str, Any]:
    return {
        "name": name,
        "date": today_date(),
        "scope": "",
        "status": "todo",
        "owner": name,
        "related_area": "",
        "depends_on": [],
        "summary": {
            "started": [],
            "in_progress": [],
            "completed": [],
        },
        "decisions": [],
        "blockers": [],
        "next_actions": [],
    }


def find_agent(state: dict[str, Any], name: str) -> dict[str, Any] | None:
    for agent in state.get("agents", []):
        if agent["name"] == name:
            return agent
    return None


def get_or_create_agent(state: dict[str, Any], name: str) -> dict[str, Any]:
    agent = find_agent(state, name)
    if agent is None:
        agent = default_agent(name)
        state.setdefault("agents", []).append(agent)
    return agent


def markdown_list(items: list[str], empty_message: str = "None.") -> list[str]:
    if not items:
        return [f"- {empty_message}"]
    return [f"- {item}" for item in items]


def numbered_list(items: list[str], empty_message: str = "None.") -> list[str]:
    if not items:
        return [f"1. {empty_message}"]
    return [f"{index}. {item}" for index, item in enumerate(items, start=1)]


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|")


def render_status_board(state: dict[str, Any]) -> str:
    lines = [
        "# Agent Status Board",
        "",
        f"Last updated: {state['meta'].get('last_updated', today_date())}",
        "",
        "This file is generated from `status.json`. Edit the JSON or use `scripts/agent_status.py`.",
        "",
        "---",
        "",
        "## Project Overview",
        "",
        "| Area | Owner | Status | Notes |",
        "|------|-------|--------|-------|",
    ]

    for area in state.get("areas", []):
        lines.append(
            "| {label} | {owner} | {status} | {notes} |".format(
                label=escape_cell(area["label"]),
                owner=escape_cell(area["owner"]),
                status=escape_cell(area["status"]),
                notes=escape_cell(area["notes"]),
            )
        )

    lines.extend([
        "",
        "---",
        "",
        "## Current Priorities",
        "",
        *numbered_list(state.get("priorities", []), empty_message="No priorities recorded."),
        "",
        "---",
        "",
        "## Open Blockers",
        "",
        *markdown_list(state.get("handoff", {}).get("current_blockers", []), empty_message="None recorded yet."),
        "",
        "---",
        "",
        "## Update Rules",
        "",
        "- Use `status.json` as the single source of truth.",
        "- Regenerate this board with `python scripts/agent_status.py sync` after manual JSON edits.",
        "- Detailed agent notes are rendered into `active/*.md`.",
    ])
    return "\n".join(lines) + "\n"


def render_handoff(state: dict[str, Any]) -> str:
    handoff = state.get("handoff", {})
    lines = [
        "# Handoff",
        "",
        f"Last updated: {state['meta'].get('last_updated', today_date())}",
        "",
        "This file is generated from `status.json`. Edit the JSON or use `scripts/agent_status.py`.",
        "",
        "---",
        "",
        "## Current Blockers",
        "",
        *markdown_list(handoff.get("current_blockers", [])),
        "",
        "---",
        "",
        "## Pending Decisions",
        "",
        *markdown_list(handoff.get("pending_decisions", [])),
        "",
        "---",
        "",
        "## Next Recommended Actions",
        "",
        *numbered_list(handoff.get("next_recommended_actions", [])),
        "",
        "---",
        "",
        "## Entries",
        "",
    ]

    entries = handoff.get("entries", [])
    if not entries:
        lines.append("- None.")
    else:
        for entry in entries:
            lines.extend(
                [
                    f"- Agent: {entry['agent']}",
                    f"  Date: {entry['date']}",
                    f"  Scope: {entry['scope']}",
                    f"  Outcome: {entry['outcome']}",
                    f"  Next: {entry['next']}",
                    f"  Blocker: {entry.get('blocker', 'None')}",
                ]
            )
    return "\n".join(lines) + "\n"


def render_agent_log(agent: dict[str, Any]) -> str:
    summary = agent.get("summary", {})
    lines = [
        f"# Agent: {agent['name']}",
        "",
        f"Last updated: {now_timestamp()}",
        "",
        "This file is generated from `../status.json`. Edit the JSON or use `scripts/agent_status.py`.",
        "",
        "---",
        "",
        "## Identity",
        "",
        f"- Agent name: {agent['name']}",
        f"- Date: {agent.get('date', today_date())}",
        f"- Scope: {agent.get('scope') or '-'}",
        "",
        "---",
        "",
        "## Current Status",
        "",
        f"- Status: {agent.get('status', 'todo')}",
        f"- Owner: {agent.get('owner', agent['name'])}",
        f"- Related area: {agent.get('related_area') or '-'}",
        f"- Depends on: {', '.join(agent.get('depends_on', [])) or '-'}",
        "",
        "---",
        "",
        "## Work Summary",
        "",
        "### Started",
        "",
        *markdown_list(summary.get('started', [])),
        "",
        "### In Progress",
        "",
        *markdown_list(summary.get('in_progress', [])),
        "",
        "### Completed",
        "",
        *markdown_list(summary.get('completed', [])),
        "",
        "---",
        "",
        "## Decisions",
        "",
        *markdown_list(agent.get('decisions', [])),
        "",
        "---",
        "",
        "## Blockers",
        "",
        *markdown_list(agent.get('blockers', [])),
        "",
        "---",
        "",
        "## Next Actions",
        "",
        *numbered_list(agent.get('next_actions', [])),
    ]
    return "\n".join(lines) + "\n"


def write_rendered_files(state: dict[str, Any]) -> None:
    AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    ACTIVE_DIR.mkdir(parents=True, exist_ok=True)

    STATUS_BOARD_PATH.write_text(render_status_board(state), encoding="utf-8")
    HANDOFF_PATH.write_text(render_handoff(state), encoding="utf-8")

    generated_paths: set[Path] = set()
    for agent in state.get("agents", []):
        destination = ACTIVE_DIR / f"{slugify(agent['name'])}.md"
        destination.write_text(render_agent_log(agent), encoding="utf-8")
        generated_paths.add(destination)

    for existing in ACTIVE_DIR.glob("*.md"):
        if existing not in generated_paths:
            existing.unlink()

    gitkeep = ACTIVE_DIR / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.write_text("", encoding="utf-8")


def sync(state: dict[str, Any], write_state: bool) -> None:
    touch_state(state)
    if write_state:
        save_state(state)
    write_rendered_files(state)


def set_area(args: argparse.Namespace) -> None:
    state = load_state()
    area = find_area(state, args.key)

    if area is None:
        if not args.label:
            raise ValueError("New areas require --label.")
        area = {
            "key": args.key,
            "label": args.label,
            "owner": args.owner or "unassigned",
            "status": ensure_status(args.status or "todo"),
            "notes": args.notes or "",
        }
        state.setdefault("areas", []).append(area)
    else:
        if args.label:
            area["label"] = args.label
        if args.owner:
            area["owner"] = args.owner
        if args.status:
            area["status"] = ensure_status(args.status)
        if args.notes:
            area["notes"] = args.notes

    sync(state, write_state=True)


def set_agent(args: argparse.Namespace) -> None:
    state = load_state()
    agent = get_or_create_agent(state, args.name)

    if args.scope is not None:
        agent["scope"] = args.scope
    if args.status is not None:
        agent["status"] = ensure_status(args.status)
    if args.owner is not None:
        agent["owner"] = args.owner
    if args.area is not None:
        validate_area_key(state, args.area)
        agent["related_area"] = args.area
    if args.date is not None:
        agent["date"] = args.date
    if args.depends_on is not None:
        for key in args.depends_on:
            validate_area_key(state, key)
        agent["depends_on"] = unique_items(args.depends_on)
    if args.started is not None:
        agent["summary"]["started"] = unique_items(args.started)
    if args.in_progress_items is not None:
        agent["summary"]["in_progress"] = unique_items(args.in_progress_items)
    if args.completed is not None:
        agent["summary"]["completed"] = unique_items(args.completed)
    if args.decisions is not None:
        agent["decisions"] = unique_items(args.decisions)
    if args.blockers is not None:
        agent["blockers"] = unique_items(args.blockers)
    if args.next_actions is not None:
        agent["next_actions"] = unique_items(args.next_actions)

    sync(state, write_state=True)


def append_agent(args: argparse.Namespace) -> None:
    state = load_state()
    agent = get_or_create_agent(state, args.name)
    path = AGENT_SECTIONS[args.section]

    cursor: Any = agent
    for key in path[:-1]:
        cursor = cursor[key]
    target = cursor[path[-1]]
    cursor[path[-1]] = unique_items([*target, args.item])

    sync(state, write_state=True)


def clear_agent_section(args: argparse.Namespace) -> None:
    state = load_state()
    agent = get_or_create_agent(state, args.name)
    path = AGENT_SECTIONS[args.section]

    cursor: Any = agent
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = []

    sync(state, write_state=True)


def set_handoff(args: argparse.Namespace) -> None:
    state = load_state()
    handoff = state.setdefault("handoff", {})

    if args.current_blockers is not None:
        handoff["current_blockers"] = unique_items(args.current_blockers)
    if args.pending_decisions is not None:
        handoff["pending_decisions"] = unique_items(args.pending_decisions)
    if args.next_recommended_actions is not None:
        handoff["next_recommended_actions"] = unique_items(args.next_recommended_actions)

    sync(state, write_state=True)


def clear_handoff_section(args: argparse.Namespace) -> None:
    state = load_state()
    path = HANDOFF_SECTIONS[args.section]

    cursor: Any = state
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = []

    sync(state, write_state=True)


def add_handoff(args: argparse.Namespace) -> None:
    state = load_state()
    handoff = state.setdefault("handoff", {})
    entries = handoff.setdefault("entries", [])
    entries.append(
        {
            "agent": args.agent,
            "date": today_date(),
            "scope": args.scope,
            "outcome": args.outcome,
            "next": args.next_step,
            "blocker": args.blocker or "None",
        }
    )

    sync(state, write_state=True)


def run_sync(_: argparse.Namespace) -> None:
    state = load_state()
    sync(state, write_state=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Update and render agent collaboration state.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sync_parser = subparsers.add_parser("sync", help="Render markdown files from status.json.")
    sync_parser.set_defaults(handler=run_sync)

    area_parser = subparsers.add_parser("set-area", help="Create or update a project area.")
    area_parser.add_argument("--key", required=True)
    area_parser.add_argument("--label")
    area_parser.add_argument("--owner")
    area_parser.add_argument("--status", choices=sorted(VALID_STATUSES))
    area_parser.add_argument("--notes")
    area_parser.set_defaults(handler=set_area)

    agent_parser = subparsers.add_parser("set-agent", help="Create or replace agent fields.")
    agent_parser.add_argument("--name", required=True)
    agent_parser.add_argument("--date")
    agent_parser.add_argument("--scope")
    agent_parser.add_argument("--status", choices=sorted(VALID_STATUSES))
    agent_parser.add_argument("--owner")
    agent_parser.add_argument("--area")
    agent_parser.add_argument("--depends-on", action="append")
    agent_parser.add_argument("--started", action="append")
    agent_parser.add_argument("--in-progress-item", dest="in_progress_items", action="append")
    agent_parser.add_argument("--completed", action="append")
    agent_parser.add_argument("--decision", dest="decisions", action="append")
    agent_parser.add_argument("--blocker", dest="blockers", action="append")
    agent_parser.add_argument("--next-action", dest="next_actions", action="append")
    agent_parser.set_defaults(handler=set_agent)

    append_parser = subparsers.add_parser("append-agent", help="Append one item to an agent section.")
    append_parser.add_argument("--name", required=True)
    append_parser.add_argument("--section", required=True, choices=sorted(AGENT_SECTIONS))
    append_parser.add_argument("--item", required=True)
    append_parser.set_defaults(handler=append_agent)

    clear_agent_parser = subparsers.add_parser("clear-agent-section", help="Clear one agent list section.")
    clear_agent_parser.add_argument("--name", required=True)
    clear_agent_parser.add_argument("--section", required=True, choices=sorted(AGENT_SECTIONS))
    clear_agent_parser.set_defaults(handler=clear_agent_section)

    handoff_parser = subparsers.add_parser("set-handoff", help="Replace handoff summary sections.")
    handoff_parser.add_argument("--current-blocker", dest="current_blockers", action="append")
    handoff_parser.add_argument("--pending-decision", dest="pending_decisions", action="append")
    handoff_parser.add_argument("--next-action", dest="next_recommended_actions", action="append")
    handoff_parser.set_defaults(handler=set_handoff)

    clear_handoff_parser = subparsers.add_parser("clear-handoff-section", help="Clear one handoff section.")
    clear_handoff_parser.add_argument("--section", required=True, choices=sorted(HANDOFF_SECTIONS))
    clear_handoff_parser.set_defaults(handler=clear_handoff_section)

    add_handoff_parser = subparsers.add_parser("add-handoff", help="Append a handoff entry.")
    add_handoff_parser.add_argument("--agent", required=True)
    add_handoff_parser.add_argument("--scope", required=True)
    add_handoff_parser.add_argument("--outcome", required=True)
    add_handoff_parser.add_argument("--next", dest="next_step", required=True)
    add_handoff_parser.add_argument("--blocker")
    add_handoff_parser.set_defaults(handler=add_handoff)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()