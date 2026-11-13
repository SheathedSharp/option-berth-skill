# option-berth skill

给 coding agent 的 **option-berth 指引**：怎么读懂一个 worktree 的服务声明与运行事实、
把它跑起来、失败时看哪里，以及把这一轮工作留给下一个接手的人。

这是三个独立产品之一，只通过 CLI 与 `--json` 契约与另外两个相连：

| 产品 | 仓库 | 它做什么 |
| --- | --- | --- |
| 引擎 | [SheathedSharp/option-berth](https://github.com/SheathedSharp/option-berth) | `oberth`：声明、观察、起停服务，输出人和 agent 都能读的事实 |
| macOS 客户端 | [SheathedSharp/option-berth-macos](https://github.com/SheathedSharp/option-berth-macos) | 原生界面，呈现同一份事实 |
| **本仓库** | — | 教会 agent 使用上面这份事实 |

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

The skill that teaches a coding agent to read one worktree's declared services and runtime
facts, run them, find out why they are not running, and leave the work behind for the next
session. It is one of three independent products and talks to the others only through the
`oberth` CLI and its `--json` contract.

Install it with `npx skills add SheathedSharp/option-berth-skill -g`, or in Claude Code with
`/plugin install option-berth --marketplace SheathedSharp/option-berth-skill`. Both keep one
canonical copy and update it in place. Cloning and symlinking into your agent's skills directory
remains the offline option; update that one with `git pull`.
