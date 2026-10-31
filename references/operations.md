# Service operations

Use this guide after the initial `oberth status --json` when the task concerns
service lifecycle, status reporting, or a start that failed. It is the default
guide for "start it and tell me why it is not running".

## Core loop

1. Read `oberth status --json`: declared services, `running`, `port_actual`,
   `health_status`, `last_exit`, `code_changed_since_start`, the attributed
   listeners, and the top-level `observation`. For a large stack,
   `status --json --brief` keeps the runtime facts (including the code-change
   fields) and drops manifest copies, git history and the change ledger;
   `--only api,worker` also narrows which services are read and hashed.
2. Run the operation:
   `oberth up --wait --json` for the project, `oberth up --only api,worker --json`
   for part of it, `oberth restart --only api --json` to re-apply the current
   manifest to one service, or `oberth down --json` to stop the project.
3. If it failed, match the evidence in the table below and read the log the
   reason names. Do not retry the same command without changing the input.
4. If the error code starts with `observation_`, stop and use
   [Observation and agent sandboxes](#observation-and-agent-sandboxes). That is
   a limitation of this process, not a service failure and not a reason to
   change the manifest.
5. Fix the declared input, repeat the operation, and refresh `status --json`.
6. Report the worktree path and branch, declared services and states, attributed
   runtime facts, the last failure evidence, and the next bounded command.

Use `up --wait` (or `--ready`) when readiness matters. It waits for listeners
and configured health checks; a portless worker is ready when its run is active.
Use `--force` only when a graceful stop failed and the person asked for it.
Use `logs --follow` for a live log stream. A port is accepted for scripts, but
an ambiguous listener must be narrowed with `--ip ADDRESS`.

Use `oberth kill` only for a named port or PID, or for the explicitly requested
all-listener exception. It is not a replacement for `down`.

Keep facts separate from guesses. A missing or ambiguous service/port result is
actionable output; it is not permission to scan the whole machine.

`oberth start -- <command>` expands `${<name>.port}`, `${<name>.url}`, and
`${worktree}` in its arguments from this worktree's address book (services,
`machine:`, and `workspace:`), using the actual port for `port: auto`. A
declared but currently unaddressable reference fails the command instead of
passing `${...}` through. Bare `${port}` / `${url}` expand only with `--port`.
Use `up` for manifest services; `start` is the explicit single-command entry.

## Worktree identity and cleanup

`status --json` publishes `worktree.identity`, the same value `${worktree}`
expands to. Use it to name per-worktree data (`app_<identity>`,
`.data/<identity>`).

`oberth worktrees [--gone] --json` is a read-only identity ledger. Each row has
`identity`, `root`, `group`, `exists`, and `last_seen`. It is not a runtime fact:
rows remain after a checkout is deleted or moved, and `exists` is re-checked
from the filesystem on every read. `--gone` keeps only checkouts that no longer
exist.

- It never deletes ledger rows, databases, data directories, or running
  processes. Deleting a worktree's data is the person's action.
- Without a daemon or before any identity is recorded, it returns an empty list;
  it does not start a daemon or create a database.
- To stop services whose checkout is gone, use
  `oberth down --identity <wt_…>`. The value comes from `worktree.identity` or
  `oberth worktrees`. `down --worktree PATH` does the same while the directory
  exists. Neither can be combined with a project name or manifest path.
- An unknown identity is `not_found`. An explicit identity with nothing to stop
  is a successful empty stop, not an error.
- A project name is a group scope. If two checkouts share a group name,
  `down <project>` and an explicit identity return `ambiguous`; use `kill` by
  port or PID instead of guessing which one to stop.

## Failure reasons and next steps

`status.worktree.services[]` publishes the evidence to branch on:
`last_exit.reason` (and its exit code), `last_exit.port_hint` /
`last_exit.port_holder` for a port conflict, `health_status` (with `status`,
`code`, `reason`, `observed_at`), `log_path`, `manifest_runtime_mismatch`, and
`code_changed_since_start` (with `code_changed_files` and `code_hint`). Read
those fields before choosing a next step.

