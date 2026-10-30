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

skill 随本仓库分发，装不装由使用者决定；引擎不会替你装。下面三种方式**选一种**，
不要在同一台机器上同时装两份同名 skill。

### Skills CLI（推荐）

支持 Claude Code、Codex、Cursor、OpenCode 等本机已安装的 agent：

```sh
npx skills add SheathedSharp/option-berth-skill -g
```

`-g` 装到用户级；去掉它则装进当前项目，随仓库共享。安装器会识别现有的 agent，
默认用软链指向一份规范副本。之后用同一套命令检查和更新：

```sh
npx skills check
npx skills update
npx skills remove option-berth
```

#### 克隆超时时的兜底

`npx skills add` 在克隆阶段超时，通常不是仓库大小的问题：本仓库约 400 KiB、17 个提交，
浅克隆本机约 2 秒。CLI 会先用 GitHub API 和 raw 各试 10 秒，最后用 `git clone --depth 1`
并给整段克隆 300 秒；网络、代理或 agent 沙箱卡住时，就会等满 5 分钟再报
`Clone timed out after 300s`。按下面的顺序换一条路，`-a` 换成你的 agent。

1. 直接下载归档，绕过 GitHub API 和 `git clone`：

   ```sh
   npx --yes skills@latest add \
     https://codeload.github.com/SheathedSharp/option-berth-skill/tar.gz/refs/heads/main \
     -g -y -a claude-code --copy
   ```

   需要固定版本时，把 `refs/heads/main` 换成具体的 commit SHA。

2. 本机先浅克隆，再把本地目录交给 CLI：

   ```sh
   git clone --depth 1 https://github.com/SheathedSharp/option-berth-skill.git /tmp/option-berth-skill
   npx --yes skills@latest add /tmp/option-berth-skill -g -y -a claude-code --copy
   ```

3. 必须走 `git clone` 时，提高超时并给 GitHub API 一个 token：

   ```sh
   SKILLS_CLONE_TIMEOUT_MS=600000 GITHUB_TOKEN=... \
     npx skills add SheathedSharp/option-berth-skill -g
   ```

`DISABLE_TELEMETRY=1` 可以省掉安装后的遥测和审计请求（约 3–5 秒），但不会改变克隆超时。
不要在 agent 沙箱里运行安装：沙箱可能禁止网络或 `git` 子进程，表现同样是克隆超时。

### Claude Code 插件市场

```text
/plugin install option-berth --marketplace SheathedSharp/option-berth-skill
```

插件市场名是 `sheathedsharp`。旧版 Claude Code 先运行
`/plugin marketplace add SheathedSharp/option-berth-skill`，再运行
`/plugin install option-berth@sheathedsharp`。更新用
`/plugin marketplace update sheathedsharp`，卸载用
`/plugin uninstall option-berth@sheathedsharp`。插件内的 skill 带命名空间，
不会和散落目录里的同名 skill 混淆。

### 手工克隆 + 软链（离线或固定版本）

```sh
git clone https://github.com/SheathedSharp/option-berth-skill.git
mkdir -p ~/.claude/skills          # 以 Claude Code 为例；其他 agent 用各自的技能目录
ln -sfn "$PWD/option-berth-skill" ~/.claude/skills/option-berth
```

这条路径靠 `git pull` 更新。如果复制而不是软链，那份不会自己更新：命令或 `--json`
形状变了它还停在旧契约上。

发布新契约时，同步 `SKILL.md` 的 `metadata.version` 与 `.claude-plugin/plugin.json`
的 `version`；插件市场按后者判断是否把更新推给已安装的用户。

引擎仓库的 `scripts/check_skill_contract.py` 会从 CLI 契约、清单 schema 与 observation
常量提取锚点，检查本仓库的 `SKILL.md` 与 `references/*.md` 是否覆盖。契约变化时先更新
内容，再同步版本号；只改版本号不会让引擎的检查通过。

## 内容

- [SKILL.md](SKILL.md) — 入口：先读当前 worktree，再按任务选一份 reference。
- `references/` — 起停与失败原因、监听观察与沙箱、清单起草与采纳（含 `prepare_inputs`、
  `env_file`、`workspace` 地址、`health` 三种写法与 `${worktree}` 引用）、
  worktree 身份与清理、工作记录、跨 worktree 观察；attention 交接只在明确需要
  人工选择时使用。

契约以引擎仓库为准：[CLI](https://github.com/SheathedSharp/option-berth/blob/main/docs/cli.md)、
[清单](https://github.com/SheathedSharp/option-berth/blob/main/docs/cli.md)、
[产品边界](https://github.com/SheathedSharp/option-berth/blob/main/docs/product.md)。

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
