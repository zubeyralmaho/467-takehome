# Agent: copilot-ops

Last updated: 2026-04-15 22:24

This file is generated from `../status.json`. Edit the JSON or use `scripts/agent_status.py`.

---

## Identity

- Agent name: copilot-ops
- Date: 2026-04-13
- Scope: Set up agent coordination workspace and CLI

---

## Current Status

- Status: done
- Owner: copilot-ops
- Related area: -
- Depends on: -

---

## Work Summary

### Started

- Designed docs/agents collaboration layout

### In Progress

- None.

### Completed

- Added status.json as the single source of truth
- Implemented scripts/agent_status.py for sync and updates
- Updated documentation to describe the tracking workflow

---

## Decisions

- Used JSON plus generated markdown instead of freeform notes

---

## Blockers

- None.

---

## Next Actions

1. Use set-area when an agent claims a project area
2. Use append-agent during active work to keep logs incremental
