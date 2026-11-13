# Reporting an improvement (optional)

`oberth feedback` files a report about **oberth itself**, not about the project
you are working in. It is opt-in: `oberth feedback status --json` answers
whether this installation agreed. When `enabled` is false, send nothing and do
not ask the person to turn it on; mention it only if they ask why nothing was
filed.

## When it is worth a report

File one only when oberth itself got in the way in one of these fixed ways. The
contract already answers a normal service failure: `crashed`, `start_failed`,
`port_occupied`, `ready_timeout`, `dependency_not_ready`. Do not report one.

| kind | File it when |
|---|---|
| `slow` | A command took many times longer than the work it describes: `status --json --brief` with no answer for tens of seconds, or `up --wait` spending its whole budget on a service whose command is trivial. |
| `stalled` | A command produced no output and no progress, and you had to cancel it; nothing in the published facts said why. |
| `coarse` | The published facts could not tell two states apart that the task needed: a `started` service with `ready: false` and no hint, an exit with no `reason`, an empty log with no explanation. |
| `misleading` | A published fact or hint contradicted what actually happened: the named log line does not exist, `listening: true` with nothing bound, a hint pointing at a command that fails the same way. |
| `observation` | An `observation_*` code appeared in an ordinary terminal (not a sandbox), and the documented next step did not resolve it. |
| `other` | Something else cost a round trip and is not covered above. |

## What to send

~~~sh
oberth feedback report --kind stalled --command up \
  --error-code observation_blind --observation blind \
  --elapsed 3m --services 4 --note "up --wait returned no facts for three minutes"
~~~

- `--kind` from the table above.
- `--command` the oberth command involved.
- `--error-code` only when the command returned one: copy `code` from the JSON
  error on stderr.
- `--observation` only when you have read `observation.state`:
  `observable`, `partial`, `blind`, or `bind_denied`.
- `--elapsed` the wall clock you measured, such as `45s` or `3m`. The engine
  files a bucket, not the number.
- `--services` the number of services the manifest declares, when you know it.
- `--note` one or two sentences in your own words: what you expected and what
  happened.

Never put a project name, path, service name, log line, command line, manifest
field, environment value, or credential into `--note`. Redaction covers paths,
addresses, logins, and secrets. It is a fallback, not permission to include
them.

## The steps

1. Read the current decision:

   ~~~sh
   oberth feedback status --json
   ~~~

2. Compose and preview without sending:

   ~~~sh
   oberth feedback report --kind stalled --command up --elapsed 3m --dry-run
   ~~~

3. Show the person the note and ask before it leaves the machine. Send with
   `--yes` only after they agreed: without it, a free-text report is refused on
   a non-terminal.
4. Report the outcome to the person: a filed issue URL, or the prefilled
   `issues/new` link when `gh` is not signed in. Do not ask them to install
   `gh`; the link path is the supported fallback.
5. File at most one report per problem in a session. The engine already refuses
   the same complaint from the same build for 24 hours, and caps an
   installation at five reports a day; do not work around either.

## Boundaries

- A report is about the engine, not the project. It never replaces `oberth
  doctor`, reading the log, or fixing the manifest.
- Do not enable reports on the person's behalf. `oberth feedback on` is their
  decision, not yours.
- Do not file in a loop, and do not use a report instead of telling the person
  that the task is blocked.
