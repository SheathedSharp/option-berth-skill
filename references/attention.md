# Attention handoff (optional)

This guide is optional. Do not read it by default after `oberth status --json`,
and do not treat `attn_path` as a required step in the service loop. Open
it only when:

- the task explicitly asks about the assessment, human-in-the-loop handling, or
  quality feedback; or
- a current anomaly blocks the task and a person must choose among the fixed
  options.

Do not use it for a routine failure already explained by
[operations.md](operations.md) (`start_failed`, `crashed`, `port_occupied`,
`ready_timeout`, `dependency_not_ready`), for an unreferenced `machine:` entry
that no declared service `depends_on`, for a normally stopped service, or on
every status read merely because `attn_path` exists.

The complete adapter contract is in
[`docs/agent/attn-adapter.md`](https://github.com/SheathedSharp/option-berth/blob/main/docs/agent/attn-adapter.md).

## Verify before acting

Read the exact path from the current status. Do not scan `BERTH_HOME`. Refresh
status before acting and verify that the artifact's worktree, state revision,
and freshness marker still match. A missing, malformed, stale, or mismatched
artifact is not actionable.

`event` and `evidence` are code-produced facts. `assessment` is an optional
model recommendation. It is never a fact, diagnosis, command, permission, or new
option. Map recommendations only to the fixed option IDs present in the
artifact's `options` and preserve the existing human approval boundary for
`up`, `restart`, `down`, and manifest adoption.

If an option is needed, present one short choice with the event, evidence, and
bounded next steps. After the person chooses, run only the documented command,
report its result, and read status again. A low-confidence, stale, conflicting,
or context-only handoff goes back to the person.

## Task-scoped runner (only when asked)

Arm a session only when the person asks for continuous attention on a
long-running task or while coordinating concurrent worktrees. For a one-shot
start, diagnose, fix, and confirm, use the service loop in
[operations.md](operations.md) and stop. Do not create a task context or arm a
session.

The session owns its poller and is stopped when the task ends. Nothing on the
machine creates the task context. You do. It is your own statement of what this
task is and which of the fixed options it may present. For a short task, pass it
inline:

```sh
oberth attn assess --follow --project "$PWD" \
  --task "keep the API healthy while the integration test runs" \
  --authorize inspect_logs,inspect_port,restart_service,continue_without_action,ask_user_for_context
```

For the complete fixed vocabulary, write a file and pass it. Choose a path
unique to this task. Two parallel agents that share one path overwrite each
other.

```sh
cat > "${TMPDIR:-/tmp}/oberth-task-$$.json" <<'JSON'
{
  "task": "keep the API and worker healthy while running the integration test",
  "authorized_options": [
    "inspect_logs", "inspect_port", "inspect_dependency", "inspect_manifest",
    "restart_service", "start_service", "stop_service", "adopt_manifest",
    "continue_without_action", "ask_user_for_context"
  ]
}
JSON
oberth attn assess --follow --project "$PWD" --task-context "${TMPDIR:-/tmp}/oberth-task-$$.json"
```

`--task` and `--authorize` override the same fields from the file. With neither
a task nor an allow-list, the runner stops with `--task or --task-context is
required` or `--authorize (or authorized_options) is required`. It does not
guess an allow-list.

`authorized_options` is an allow-list for the current task, not user approval.
Side effects still require an explicit user choice. `oberth attn assess --follow`
is the long-lived form of the one-shot `oberth attn assess`. The runner reads
`$BERTH_HOME/attn.json` (default `~/.option-berth/attn.json`). A copy there with
`enabled: false` keeps the session fact-only and prevents a remote call. Under an
isolated `BERTH_HOME`, the default home file is not the one being read.

For a task that remains active while services run, use the agent-side
subscription instead of rebuilding the request repeatedly:

```sh
oberth attn assess --follow --project "$PWD" --interval 2s \
  --task-context "${TMPDIR:-/tmp}/oberth-task-$$.json"
```

The runner polls the existing CLI contract. It does not add a daemon watcher,
hook, MCP server, model call to the core engine, or an automatic action path. It
calls the provider only for a new event or revision, or an uncached assessment.
Normal polls are recorded as no-event observations.

## Quality feedback

The runner may write its redacted ledger to
`$BERTH_HOME/quality/events.ndjson`. Keep it local. Do not copy it into the
repository or send it to a provider. When recording feedback, include only the
event identity, revision, fixed enums, and outcome. Never include task text,
logs, commands, absolute paths, credentials, or free-form model output.

Use `oberth attn status --json --since 0` to inspect local results. A `null`
metric means there are too few labeled cases. Read `labeled_cases`,
`unlabeled_cases`, and `label_coverage` before interpreting a score. The
`sessions` object explains whether a quiet ledger came from an armed session
with no events, or from no session at all.

The runner's fixed vocabulary, preflight rules, settings, and exact feedback
schema are maintained in `docs/agent/attn-adapter.md`. Read that document before
you change or evaluate those interfaces.
