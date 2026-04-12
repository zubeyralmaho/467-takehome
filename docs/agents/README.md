# Agent Workspace

This folder is the operational workspace for AI agents working on the project.

Its purpose is different from the numbered architecture documents:

- `docs/01-11`: stable design, implementation, and report documentation
- `docs/agents/`: live execution state, handoff notes, and agent-specific progress

The single source of truth is `status.json`. Markdown files in this folder should be treated as generated views.

For parallel work, use the short operating protocol in `protocol.md`.
For a copy-pasteable agent instruction, use `system-prompt.md`.

---

## Recommended Workflow

For multi-agent parallel execution, follow `protocol.md` first and use the workflow below as the mechanical update sequence.

When an agent starts work:

1. Read `status-board.md` for the current project snapshot.
2. Create or update the agent state via `scripts/agent_status.py set-agent ...`.
3. Append progress as work advances with `append-agent`.
4. Update the relevant project area with `set-area` when ownership or status changes.
5. Add a handoff entry when work is paused or transferred.

---

## Folder Layout

```text
docs/agents/
|-- README.md                # Operational rules for agent collaboration
|-- protocol.md             # Short rules for safe multi-agent parallel work
|-- system-prompt.md        # Very short copy-paste prompt for parallel agents
|-- status.json             # Canonical machine-readable state
|-- status-board.md          # Canonical high-level project snapshot
|-- handoff.md               # Shared blockers, next actions, ownership handoff
|-- agent-template.md        # Template for new agent work logs
+-- active/
    +-- .gitkeep             # Keeps the directory in version control
```

---

## Status Convention

Use the same status vocabulary everywhere:

- `todo`: not started yet
- `in_progress`: actively being worked on
- `blocked`: waiting on a dependency or decision
- `review`: implemented, pending validation or review
- `done`: completed and verified

---

## CLI Usage

Common commands:

```bash
# Regenerate markdown views from the JSON state
python scripts/agent_status.py sync

# Claim an area and mark it in progress
python scripts/agent_status.py set-area \
    --key q1_text_classification \
    --owner agent-q1 \
    --status in_progress \
    --notes "TF-IDF baseline implementation in progress"

# Create or update an agent record
python scripts/agent_status.py set-agent \
    --name agent-q1 \
    --scope "Q1 baseline training pipeline" \
    --status in_progress \
    --area q1_text_classification \
    --started "Reviewed existing Q1 module" \
    --next-action "Implement baseline trainer"

# Append progress incrementally
python scripts/agent_status.py append-agent \
    --name agent-q1 \
    --section completed \
    --item "Implemented TF-IDF data flow"

# Add a handoff entry
python scripts/agent_status.py add-handoff \
    --agent agent-q1 \
    --scope "Q1 baseline setup" \
    --outcome "Data flow and baseline scaffolding completed" \
    --next "Run validation experiment"
```

---

## Why This Is Better Than A Single Notes File

A single markdown file becomes noisy quickly and creates edit conflicts when multiple agents write to it.

This structure is more reliable because:

- `status.json` gives one canonical machine-readable state.
- `status-board.md` stays short and human-readable.
- Each agent gets a rendered file under `active/` with less risk of conflicts.
- `handoff.md` stays focused on coordination instead of becoming a scratchpad.
- The numbered docs stay clean and stable instead of becoming a work log.

This is the better method than raw notes because updates become structured and scriptable without adding a heavy database or external service.

If you later run multiple agents truly in parallel, the next scaling step is splitting the machine-readable state into one file per agent plus one project-level summary file. For the current repo size, the single JSON plus generated views approach is still the simpler trade-off.