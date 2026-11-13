# option-berth skill

<p align="center">English · <a href="README.zh.md">简体中文</a></p>

This repository holds a guide for coding agents: read one worktree's declared
services and runtime facts, start them, find out why they are not running, and
leave the work behind for the next session.

It is one of three separate products. They meet only at the `oberth` CLI and
its `--json` contract:

| Product | Repository | What it does |
| --- | --- | --- |
| Engine | [SheathedSharp/option-berth](https://github.com/SheathedSharp/option-berth) | `oberth` declares and observes services, starts and stops them, and publishes facts that both people and agents can read. |
| macOS client | [SheathedSharp/option-berth-macos](https://github.com/SheathedSharp/option-berth-macos) | A native interface over the same facts. |
| Skill (this repository) | [SheathedSharp/option-berth-skill](https://github.com/SheathedSharp/option-berth-skill) | Teaches an agent to use those facts. |

The current version is **0.9.2**. Both READMEs ship with the skill, so this
number is the version of the copy you have.

## Install

The skill ships in this repository. The engine does not install it. Pick one
of the three methods. Keep one copy of `option-berth` in your skills directory.
The plugin copy is namespaced, so the two do not collide.

### Skills CLI

The Skills CLI supports Claude Code, Codex, Cursor, OpenCode, and any other
agent installed on this machine:

```sh
npx skills add SheathedSharp/option-berth-skill -g
```

`-g` installs at the user level. Leave it out to install into the current
project and share it through the repository. The installer detects the agents
already on this machine and symlinks them to one source copy by default. To pin
a commit, append `#<commit>` to the repository name, and `npx skills update`
then stays on that commit. The other `npx skills` commands on this page follow
the same rule: leave out `-g` for a project-level install.

### Claude Code plugin marketplace

```text
/plugin install option-berth --marketplace SheathedSharp/option-berth-skill
```

The marketplace name is `sheathedsharp`. On older Claude Code, run
`/plugin marketplace add SheathedSharp/option-berth-skill` first, then
`/plugin install option-berth@sheathedsharp`. The skill inside the plugin is
namespaced, so it does not collide with the copy in a skills directory.

### Clone and symlink

```sh
git clone https://github.com/SheathedSharp/option-berth-skill.git
mkdir -p ~/.claude/skills          # Claude Code shown; other agents differ
ln -sfn "$PWD/option-berth-skill" ~/.claude/skills/option-berth
```

To pin a version, run `git -C option-berth-skill checkout <commit>` before you
create the symlink. The clone is then on a detached HEAD, and `git pull`
refuses to run. Return to `main` with
`git -C option-berth-skill checkout main`. A copy instead of a symlink does not
update itself.

## Upgrade

| Install method | Is a new version available? | Upgrade |
| --- | --- | --- |
| Skills CLI | `npx skills check -g option-berth` checks without installing, and exits 1 when an update is available or the check fails | `npx skills update -g option-berth` |
| Claude Code plugin | The plugin marketplace has no check-only command | `claude plugin update option-berth@sheathedsharp`, or use the `/plugin` panel |
| Clone | `git -C <dir> fetch`, then `git -C <dir> status -sb` shows whether the clone is behind | `git -C <dir> pull --ff-only`. The symlink stays valid |

A clone pinned to a commit returns to `main` first with
`git -C <dir> checkout main`, then upgrades as the table says.

Which version is installed: when a copy sits in a skills directory,
`oberth doctor --only agent_skill --json` lists the path and version of each
copy in `detail`, and warns when the copies disagree. For a plugin, run
`claude plugin list`. The Skills CLI keeps no version of its own, and `check`
answers only whether an update exists.

The commands and fields in this skill follow the engine contract. The engine
does not know which copy is out of date, so it runs as usual: a changed command
or flag fails immediately, and a changed field reads as absent. On either
error, upgrade first, then look for another cause.

## Uninstall

| Install method | Uninstall |
| --- | --- |
| Skills CLI | `npx skills remove -g option-berth` |
| Claude Code plugin | `claude plugin uninstall option-berth@sheathedsharp`. To stop using this marketplace, run `/plugin marketplace remove sheathedsharp` |
| Clone | Delete the `~/.claude/skills/option-berth` symlink, then the clone directory |

The skill contains documentation and one agent interface declaration,
`agents/openai.yaml`. It installs no hooks and changes no agent configuration.
Uninstalling leaves `oberth.yaml`, runtime state, and project files untouched.

## Release

When the engine publishes a new contract, update three places in the same pull
request:

- `metadata.version` in `SKILL.md`
- `version` in `.claude-plugin/plugin.json`, which the marketplace reads to
  decide whether to push an update
- the current version at the top of `README.md` and `README.zh.md`

`scripts/check_skill_contract.py` in the engine repository takes anchors from
the CLI contract, the manifest schema, and the observation constants, then
checks that `SKILL.md` and `references/*.md` here cover them. Change the content
first, and the version second. A version bump alone does not pass the engine's
check.

## Contents

- [`SKILL.md`](SKILL.md) is the entry point: read the current worktree first,
  then open one reference for the task.
- `references/` holds one guide per task: service lifecycle and failure
  reasons, listener observation and sandboxes, manifest drafting and adoption,
  worktree identity and cleanup, the workplace record, and cross-worktree
  observation. The attention handoff is only for a choice a person has to make.
  `oberth feedback` has its own guide, with its fixed triggers and steps.

The contract lives in the engine repository:
[CLI](https://github.com/SheathedSharp/option-berth/blob/main/docs/cli.md),
[manifest](https://github.com/SheathedSharp/option-berth/blob/main/engine/docs/schema/manifest.schema.json),
[product](https://github.com/SheathedSharp/option-berth/blob/main/docs/product.md),
[workplace](https://github.com/SheathedSharp/option-berth/blob/main/docs/workplace.md).

## License

The license is MIT, the same as the engine. See [LICENSE](LICENSE).
