# Manifest governance

Use this guide when a worktree has no `oberth.yaml`, when a person asks for help
changing one, or when a failure points at how a service is declared.

## What the manifest controls

Top-level keys:

| Field | Meaning |
|---|---|
| `name` | The project name `oberth` knows this worktree by. Defaults to the directory name. |
| `services` | The services `oberth up` starts and `oberth down` stops. |
| `machine` | Services the machine already runs (a database, middleware). Each entry has `name` and `port`. Read-only references: `up`/`down` never start or stop them. |
| `workspace` | Services in another checkout, addressed read-only. Each entry has `name`, `worktree`, and `service`. `up`/`down`/`restart` never start or stop the other checkout. |
| `ports` | Extra fixed ports this project claims beyond its services. |
| `worktree_ports` | How many auto ports a linked-worktree claim takes by default. |
| `$schema` | Optional JSON Schema URL for editor completion. It is metadata, not a service. |

Each entry in `services`:

| Field | Meaning | Failure it explains |
|---|---|---|
| `name` | Short name, unique in this file. | `not_found`, `ambiguous` when a selector is unclear. |
| `cmd` | The long-lived process, run in the service directory (`cwd`). | `start_failed`, `crashed`. |
| `cwd` | Working directory, relative to the directory holding `oberth.yaml`. | `start_failed` when it is unusable. |
| `prepare` | A command that runs before `cmd` on `up` and `restart`; its failure prevents the long-lived start. Use it when the artifact must be rebuilt from this checkout (a jar, generated config, code generation). | A prepare failure; a stale or missing generated artifact. |
| `prepare_inputs` | Files the prepare command reads, relative to `cwd`. When their contents are unchanged, `up` skips prepare. | A prepare that reruns unnecessarily, or a stale result when the inputs are not declared. |
| `port` | A fixed number from 1–65535, or `auto`. `status` reports the running address as `port_actual`. | `port_occupied`; an auto port that is not yet assigned. |
| `health` | An HTTP path, `{tcp: port}`, or `{command: ...}`. `up --wait` and dependency waits use it. | `health_status: fail`, `ready_timeout`, and a dependency that never becomes ready. |
| `depends_on` | Declared services that must be started first; a portless dependency is ready when its run is active, a ported one when it listens (and is healthy when declared). | `dependency_not_ready`, `dependency_timeout`. |
| `env` | Environment added when option-berth starts the service. Values may use the references below. | A service that starts with the wrong configuration. |
| `env_file` | A dotenv-style file read before `prepare` and `cmd`; relative to the manifest directory. Its contents do not enter `status`, logs, or `spec_hash`. | A service that cannot start because the file is missing or malformed. |
| `description`, `icon`, `color` | User-authored metadata shown by clients; they do not change runtime behavior. | Nothing. |

`port: auto` is assigned by the daemon. `restart --only` keeps that reservation
so the service comes back on the same address; `down` releases it only after the
stop is confirmed.

## Health checks

`health` has three forms:

```yaml
health: /healthz                    # HTTP path, the default form
health: {http: /healthz}            # the same check in object form
health: {tcp: 5432}                 # TCP connect
health: {command: pg_isready -h 127.0.0.1 -p ${port}}
```

- An HTTP path must start with `/`.
- `{tcp: port}` connects to that port. The port must match the service's
  declared `port`; use this for a raw TCP service.
- `{command: ...}` runs in the service `cwd`, split into argv the same way as
  `cmd:` (no shell), and exit code 0 is healthy. It supports `${port}`, `${url}`,
  `${<name>.port}`, and `${worktree}`. Use it when the port opens before the
  protocol is ready (databases) or when readiness needs a real client.
- An object form has exactly one of `http`, `tcp`, or `command`.
- HTTP and TCP only prove the port is reachable. They do not prove the protocol
  behind it is ready.
- The same health fact feeds `up --wait`, dependency waits, `status`
  (`health_status`), and attention. A command-form check does not require the
  service itself to listen.

## References

`prepare:`, `cmd:`, and `env:` may reference ports and the checkout identity.
A command-form `health:` supports `${port}`, `${url}`, `${<name>.port}`, and
`${worktree}`, but not `${<name>.url}` and not a `workspace:` address. The
daemon expands them before starting the service:

| Reference | Expands to |
|---|---|
| `${port}` / `${url}` | This service's own port / `http://localhost:<port>` |
| `${<name>.port}` / `${<name>.url}` | A service in this manifest, a `machine:` reference, or a `workspace:` reference |
| `${worktree}` | This checkout's stable identity, shaped like `wt_0123456789ab` |

- `<name>` is looked up first in `services:`, then in `machine:`, then in
  `workspace:`. A service, machine entry, and workspace entry cannot share a
  name.
- Only these shapes are references. Other `${...}` text (for example `${HOME}`
  or `${FOO:-x}`) is left unchanged for the command.
- A reference to an undeclared name, or a port reference to a service without a
  port, is rejected by manifest validation instead of being passed through.
- `${worktree}` is derived from the normalized root path of the checkout that
  holds the manifest. The same worktree gets the same value on every start;
  the main checkout and every linked worktree get different values. It is an
  identifier, not a path: use it in a database name (`app_${worktree}`) or a
  relative data directory (`.data/${worktree}`).
- The current value is published as `worktree.identity` in `status --json`.
  `oberth worktrees` lists the identities this daemon has seen. Use those
  values when connecting a database or finding old data; the engine does not
  delete data.
- Moving a checkout produces a new identity; old data is not moved. `${worktree}`
  does not point at a service and does not create or need a `depends_on` entry.
  `down` only stops this worktree's services; it never deletes data.
