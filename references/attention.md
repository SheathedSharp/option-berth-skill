# Attention handoff (optional)

Use this guide when entering an oberth-related runtime task, when a deterministic
anomaly needs assessment, or when explaining local quality data. It does not
turn an unrelated coding task into a background monitoring job.

At task entry read `oberth attn status --json` once. `enabled` means permission
to assess this task's bounded runtime events, not that a runner is already
observing. Do not ask the person to repeat a special “continuous attention”
phrase when this permission is already enabled. If off, missing configuration,
or unavailable, continue the ordinary fact-only service loop and explain the
fixed reason once; do not enable, reconfigure, or probe credentials.

Capture `scope.root` from the current runtime status as the canonical project.
Use a one-sentence task summary with no source code, raw logs, paths, secrets,
or copied conversation. Start with read-only evaluation options:
`inspect_logs`, `inspect_port`, `inspect_dependency`, `inspect_manifest`,
`continue_without_action`, and `ask_user_for_context`. Add mutating candidate
options only when relevant to this task; they remain suggestions and still
require the person's explicit choice before execution.

Do not assess a normally stopped service, an unrelated listener, an unreferenced
`machine:` dependency, or an unrelated task. When a routine failure has a clear
deterministic next step, perform the already-authorized inspection and refresh
facts instead of buying an assessment merely to increase call counts.

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

## Task-scoped runner and ownership

For a relevant task that continues while services run, attach one task-owned
`assess --follow` session after the local consent check. For a short task or a
single decision, use one-shot `assess` with the same explicit scope and options;
there is no need to leave a poller behind. The runner itself does not call the
provider when no eligible anomaly is present.

Compatibility: automatic long-lived attachment requires the engine's
`quality.activity` field in the local attn status. If it is absent, use bounded
one-shot assessment with a fresh consent check before each attempt; do not
assume an older runner stops when settings change. Report that limitation once.
No new command is required on the older engine.

Record the task's own background tool handle, canonical worktree, task context,
allow-list, and state directory. Reuse it only for this same task and scope; do
not start another after each status read. A historical `subscribed` row or a
fresh observation from another task is not ownership or permission to reuse it.
Do not share a context file across tasks or worktrees. Never copy credentials
into an isolated state directory to make it look enabled.

When the task finishes, is cancelled, changes scope, or the user disables
attention, cancel/join the owned tool session and remove only this task's
context file. The current runner also rechecks consent on every poll and exits
when it is revoked. Do not use broad process-name kills, port kills, or touch
another task's runner. If the agent cannot own and reliably close a background
handle, use one-shot assessment at meaningful boundaries instead.

The session owns its poller and is stopped when the task ends. Nothing on the
machine creates the task context. You do. It is your own statement of what this
task is and which of the fixed options it may present. For a short task, pass it
inline:

```sh
oberth attn assess --follow --project "$PWD" \
  --task "keep the API healthy while the integration test runs" \
  --authorize inspect_logs,inspect_port,inspect_dependency,inspect_manifest,continue_without_action,ask_user_for_context
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

The runner polls the existing CLI contract, rechecking enabled consent each time.
It does not add a daemon watcher,
hook, MCP server, model call to the core engine, or an automatic action path. It
calls the provider only for a new event or revision, or an uncached assessment.
Normal polls are recorded as no-event observations, not model calls. Output
NDJSON still emits only changes; local observation freshness and counters are
updated even when an unchanged poll prints nothing.

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

## Reading quiet status correctly

`on` means assessment is permitted. Read `quality.activity` separately:
`no_session` means no observation is recorded in this home/window/filter;
`observing` means a completed poll has a short, unexpired observation lease;
`failed` means the last observation failed; `recent` means history exists but
there is no fresh lease. A lease is bounded evidence, not proof that a PID is
alive. Never infer active monitoring from a historical `subscribed` row.

`quality.model_calls` and `quality.cache_hits` include one-shot and active-task
observations without waiting for session exit. Lifecycle totals are not added
twice. Older session aggregates that cannot be allocated to a partial time
window are flagged with `legacy_counts_unallocated`; the displayed counters
are then lower bounds, not evidence of zero historical requests. Root-path
quality filters select the exact worktree identity; project labels intentionally
aggregate same-named directories. These are local observations, not a provider
billing statement or an API connectivity test.
