# atask

Lightweight task tracking CLI for AI agents. Single-file JSON truth source at `.project.atask`.

## Design Constraints

- One project → one `.project.atask` file (project root)
- Main task `key` and subtask `id` must be defined in the **plan phase** before execution
- All writes go through `atask` CLI — no direct JSON editing in normal workflow

## Install

### npm（推荐，无需 Python）

```bash
npm install -g @lettertree/atask
```

支持平台：Linux x64、macOS x64、Windows x64。

### 从源码安装（开发者）

```bash
pip install -e .
```

### 本地构建二进制

```bash
pip install -e '.[build]'
sh npm/scripts/build.sh
```

## Commands

### `atask init`

Create `.project.atask` in the current directory.

```bash
atask init
atask init --title "my-project"
```

### `atask add`

Add main task or subtask.

```bash
# Main task
atask add --task-key cli-core --title "CLI 核心能力" --desc "实现基础命令"

# Subtask
atask add --task cli-core --id t1 --title "实现 init 命令" --desc "创建项目真源"

# Nested subtask
atask add --task cli-core --parent t1 --id t1.1 --title "支持 --title 参数" --desc ""
```

### `atask start` / `atask done` / `atask block` / `atask cancel`

Transition task status.

```bash
atask start --task cli-core --id t1    # todo → doing
atask done  --task cli-core --id t1    # doing → done
atask block --task cli-core --id t1    # doing → blocked
atask cancel --task cli-core --id t1   # doing/todo → cancelled

# Operate on main task (omit --id)
atask start --task cli-core
atask done  --task cli-core
```

**Allowed transitions:**
- `todo → doing`, `todo → cancelled`
- `doing → done`, `doing → blocked`, `doing → cancelled`
- `blocked → doing`

Parent task can only be marked `done` when all children are `done` or `cancelled`.

### `atask tree`

Show task tree with status and indentation.

```bash
atask tree
```

Output example:
```
[todo] cli-core CLI 核心能力
  [doing] t1 实现 init 命令
  [todo] t2 输出任务树视图
    [todo] t2.1 渲染缩进树结构
```

### `atask validate`

Validate `.project.atask` — checks schema, key/id uniqueness, state values, parent completion constraints.

```bash
atask validate
```

Returns exit code 0 on success, non-zero with error list on failure.

### `atask prune`

Remove completed tasks older than 14 days.

```bash
atask prune           # dry-run (shows what would be pruned)
atask prune --apply   # actually removes eligible tasks
```

Only `done` tasks with `dt` older than 14 days are eligible.

## Plan-Layer Constraints

- Main task `key` must be defined in the plan document before running `atask add --task-key`
- Subtask `id` must be defined in the plan document before running `atask add --id`
- CLI is the only write path — do not edit `.project.atask` directly during normal workflow
