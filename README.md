# option-berth skill

给 coding agent 的 **option-berth 指引**：怎么读懂一个 worktree 的服务声明与运行事实、
把它跑起来、失败时看哪里，以及把这一轮工作留给下一个接手的人。

这是三个独立产品之一，只通过 CLI 与 `--json` 契约与另外两个相连：

| 产品 | 仓库 | 它做什么 |
| --- | --- | --- |
| 引擎 | [SheathedSharp/option-berth](https://github.com/SheathedSharp/option-berth) | `oberth`：声明、观察、起停服务，输出人和 agent 都能读的事实 |
| macOS 客户端 | [SheathedSharp/option-berth-macos](https://github.com/SheathedSharp/option-berth-macos) | 原生界面，呈现同一份事实 |
| **本仓库** | — | 教会 agent 使用上面这份事实 |

当前版本 **0.9.2**。这份 README 随 skill 一起分发，所以它开头的版本就是手上那份的版本。

## 安装

skill 随本仓库分发，引擎不会替你装。三种方式挑一种；散落目录里只留一份同名 skill，
插件那份带命名空间，不会和它混。

### Skills CLI

支持 Claude Code、Codex、Cursor、OpenCode 等本机已安装的 agent：

```sh
npx skills add SheathedSharp/option-berth-skill -g
```

`-g` 装到用户级，去掉 `-g` 则装进当前项目随仓库共享。安装器识别本机已有的 agent，
默认软链到一份规范副本。要固定到某个提交，在仓库名后加 `#<commit>`。固定之后
`npx skills update` 不会离开这个提交。本页后面的 `npx skills` 命令也一样，项目级安装时
去掉 `-g`。

### Claude Code 插件市场

```text
/plugin install option-berth --marketplace SheathedSharp/option-berth-skill
```

插件市场名是 `sheathedsharp`。旧版 Claude Code 先运行
`/plugin marketplace add SheathedSharp/option-berth-skill`，再运行
`/plugin install option-berth@sheathedsharp`。插件内的 skill 带命名空间，
不会和散落目录里的同名 skill 混淆。

### 手工克隆并软链

```sh
git clone https://github.com/SheathedSharp/option-berth-skill.git
mkdir -p ~/.claude/skills          # 以 Claude Code 为例；其他 agent 用各自的技能目录
ln -sfn "$PWD/option-berth-skill" ~/.claude/skills/option-berth
```

要固定版本，先 `git -C option-berth-skill checkout <commit>`，再建软链。这时 clone 处于
游离 HEAD，`git pull` 会拒绝执行；回到主线用 `git -C option-berth-skill checkout main`。
用复制代替软链时，这份副本不会自己更新。

## 升级

| 装法 | 有没有新版 | 升级 |
| --- | --- | --- |
| Skills CLI | `npx skills check -g option-berth`，只查不装，有更新或检查失败时退出码为 1 | `npx skills update -g option-berth` |
| Claude Code 插件 | 市场没有只查不装的命令 | `claude plugin update option-berth`，或在 `/plugin` 面板里操作 |
| 手工克隆 | `git -C <目录> fetch` 后用 `git -C <目录> status -sb` 看是否 behind | `git -C <目录> pull --ff-only`，软链不用重建 |

固定在某个提交上的 clone 先 `checkout main`，再按上表升级。

装的是哪一版：技能目录里装了副本时，`oberth doctor --only agent_skill --json` 的 `detail`
列出每个副本的路径和版本，多份副本版本不一致时会告警。插件还可以用 `claude plugin list`。
Skills CLI 自己不带版本，`check` 只回答有没有更新。

skill 里的命令和字段跟着引擎契约走。引擎不知道哪份副本过期，只是照常执行：命令或 flag
改过就直接报错，字段改过则读不到值。升级后再排查其他原因。

## 卸载

| 装法 | 卸载 |
| --- | --- |
| Skills CLI | `npx skills remove -g option-berth` |
| Claude Code 插件 | `claude plugin uninstall option-berth@sheathedsharp`。不再用这个市场时运行 `/plugin marketplace remove sheathedsharp` |
| 手工克隆 | 删掉 `~/.claude/skills/option-berth` 这条软链，再删 clone 的目录 |

skill 里只有说明文档和 `agents/openai.yaml` 这一份 agent 接口声明，不安装钩子，
也不修改 agent 配置。卸载不会动 `oberth.yaml`、运行状态和项目文件。

## 发布

新契约发布时，在同一个 PR 里同步三处：

- `SKILL.md` 的 `metadata.version`
- `.claude-plugin/plugin.json` 的 `version`，插件市场按它决定是否推送更新
- 本 README 开头的当前版本

引擎仓库的 `scripts/check_skill_contract.py` 从 CLI 契约、清单 schema 和 observation
常量里取锚点，检查本仓库的 `SKILL.md` 和 `references/*.md` 是否覆盖。契约变了先改内容，
再改版本号。只改版本号过不了引擎的检查。

## 内容

- [SKILL.md](SKILL.md) — 入口：先读当前 worktree，再按任务选一份 reference。
- `references/` — 起停与失败原因、监听观察与沙箱、清单起草与采纳（含 `prepare_inputs`、
  `env_file`、`workspace` 地址、`health` 三种写法与 `${worktree}` 引用）、
  worktree 身份与清理、工作记录、跨 worktree 观察；attention 交接只在明确需要
  人工选择时使用；`oberth feedback` 的固定触发条件与步骤在可选的一节里。

契约以引擎仓库为准：[CLI](https://github.com/SheathedSharp/option-berth/blob/main/docs/cli.md)、
[清单](https://github.com/SheathedSharp/option-berth/blob/main/docs/cli.md)、
[产品边界](https://github.com/SheathedSharp/option-berth/blob/main/docs/product.md)、
[工作记录](https://github.com/SheathedSharp/option-berth/blob/main/docs/workplace.md)。

## 许可证

与引擎相同，适用 MIT；见 [LICENSE](LICENSE)。

## English

This repository ships the skill that teaches a coding agent to read one worktree's declared
services and runtime facts, run them, find out why they are not running, and leave the work behind
for the next session. The skill, the engine, and the macOS client are separate products and meet
only at the `oberth` CLI and its `--json` contract.

Install it with `npx skills add SheathedSharp/option-berth-skill -g`, with `/plugin install
option-berth --marketplace SheathedSharp/option-berth-skill`, or by cloning the repository and
symlinking it into your agent's skills directory. The version at the top of this file ships with the
skill, so it is the version of the copy you have.

`npx skills check -g option-berth` reports whether that skill's source changed, installs nothing, and
exits 1 when an update is available or the check fails. Install the update with `npx skills update
-g option-berth`. A plugin install shows its version in `claude plugin list` and updates with
`claude plugin update option-berth`. A clone updates with `git pull`; when it is pinned to a commit,
check out main first. `oberth doctor --only agent_skill --json` lists every copy it finds under the
agent skill directories, with the version each declares. Uninstall with `npx skills remove -g
option-berth`, `claude plugin uninstall option-berth@sheathedsharp`, or by deleting the symlink and
the clone. The skill ships documentation and one agent interface declaration, so uninstalling it
changes no hooks, no agent configuration, and no project files.
