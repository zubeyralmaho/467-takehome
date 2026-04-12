# Agent Workspace

This folder is the operational workspace for AI agents working on the project.

Its purpose is different from the numbered architecture documents:

- `docs/01-11`: stable design, implementation, and report documentation
- `docs/agents/`: live execution state, handoff notes, and agent-specific progress

---

## Recommended Workflow

When an agent starts work:

1. Read `status-board.md` for the current project snapshot.
2. Claim or create an agent file under `active/` using the template.
3. Update the relevant task status before and after meaningful work.
4. Record blockers, decisions, and next actions in the same agent file.
5. Reflect project-level changes in `status-board.md` when the global state changes.

---

## Folder Layout

```text
docs/agents/
|-- README.md                # Operational rules for agent collaboration
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

## Why This Is Better Than A Single Notes File

A single markdown file becomes noisy quickly and creates edit conflicts when multiple agents write to it.

This structure is more reliable because:

- `status-board.md` stays short and human-readable.
- Each agent can update its own file under `active/` with less risk of conflicts.
- `handoff.md` gives one place for blockers and next actions.
- The numbered docs stay clean and stable instead of becoming a work log.

If you later want stricter automation, the next step would be adding a machine-readable `status.json` file as the single source of truth and generating the markdown board from it. For the current project size, the markdown-first structure is simpler and sufficient.