- `oberth start -- <command>` expands `${<name>.port}`, `${<name>.url}`, and
  `${worktree}` in its arguments before execution. A declared but currently
  unaddressable reference fails the command; `${...}` is not passed through
  literally. Bare `${port}` / `${url}` expand only when `--port` is given.

## Shared environment files

`env_file:` points at a dotenv-style file. A relative path is resolved against
the directory holding `oberth.yaml`, so `../shared/dev.env` can live outside the
checkout and serve several worktrees:

```yaml
env_file: ../shared/dev.env
```

- It is read before `prepare:` and before the long-lived `cmd:`.
- Blank lines and lines starting with `#` are ignored. An optional `export `
  prefix is accepted. Single-quoted values are literal; double-quoted values
  support `\n`, `\r`, `\t`, `\\`, and `\"`.
- Values are not interpolated: `${...}` stays literal.
- Environment precedence, low to high: the daemon's own environment, the
  caller's environment, `env_file`, `PORT`, the service's own `env:`.
- A missing file, a non-regular file, or a malformed line fails the service
  start. The error names the file and line and does not print values.
- The contents do not enter `status`, logs, or `spec_hash`. Changing the file
  does not require a daemon restart, but a running service must restart to read
  it. option-berth never creates or modifies the file; secrets belong here, not
  in the manifest.

## Cross-worktree address references

`workspace:` lists services in another checkout. It only provides addresses; it
does not participate in start or stop:

```yaml
workspace:
  - name: backend
    worktree: ../backend
    service: api
```

- `worktree` is the other checkout's root (relative to the manifest directory
  or absolute), or its manifest file. `service` is a service name in that
  manifest.
- `prepare:`, `cmd:`, and `env:` can then use `${backend.port}` /
  `${backend.url}`.
- Resolution reads the other manifest and the daemon's published runtime facts:
  a running service uses its actual port (including `port: auto`); a stopped
  service with a fixed port uses the declared address; `port: auto` without a
  running service is unaddressable and the referencing service fails to start
  with the reason.
- `up`, `down`, and `restart` never start or stop the other checkout and do not
  create a `depends_on` relation. A `workspace:` name cannot collide with a
  service or `machine:` name.
- Health checks do not accept `workspace:` references.
- `workspace:` in `oberth.yaml` is not the `--workspace` label on
  `oberth events`; that label is an ephemeral subscription relation. Do not
  infer one from the other.

## `prepare_inputs` and the prepare cache

`prepare_inputs` lists the files the `prepare` command reads, relative to the
service `cwd`:

```yaml
prepare: npm ci
prepare_inputs: [package.json, package-lock.json]
```

- `up` runs `prepare` and only starts `cmd` after it succeeds.
- The fingerprint is recorded only after a successful prepare. The next `up`
  skips prepare when those files still have the same contents.
- Missing or unreadable inputs always rerun prepare. A failed prepare never
  records a fingerprint.
- The cache lives under `$BERTH_HOME/prepare`. Deleting it only makes the next
  start slower; it is not a source of truth about the service.

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

## Schema and strict parsing

The JSON Schema is published at
[`engine/docs/schema/manifest.schema.json`](https://github.com/SheathedSharp/option-berth/blob/main/engine/docs/schema/manifest.schema.json).
It is generated from the Go declaration types; do not edit it by hand.

- The schema rejects unknown keys, except top-level `x-` extensions and
  `$schema`. A key inside `services[]` or a service object is checked against
  that object; extra keys there are errors.
- `port` accepts only 1–65535 or `auto`.
- `oberth init` and `oberth init draft` write a modeline as the first line:
  `# yaml-language-server: $schema=...`. Editors use it to flag misspelled keys
  before a draft is adopted. A hand-written manifest may add the same line.
- The default parser still ignores unknown keys for compatibility. Set
  `BERTH_STRICT_MANIFEST=1` (also `true`, `yes`, `on`) to turn them into load
  errors with file, line, and column. It applies to every manifest read path:
  the CLI, the daemon, and `oberth init adopt`. Top-level `x-` and `$schema`
  remain valid.
- `doctor --only project_config` reports ignored keys as warnings with their
  location in the default mode. It does not print field values and does not
  rewrite the manifest.
- `oberth.yaml` accepts exactly one YAML document. A second document, including
  an empty one, is an error. Declaring `port` twice for one service, including
  `auto` mixed with a number, is an error with a YAML line number.

## Common diagnosis

- **Missing generated file.** Run the documented generator if the repository
  has one. A `prepare:` entry belongs in a draft for the person to adopt, not in
  a file the agent writes itself. Add `prepare_inputs:` for the files it reads,
  so the next `up` can skip an unchanged prepare.
- **Port occupied.** This is a process conflict, not a manifest typo. Do not
  change the port to hide it, and do not kill the other process. Report the
  evidence and let the person decide.
- **Dependency not ready.** Fix the dependency; do not remove or reorder
  `depends_on` to make the dependent start. If the dependency declares a
  command-form health check, its readiness may be protocol-level, not just the
  port.
- **Running process predates the manifest.** `restart --only <service>`; do not
  edit the manifest back to match the old process. `manifest_runtime_mismatch`
  is the signal.
- **Shared env file missing or malformed.** Read the error's file and line; it
  does not print values. The person owns that file: fix its path or content, and
  do not inline secrets into `oberth.yaml`.
- **Workspace address unresolved.** Check the other checkout's manifest and
  whether its service is running. `port: auto` without a running service cannot
  be addressed; start that service or give it a fixed port. Do not add a
  `depends_on` relation or copy the other address into this manifest.
- **Unreferenced `machine:` entry.** Its `listening` value is the whole story.
  It has no start/stop operation and does not need a handoff.
- **An `observation_*` error, not a manifest problem.** The manifest was read
  successfully; this process cannot see listeners. Do not change the manifest
  or restart services. See [operations.md](operations.md).
