---
name: option-berth
description: Use oberth to inspect and operate services for the current worktree, read the engine's failure reason and next step, and observe explicitly related local worktrees during parallel development.
metadata:
  version: "0.5.0"
  source: "github.com/SheathedSharp/option-berth"
---

# option-berth

`oberth` is the source of truth for declared services and runtime facts. Run it
from the worktree that the task concerns. Use `--json` for a single document or
NDJSON for a stream; errors belong on stderr.

This skill ships with the repository and is part of the product, not a summary
of it: it is how a coding agent is meant to learn `oberth`. Commands are grouped
by what you are trying to do — facts, operations, code and declaration, handoff,
runtime — and `oberth --help` shows the same grouping.

## Default loop

Read the current worktree before reasoning about services:

~~~sh
oberth status --json
~~~

This gives the declaration, service runs, listeners attributed to the worktree,
branch and dirty counts, recent exits, and any pending manifest draft. Do not
turn it into a question about every port on the machine.

For a service task, the default loop is:

1. Read `status --json` and the declared services.
2. Run the operation: `oberth up --wait --json`,
   `oberth restart --only <service> --json`, or `oberth down --json`.
3. On failure, match `last_exit.reason` and `health_status` against the table in
   [references/operations.md](references/operations.md), and read the log the
   reason names.
4. Fix the declared input, repeat the operation, and refresh `status --json`.

`attention_path` is optional context, not a required branch after `status`.
Read [references/attention.md](references/attention.md) only when the task is
explicitly about Jev, quality feedback, or human handoff, or when the current
anomaly blocks the task and a person must choose among the fixed options. A
`machine:` entry that no declared service `depends_on` is a read-only fact:
report its `listening` value; do not hand it off, arm a session, or start it.

For code changes, read the worktree-scoped Git summary as well:

~~~sh
oberth git files --json
oberth git diff --json --file path/to/file
~~~

Read the detailed guide only for the mode the task needs:

- Service start, stop, restart, logs, status reporting, or a failed start:
  [references/operations.md](references/operations.md).
- Manifest drafting, adoption, `prepare:`, ports, or `machine:`:
  [references/manifest.md](references/manifest.md).
- What work has been done in this worktree, or which workplace new work belongs
  to: [references/workplace.md](references/workplace.md).
- Explicitly related worktrees or repositories:
  [references/cross-worktree.md](references/cross-worktree.md).
- `attention_path`, Jev, human-in-the-loop, or quality feedback (optional):
  [references/attention.md](references/attention.md).

## Boundaries

- Facts come from the CLI and daemon. Do not infer runtime facts from model
  output, ports, process names, branches, or logs that were not published by
  `oberth`.
- `machine:` entries are read-only dependencies. `up` and `down` do not operate
  them; `kill` requires a specifically named target and the existing approval
  boundary. An unreferenced `machine:` entry never justifies a handoff.
- A person owns `oberth.yaml`. The agent may draft and explain a manifest, but
  adoption is an explicit human choice. Do not edit it to hide a failure.
- Do not write hooks, MCP registrations, agent configuration, or a second
  product model. Do not answer the whole-machine port-radar question.
- Do not arm a task-scoped attention session by default. Arm it only when the
  person explicitly asks for continuous attention on a long-running task.
- Refresh `oberth status --json` after a control command and before acting on a
  derived attention request.

The detailed guides are part of this skill's distribution. Read only the guide
needed for the current task; do not load all references by default.
