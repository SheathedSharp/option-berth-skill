---
name: option-berth
description: Use oberth to inspect and operate services for the current worktree, read the engine's failure reason and next step, tell a trustworthy listener observation from a sandbox limitation, and observe explicitly related local worktrees during parallel development.
metadata:
  version: "0.8.0"
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
oberth status --json --brief
~~~

The brief document is the runtime facts: service states, declared and actual
ports, `health_status`, the current exit reason and next step, the code-change
fields, in-flight `starting`, and — when the listener table cannot be trusted —
the top-level `observation`. It leaves out the manifest copies, the git
summary, the change ledger and the attention handoff, which are most of a full
`status --json`. Narrow it further with `--only api,worker` when the task is
about named services.

Read `observation` before you use `ports`: `ports: []` together with
`observation.state: blind` or `bind_denied` means this process cannot see
listeners, not that nothing is running. The observation section of
[references/operations.md](references/operations.md) says what to do next.

Go to the full `oberth status --json` only when the brief document cannot
answer the question: which manifest draft is pending, what changed since the
last read, what the repository summary is, or the attention handoff. Reading it
first costs the context the brief read saves.

For a service task, the default loop is:

1. Read `status --json --brief`, the declared services, and `observation`.
2. Run the operation: `oberth up --wait --json`,
   `oberth restart --only <service> --json`, or `oberth down --json`. A
   `started` service with `services[].ready: false` is not confirmed ready; it
   is not a failure.
3. On failure, match `services[].exit_reason` and `health_status` against the
   table in [references/operations.md](references/operations.md), read the log
   the reason names, and report `services[].hint` when it is present. The same
   evidence is `oberth logs <service> --once --json --run current
   --first-error`, which returns the first matching line of this run instead of
   the whole file.
4. If the command itself returned an `observation_*` code, it is a fact about
   this process, not a service exit reason. Follow the observation and
   sandbox section instead of the exit table.
5. Fix the declared input, repeat the operation, and refresh
   `status --json --brief`.

`attention_path` is optional context, not a required branch after `status`, and
the brief read does not carry it at all. Read
[references/attention.md](references/attention.md) only when the task is
explicitly about Jev, quality feedback, or human handoff, or when the full
`status --json` published an `attention_path` and the current anomaly blocks the
task and a person must choose among the fixed options. A `machine:` entry that
no declared service `depends_on` is a read-only fact: report its `listening`
value; do not hand it off, arm a session, or start it.

For code changes, read the worktree-scoped Git summary as well:

~~~sh
oberth git files --json
oberth git diff --json --file path/to/file
~~~

Read the detailed guide only for the mode the task needs:

- Service start, stop, restart, logs, status reporting, a failed start, an
  observation/sandbox error, or worktree identity and cleanup:
  [references/operations.md](references/operations.md).
- Manifest drafting, adoption, `prepare:` / `prepare_inputs:`, `sources:`,
  `env_file:`, health checks, ports and references such as `${worktree}`,
  `machine:`, or `workspace:` [references/manifest.md](references/manifest.md).
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
- An observation code is evidence about this process, not about the machine.
  Do not retry the identical sandboxed call, do not start a daemon from the
  sandbox, and never report an empty `ports` list as "nothing is running".
  Report the code and hint; the bounded next step is a normal terminal with
  `oberth serve --detach`, or `oberth doctor --only listener_observation` to
  confirm the limitation.
- `machine:` entries are read-only dependencies. `up` and `down` do not operate
  them; `kill` requires a specifically named target and the existing approval
  boundary. An unreferenced `machine:` entry never justifies a handoff.
- `workspace:` entries are read-only addresses in another checkout. `up`,
  `down`, and `restart` never start or stop the other checkout. `oberth
  worktrees` is a read-only identity ledger: never delete a database, data
  directory, or checkout on the person's behalf. To stop a checkout whose
  directory is gone, use `oberth down --identity <wt_…>`.
- A person owns `oberth.yaml`. The agent may draft and explain a manifest, but
  adoption is an explicit human choice. Do not edit it to hide a failure.
- Do not write hooks, MCP registrations, agent configuration, or a second
  product model. Do not answer the whole-machine port-radar question.
- Do not arm a task-scoped attention session by default. Arm it only when the
  person explicitly asks for continuous attention on a long-running task.
- Refresh `oberth status --json --brief` after a control command, and the full
  `oberth status --json` before acting on a derived attention request.

The detailed guides are part of this skill's distribution. Read only the guide
needed for the current task; do not load all references by default.