| Evidence | Meaning | Next step |
|---|---|---|
| `start_failed` | The command could not be started (missing executable, unusable cwd, or outside the home boundary). | Check `cmd` and `cwd`. There is no process log because no process ran. For `outside_home`, pass `--allow-outside-home` only when the person asks; otherwise report the refusal and its hint. |
| `crashed` (non-zero exit) | The process ran and exited; the cause is in its output. | `oberth logs <service> --once --json`, fix the generated file, data, or command it names, then `up` again. |
| `port_occupied` | The declared fixed port is owned by another process. `last_exit.port_holder` names the process observed at read time. | Do not kill an unrelated process and do not edit `oberth.yaml` to dodge it. Report the port, `last_exit.port_holder`, and let the person decide whether to free the port or change the manifest. |
| `ready_timeout` | The process started but did not listen or pass `health:` before the deadline. | Read its log; check the bind address, port, and health declaration. Fix the input, then `restart --only <service>`. An already-running instance is not stopped by this timeout. |
| `dependency_not_ready` / `dependency_timeout` | A declared `depends_on` dependency did not resolve or become ready. | Read the **dependency's** log (`oberth logs <dependency> --once --json`), fix the dependency first, then `up` the dependent. The failure hint names the dependency. |
| `stopped` / `exited` (code 0) | Normal stop or clean exit, not a failure. | Report the state; do not "recover" it. |
| `health_status: fail` (with `code`/`reason`) | A listener exists but the declared health probe failed. | Read the log; for an HTTP path check the route, for `{tcp: port}` confirm the port matches the declared `port`, for `{command: ...}` run that command in the service cwd and read `reason`. Fix it and `restart --only <service>`. |
| `manifest_runtime_mismatch: true` | The running process predates the current manifest. | `oberth restart --only <service>`. Do not kill by PID. |
| `code_changed_since_start: true` | The source under `sources:` changed after this run started, so the process is still executing older code. `code_changed_files` is the count when known; `code_hint` names the restart. | `oberth restart --only <service>`, then re-read status and confirm the field is `false` before trusting an unchanged HTTP result. A missing field is unknown, not "unchanged". |
| `machine:` entry `listening: false` | A read-only dependency is not listening. | Report the fact. `up`/`down` never operate `machine:` entries. If no declared service `depends_on` it, stop here; there is nothing to hand off. |
| `outside_home` | The worktree is outside `HOME` and was not allowed. | Ask the person; `--allow-outside-home` is their decision, not a default fix. |

Rules for using the table:

- Match the **current** run. An old exit record left by `down` is not evidence
  that this `up` failed.
- When the reason names a dependency, read the dependency's log. The dependent
  may have no log because it never started.
- An `observation_*` error is a **command** error, not a `last_exit.reason`.
  Do not look for it in this table and do not restart services to "fix" it.
- Do not edit `oberth.yaml` to work around a failure. Drafting and adoption are
  a human choice; see [manifest.md](manifest.md).
- Do not kill by PID or port unless it is this project's own service and `down`
  failed. A named `kill` still needs the existing approval boundary.
- After a fix, use `up --wait`, refresh status, and report the observed facts
  rather than "it should work now".

`last_exit.port_holder` has `port`, `pid`, `command`, and `kind`; a managed run
adds `group`, `name`, and `run_id`, and a readable row can add `cwd` and
`bind_address`. `kind` is `oberth_run` (started by option-berth, possibly in
another worktree), `previous_run` (an earlier generation of this service),
`worktree_listener` (attributed to a worktree without a managed run), or
`unknown`. It only covers the failed service's own port, not the machine's port
table. When the holder has released the port or cannot be observed, the field
is absent: that means "not observed at read time", not "the port is free".
`up --json` publishes the same `services[].port_holder` shape for a
`port_occupied` attempt.

`status --json` also publishes `exits[]`, the last five ended runs newest
first; it is history, not the current failure set. Use
`worktree.services[].last_exit` for the current facts. A failure record can
carry `exits[].hint`, the deterministic next step (the same hint as
`groups.start`), present only when a log file exists. `exits[].ports` lists
ports the ended run still held, so an exited run usually has an empty array.

`up --json` and `restart --json` publish `services[].ready` as a CLI
annotation, not a daemon fact. With `--wait`, it is `true` only after the
listener (and any declared `health:`) is confirmed; without waiting, a
`started` service carries `false`, and `skipped` / `failed` omit the field.
`restart` never waits, so its `started` services are always `ready: false`.
`false` means "readiness not confirmed", not failure: branch on `state` and
`reason`.

## Command errors

An error is a single object, `{"error":{"code":"...","message":"...","hint":"..."}}`;
diagnostics belong on stderr. Branch on `code`, not on the message text. The
stable codes are:

