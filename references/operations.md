# Service operations

Use this guide after the initial `oberth status --json` when the task concerns
service lifecycle, status reporting, or a start that failed. It is the default
guide for "start it and tell me why it is not running".

## Core loop

1. Read `oberth status --json`: declared services, `running`, `port_actual`,
   `health_status`, `last_exit`, and the attributed listeners.
2. Run the operation:
   `oberth up --wait --json` for the project, `oberth up --only api,worker --json`
   for part of it, `oberth restart --only api --json` to re-apply the current
   manifest to one service, or `oberth down --json` to stop the project.
3. If it failed, match the evidence in the table below and read the log the
   reason names. Do not retry the same command without changing the input.
4. Fix the declared input, repeat the operation, and refresh `status --json`.
5. Report the worktree path and branch, declared services and states, attributed
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

## 失败原因与下一步

`status.worktree.services[]` publishes the evidence to branch on:
`last_exit.reason` (and its exit code), `health_status`, `log_path`, and
`manifest_runtime_mismatch`. Read those fields before choosing a next step.

| Evidence | Meaning | Next step |
|---|---|---|
| `start_failed` | The command could not be started (missing executable, unusable cwd, or outside the home boundary). | Check `cmd` and `cwd`. There is no process log because no process ran. For `outside_home`, pass `--allow-outside-home` only when the person asks; otherwise report the refusal and its hint. |
| `crashed` (non-zero exit) | The process ran and exited; the cause is in its output. | `oberth logs <service> --once --json`, fix the generated file, data, or command it names, then `up` again. |
| `port_occupied` | The declared fixed port is owned by another process. | Do not kill an unrelated process and do not edit `oberth.yaml` to dodge it. Report the port, the listener evidence, and let the person decide whether to free the port or change the manifest. |
| `ready_timeout` | The process started but did not listen or pass `health:` before the deadline. | Read its log; check the bind address, port, and health path. Fix the input, then `restart --only <service>`. An already-running instance is not stopped by this timeout. |
| `dependency_not_ready` / `dependency_timeout` | A declared `depends_on` dependency did not resolve or become ready. | Read the **dependency's** log (`oberth logs <dependency> --once --json`), fix the dependency first, then `up` the dependent. The failure hint names the dependency. |
| `stopped` / `exited` (code 0) | Normal stop or clean exit, not a failure. | Report the state; do not "recover" it. |
| `health_status: fail` (with `code`/`reason`) | A listener exists but the declared health probe failed. | Read the log; check the `health:` path and the app's route; fix it and `restart --only <service>`. |
| `manifest_runtime_mismatch: true` | The running process predates the current manifest. | `oberth restart --only <service>`. Do not kill by PID. |
| `machine:` entry `listening: false` | A read-only dependency is not listening. | Report the fact. `up`/`down` never operate `machine:` entries. If no declared service `depends_on` it, stop here; there is nothing to hand off. |
| `outside_home` | The worktree is outside `HOME` and was not allowed. | Ask the person; `--allow-outside-home` is their decision, not a default fix. |

Rules for using the table:

- Match the **current** run. An old exit record left by `down` is not evidence
  that this `up` failed.
- When the reason names a dependency, read the dependency's log. The dependent
  may have no log because it never started.
- Do not edit `oberth.yaml` to work around a failure. Drafting and adoption are
  a human choice; see [manifest.md](manifest.md).
- Do not kill by PID or port unless it is this project's own service and `down`
  failed. A named `kill` still needs the existing approval boundary.
- After a fix, use `up --wait`, refresh status, and report the observed facts
  rather than "it should work now".
