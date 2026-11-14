# option-berth skill

<p align="center"><a href="README.md">English</a> · 简体中文</p>

给 coding agent 的指引：读懂一个 worktree 的服务声明与运行事实，把服务跑起来，
失败时定位原因，并把这一轮工作记录留给下一次会话。

本仓库是三个独立产品之一，只通过 `oberth` CLI 及其 `--json` 契约与另外两个相连：

| 产品 | 仓库 | 它做什么 |
| --- | --- | --- |
| 引擎 | [SheathedSharp/option-berth](https://github.com/SheathedSharp/option-berth) | `oberth` 声明并观察服务，负责起停，输出人和 agent 都能读的事实 |
| macOS 客户端 | [SheathedSharp/option-berth-macos](https://github.com/SheathedSharp/option-berth-macos) | 原生界面，呈现同一份事实 |
| skill（本仓库） | [SheathedSharp/option-berth-skill](https://github.com/SheathedSharp/option-berth-skill) | 教会 agent 使用这份事实 |

当前版本 **0.10.0**。两份 README 都随 skill 一起分发，因此这里的版本号就是本地副本的版本号。

## 安装

skill 随本仓库分发，引擎不负责安装。三种方式任选一种。skill 目录里只留一份
`option-berth`。插件安装的那份带命名空间，两者不会冲突。

### Skills CLI

支持 Claude Code、Codex、Cursor、OpenCode 等本机已安装的 agent：

```sh
npx skills add SheathedSharp/option-berth-skill -g
```

`-g` 装到用户级，去掉则装进当前项目，随仓库共享。安装器识别本机已有的 agent，
默认把它们软链到同一份源副本。要固定到某个提交，在仓库名后加 `#<commit>`，
之后 `npx skills update` 不会离开这个提交。本页其余 `npx skills` 命令也按这条规则：
项目级安装时去掉 `-g`。

### Claude Code 插件市场

```text
/plugin install option-berth --marketplace SheathedSharp/option-berth-skill
```

插件市场名是 `sheathedsharp`。旧版 Claude Code 先运行
`/plugin marketplace add SheathedSharp/option-berth-skill`，再运行
`/plugin install option-berth@sheathedsharp`。插件内的 skill 带命名空间，
不会与 skill 目录里的同名 skill 冲突。

### 手工克隆并软链

```sh
git clone https://github.com/SheathedSharp/option-berth-skill.git
mkdir -p ~/.claude/skills          # 以 Claude Code 为例，其他 agent 用各自的 skill 目录
ln -sfn "$PWD/option-berth-skill" ~/.claude/skills/option-berth
```

要固定版本，先 `git -C option-berth-skill checkout <commit>`，再建软链。这时 clone 处于
游离 HEAD，`git pull` 会拒绝执行。回到 `main` 用
`git -C option-berth-skill checkout main`。用复制代替软链时，副本不会自动更新。

## 升级

| 装法 | 有没有新版 | 升级 |
| --- | --- | --- |
| Skills CLI | `npx skills check -g option-berth` 只检查不安装，有更新或检查失败时退出码为 1 | `npx skills update -g option-berth` |
| Claude Code 插件 | 插件市场没有只检查的命令 | `claude plugin update option-berth@sheathedsharp`，或在 `/plugin` 面板里操作 |
| 手工克隆 | `git -C <目录> fetch`，再用 `git -C <目录> status -sb` 看是否落后 | `git -C <目录> pull --ff-only`。软链无需重建 |

固定在某个提交上的 clone 先 `checkout main`，再按上表升级。

装了哪一版：skill 目录里装了副本时，`oberth doctor --only agent_skill --json` 的 `detail`
列出每个副本的路径和版本，多份副本版本不一致时告警。插件用 `claude plugin list` 查看。
Skills CLI 自身不带版本，`check` 只回答有没有更新。

skill 里的命令和字段以引擎契约为准。引擎不知道哪份副本过期，只是照常执行：命令或 flag
改过会直接报错，字段改过则读不到值。遇到这两类错误先升级，再排查其他原因。

## 卸载

| 装法 | 卸载 |
| --- | --- |
| Skills CLI | `npx skills remove -g option-berth` |
| Claude Code 插件 | `claude plugin uninstall option-berth@sheathedsharp`。不再用这个市场时运行 `/plugin marketplace remove sheathedsharp` |
| 手工克隆 | 删掉 `~/.claude/skills/option-berth` 这条软链，再删 clone 的目录 |

skill 里只有说明文档和 `agents/openai.yaml` 这一份 agent 接口声明，不安装钩子，
也不修改 agent 配置。卸载不会修改 `oberth.yaml`、运行状态和项目文件。

## 发布

新契约发布时，在同一个 PR 里同步三处：

- `SKILL.md` 的 `metadata.version`
- `.claude-plugin/plugin.json` 的 `version`，插件市场按它决定是否推送更新
- `README.md` 与 `README.zh.md` 开头的当前版本

引擎仓库的 `scripts/check_skill_contract.py` 从 CLI 契约、清单 schema 和 observation
常量里取锚点，检查本仓库的 `SKILL.md` 和 `references/*.md` 是否覆盖。契约变了先改内容，
再改版本号。只改版本号无法通过引擎的检查。

## 内容

- [`SKILL.md`](SKILL.md) 是入口：先读当前 worktree，再按任务打开一份 reference。
- `references/` 按任务分册：服务起停与失败原因、监听观察与沙箱、清单起草与采纳、
  worktree 身份与清理、工作记录、跨 worktree 观察。attention 交接只在需要人做选择时
  使用。`oberth feedback` 单独一册，写明固定的触发条件与步骤。

契约以引擎仓库为准：[CLI](https://github.com/SheathedSharp/option-berth/blob/main/docs/cli.md)、
[清单](https://github.com/SheathedSharp/option-berth/blob/main/engine/docs/schema/manifest.schema.json)、
[产品边界](https://github.com/SheathedSharp/option-berth/blob/main/docs/product.md)、
[工作记录](https://github.com/SheathedSharp/option-berth/blob/main/docs/workplace.md)。

## 许可证

与引擎相同，适用 MIT。见 [LICENSE](LICENSE)。
