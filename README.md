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

skill 随本仓库分发，装不装由使用者决定；引擎不会替你装。用**软链**指向克隆下来的仓库，
这样 `git pull` 之后 agent 看到的就是新版本：

```sh
git clone https://github.com/SheathedSharp/option-berth-skill.git
mkdir -p ~/.claude/skills          # 以 Claude Code 为例；其他 agent 用各自的技能目录
ln -sfn "$PWD/option-berth-skill" ~/.claude/skills/option-berth
```

复制过去的那份不会自己更新：命令或 `--json` 形状变了它还停在旧契约上，于是同一台机器上
会出现两份同名 skill，agent 用哪份不确定。

## 内容

- [SKILL.md](SKILL.md) — 入口：先读当前 worktree，再按任务选一份 reference。
- `references/` — 起停与状态、清单起草、工作记录、跨 worktree 观察、attention 交接。

契约以引擎仓库为准：[CLI](https://github.com/SheathedSharp/option-berth/blob/main/docs/cli.md)、
[清单](https://github.com/SheathedSharp/option-berth/blob/main/docs/cli.md)、
[产品边界](https://github.com/SheathedSharp/option-berth/blob/main/docs/product.md)。

## 许可证

与引擎相同，适用 MIT；见 [LICENSE](LICENSE)。

## English

The skill that teaches a coding agent to read one worktree's declared services and runtime
facts, run them, find out why they are not running, and leave the work behind for the next
session. It is one of three independent products and talks to the others only through the
`oberth` CLI and its `--json` contract. Install it by symlinking this clone into your agent's
skills directory so `git pull` is the update.
