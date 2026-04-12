# Multi-Agent Parallel Work Protocol

Use this protocol when multiple agents are working on the project at the same time.

The goal is simple: keep ownership clear, avoid file conflicts, and leave clean handoffs.

---

## Core Rules

1. One area has one active owner at a time.
2. One agent should work on one narrow deliverable, not a broad theme.
3. Shared state should be updated only at checkpoints, not after every small step.
4. An agent must not edit another agent's claimed files without an explicit handoff.
5. If the task touches a shared module, coordinate first and keep the change minimal.
6. A blocker must be recorded immediately, not after the agent stops.
7. Before stopping, every agent must leave a next action another agent can execute directly.

---

## Standard Flow

1. Claim
   - Read the current board.
   - Claim one project area.
   - Create or update the agent record with scope, owner, and status.

2. Execute
   - Stay inside the claimed area and file set.
   - Record only meaningful progress milestones.
   - Do not rewrite shared state repeatedly during active coding.

3. Block
   - Mark the agent or area as `blocked`.
   - Add a handoff entry with the blocker and the exact next step.

4. Finish
   - Record completed work.
   - Move the area to `review` or `done`.
   - Leave a handoff if follow-up work remains.

---

## Conflict Rules

- If two agents need the same area, split the scope before coding.
- If two agents need the same file, only one keeps ownership; the other waits or takes a different slice.
- Prefer adding a new module over editing a hot shared file when both options are valid.
- If scope expands beyond the original claim, open a new claim instead of silently stretching the task.

---

## Checkpoint Cadence

Update shared agent state only at these moments:

- when claiming work
- after a meaningful milestone
- when blocked
- when handing off
- when moving to `review` or `done`

This keeps parallel work safer because it reduces write contention on shared tracking files.

---

## Minimum Handoff Standard

Every handoff should answer five things:

1. What was changed?
2. What is still incomplete?
3. What is the next concrete action?
4. Is there a blocker?
5. Which area now owns the next step?

---

## Definition Of Done

An agent should not mark work as `done` unless:

- the claimed scope is finished
- relevant validation was run
- status was updated
- the next dependency, if any, is explicit

If implementation is finished but validation or review is still pending, use `review` instead of `done`.