| Code | Meaning |
|---|---|
| `invalid_params` | A request or option is malformed. Fix the call; do not retry it unchanged. |
| `invalid_config` | The manifest or configuration could not be loaded. Read `detail`; it names the file and location. |
| `not_found` | The named worktree, service, port, or record does not exist. Do not widen the search to the whole machine. |
| `ambiguous` | The selector matched more than one target. Narrow it with a name, `--ip`, or a full id. |
| `permission_denied` | The operating system refused the action. Report it and the hint; do not retry blindly. |
| `timeout` | The operation did not finish in time. Refresh `status --json` before assuming it had no effect. |
| `daemon_busy` | Another writer holds the state. Refresh `status --json`, then retry once. |
| `internal` | An unexpected engine failure. Report `detail` and `hint`; do not translate it into a service failure. |
| `observation_empty` / `observation_unrecognized` / `observation_incomplete` / `observation_blind` / `observation_bind_denied` | This process cannot produce a trustworthy listener table. See the next section. |

An `observation_*` code is not a service `last_exit.reason` and not proof that
the manifest is wrong.

## Observation and agent sandboxes

`status --json` can publish a top-level `observation`:

~~~json
{"state":"bind_denied","code":"observation_bind_denied",
 "detail":"...","hint":"...","checked_at":"..."}
~~~

Read it before treating `ports` as complete. The fields mean:

| `observation.state` | Meaning | What to do |
|---|---|---|
| `observable` | The collector saw its own self-probe listener. | `ports` and `port_actual` are usable. |
| `partial` | Some rows were unreadable. The published rows are facts; unreadable ports are unknown. | Use the published rows. Do not fill in or assume the missing ports. |
| `blind` | The process can bind a port but cannot see its own listener. | An empty listener list is not evidence that nothing runs. Move the check outside the sandbox. |
| `bind_denied` | The process cannot bind a local port at all. | Services started from this process cannot listen either. Move the check outside the sandbox. |

The matching stable error codes appear in command errors, `up --wait`, `logs`,
and `doctor`:

| Code | Meaning | Bounded next step |
|---|---|---|
| `observation_empty` | The collector exited 0 but printed no listening table. The self-probe decides whether this is an empty machine or a blind process. | Run `oberth doctor --only listener_observation`; if it is blind, retry outside the sandbox. |
| `observation_unrecognized` | The output had no table header this build recognizes. This is a format/version problem. | Upgrade option-berth, or report the header line. A sandbox change is not the first fix. |
| `observation_incomplete` | Some output rows could not be decoded. Readable rows are published and `observation.state` is `partial`; unreadable ports stay unknown. If the command could not finish at all, it still fails. | Keep the readable rows, do not treat missing ports as free, and retry outside the sandbox if `doctor` agrees. |
| `observation_blind` | The self-probe can bind a local port but cannot see its own listener. | Retry outside the sandbox or run `doctor --only listener_observation`. Never conclude "nothing is running". |
| `observation_bind_denied` | The self-probe cannot bind a local port. | Retry outside the sandbox or allow option-berth's network access. Do not start services from here. |

A coding-agent sandbox is the usual source of `observation_bind_denied`
(Codex's seatbelt, Claude Code's sandbox, Cursor's `--sandbox`) and can also
produce `blind` or `empty`. In that situation:

- `status` still exits 0 with the declaration, service runs, log paths, and
  recent exits. `ports` is empty and `port_actual` is `null`; that is a partial
  answer, not a failure to read the project. Say what you know and what you
  cannot confirm.
- `up --wait` returns the observation error immediately and keeps the run it
  just started. It does not wait for the full timeout and then stop it.
- Write commands that would auto-start a daemon run the self-probe first and
  refuse to create a daemon from a blind process. The hint names
  `oberth serve --detach`; that command belongs in a normal terminal, not in
  the sandbox. Do not start a daemon from the sandbox yourself.
- `logs <service>` still reads the managed run's registered `log_path`; it does
  not depend on the listener table.
- `--no-daemon` makes read commands collect locally. It does not make a
  sandbox able to see listeners.
- `oberth doctor --only listener_observation` binds a real local port and
  reports `observable`, `blind`, or `bind_denied` with the same collector. CLI
  mode also checks the daemon's own observation.
- Do not parse `internal`, do not retry the identical command, and do not ask
  the person to run the whole task again inside the sandbox. The code and hint
  are the contract; the next step is outside the sandbox.
