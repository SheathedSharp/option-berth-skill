# Manifest governance

Use this guide when a worktree has no `oberth.yaml`, when a person asks for help
changing one, or when a failure points at how a service is declared.

## What the manifest controls

| Field | Meaning | Failure it explains |
|---|---|---|
| `cmd` | The long-lived process, run in the service directory. | `start_failed`, `crashed`. |
| `prepare` | A command that runs before `cmd` on `up` and `restart`; its failure prevents the long-lived start. Use it when the artifact must be rebuilt from this checkout (a jar, generated config, code generation). | A prepare failure; a stale or missing generated artifact. |
| `port` | A fixed number, or `auto`. `status` reports the running address as `port_actual`. | `port_occupied`; an auto port that is not yet assigned. |
| `health` | An HTTP path that must return a healthy response. `up --wait` waits for it. | `health_status: fail`, `ready_timeout`, and a dependency that never becomes ready. |
| `depends_on` | Declared services that must be started first; a portless dependency is ready when its run is active, a ported one when it listens (and is healthy when declared). | `dependency_not_ready`, `dependency_timeout`. |
| `machine:` | Services this project reads but does not start (a database or middleware). It has no `cmd`; `up`/`down` never touch it. | Only `listening: false`; it is not a project failure. |

`port: auto` is assigned by the daemon. `restart --only` keeps that reservation
so the service comes back on the same address; `down` releases it only after the
stop is confirmed.

## Draft and adopt

Preview a starter without writing it:

```sh
oberth init --dry-run
```

If a person asks the local agent to draft a manifest, use `oberth init draft`
and show the result. Adoption is a separate human decision:

```sh
oberth init adopt
oberth init adopt --replace
oberth init adopt --merge
```

Use `--replace` or `--merge` only after the person chooses that write. Do not
edit `oberth.yaml`, invent a service command, install hooks/MCP, or adopt a
draft on the agent's own authority.

A `prepare` command must rebuild the current checkout before the long-lived
`cmd`; never rely on a stale artifact. Add it only when the person adopts it.

## Common diagnosis

- **Missing generated file.** Run the documented generator if the repository
  has one. A `prepare:` entry belongs in a draft for the person to adopt, not in
  a file the agent writes itself.
- **Port occupied.** This is a process conflict, not a manifest typo. Do not
  change the port to hide it, and do not kill the other process. Report the
  evidence and let the person decide.
- **Dependency not ready.** Fix the dependency; do not remove or reorder
  `depends_on` to make the dependent start.
- **Running process predates the manifest.** `restart --only <service>`; do not
  edit the manifest back to match the old process.
- **Unreferenced `machine:` entry.** Its `listening` value is the whole story.
  It has no start/stop operation and does not need a handoff.
