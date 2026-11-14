---
name: option-berth
description: Use oberth to inspect and operate services for the current worktree, read the engine's failure reason and next step, tell a trustworthy listener observation from a sandbox limitation, and observe explicitly related local worktrees during parallel development.
metadata:
  version: "0.9.2"
  source: "github.com/SheathedSharp/option-berth"
---

# option-berth

`oberth` is the source of truth for declared services and runtime facts. Run it
from the worktree that the task concerns. Use `--json` for a single document or
NDJSON for a stream; errors belong on stderr.

This skill ships with the repository and is part of the product, not a summary
of it: it is how a coding agent is meant to learn `oberth`. Commands are grouped
by what you are trying to do: facts, operations, code and declaration, handoff,
runtime. `oberth --help` shows the same grouping.

## Default loop

Read the current worktree before reasoning about services:

```sh
oberth status --json --brief
```

The brief document is the runtime facts: service states, declared and actual
ports, `services[].health.status` when the key is present (the full document's
`health_status`), the current exit reason and next step, the code-change and
executable fields, in-flight `starting`, and the top-level `observation` when
the listener table cannot be trusted. It leaves out the manifest copies, the git
summary, the change ledger, and the attention handoff, which are most of a full
`status --json`. Narrow it further with `--only api,worker` when the task is
about named services.

Per-service keys are present only when the fact exists. A stopped service has
no `health` or `port_actual`, and an absent `code_changed_since_start` means
unknown, not "unchanged". Absence is never a negative result: read `running`
first, and use `exit_reason` for a service that is down. A running service with
a declared health check may carry `health.status: unknown` with
`reason: pending` before its first probe; that is not a failure.

`worktree.ad_hoc_runs` lists runs started with `oberth start` that the manifest
does not declare: `name`, `run_id`, `group`, `pid` and the `ports` each holds.
Those ports belong to oberth, not to a stray process, so do not kill them by
port. `restart --only` accepts only declared services; for an ad-hoc run, use
the start line its `not_found` hint prints (or `oberth start` with the same
group, name and port).

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
   `started` service with `services[].ready: false` is not confirmed ready. It
   is not a failure. Without `--wait`, `up` publishes `next` when readiness is
   unconfirmed; run that command instead of polling sockets.
3. On failure, match `services[].exit_reason` and, when present,
   `services[].health.status` against the table in
   [references/operations.md](references/operations.md), read the log the
   reason names, and report `services[].hint` when it is present. The same
   evidence is `oberth logs <service> --once --json --run current
   --first-error`, which returns the first matching line of this run instead of
   the whole file.
4. If the command itself returned an `observation_*` code, it is a fact about
   this process, not a service exit reason. Follow the observation and
   sandbox section instead of the exit table.
5. Fix the declared input, repeat the operation, and refresh
   `status --json --brief`.

For a task that uses oberth-managed services, a running ad-hoc run, or explicitly
related worktrees, read `oberth attn status --json` once at task entry. This reads
local consent, not the provider. If `enabled` is true, attach the existing
assessment to this task without waiting for the person to say “continuous
attention”. First bind the exact worktree from `scope.root`, a short redacted
task summary, and a fixed evaluation allow-list. Follow
[references/attention.md](references/attention.md) for ownership, reuse,
compatibility, and cleanup. A docs-only edit or a task with no relevant runtime
does not need a watcher. Disabled or unavailable configuration stays fact-only;
do not change settings, test credentials, or create permission on the user's behalf.

The brief document deliberately omits `attn_path`. An attached runner reads the
full facts itself; do not add a full status read after every brief read merely
to make the model participate. No eligible event means no provider request.

For code changes, read the worktree-scoped Git summary as well:

```sh
oberth git files --json
oberth git diff --json --file path/to/file
```

Read the detailed guide only for the mode the task needs:

- Service start, stop, restart, logs, status reporting, a failed start, an
  observation or sandbox error, or worktree identity and cleanup:
  [references/operations.md](references/operations.md).
- Manifest drafting, adoption, `prepare:` / `prepare_inputs:`, `sources:`,
  `env_file:`, health checks, ports, and references such as `${worktree}`,
  `machine:`, or `workspace:` [references/manifest.md](references/manifest.md).
- What work has been done in this worktree, or which workplace new work belongs
  to: [references/workplace.md](references/workplace.md).
- Explicitly related worktrees or repositories:
  [references/cross-worktree.md](references/cross-worktree.md).
- `attn_path`, the optional assessment, human-in-the-loop, or quality feedback
  (optional):
  [references/attention.md](references/attention.md).
- Oberth itself got in the way. A command hung, a read was far slower than its
  work, the published facts could not tell two states apart, a hint did not
  match, or an observation code survived the documented next step. Then read
  [references/feedback.md](references/feedback.md).

## When oberth itself gets in the way

The loop above assumes the facts arrive. When they do not, say so to the person
first. Then, only if this installation agreed, file one improvement report
about the engine, not about the project:

```sh
oberth feedback status --json
oberth feedback report --kind stalled --command up --elapsed 3m --dry-run
```

A failure already explained by `exit_reason`, `services[].health.status`, or the
operation table is not a report. The fixed kinds, the flags, the note rule, and
the exact steps are in [references/feedback.md](references/feedback.md).

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
- A report is about oberth, not the project. Never put a path, service name, log
  line, command line, manifest field, environment value, or credential in a
  report note, and never enable reports on the person's behalf.
- Existing `enabled: true` permits task-scoped runtime assessment, not global
  monitoring. Attach once per relevant task, reuse only that task's own handle,
  and close it when the task ends or consent is disabled. Never execute a
  mutating recommendation without the existing explicit user choice.
- Refresh `oberth status --json --brief` after a control command, and the full
  `oberth status --json` before acting on a derived attention request.

The detailed guides are part of this skill's distribution. Read only the guide
needed for the current task; do not load all references by default.
