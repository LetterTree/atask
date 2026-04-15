import argparse
import sys
from pathlib import Path


def cmd_init(args, cwd: Path = None) -> int:
    from atask import store, schema
    cwd = cwd or Path.cwd()
    title = args.title or cwd.name
    data = schema.new_project(title)
    try:
        store.create(data, cwd)
        print(f"Initialized {schema.PROJECT_FILE} with title '{title}'")
        return 0
    except FileExistsError as e:
        print(str(e), file=sys.stderr)
        return 1


def cmd_add(args, cwd: Path = None) -> int:
    from atask import store
    from atask import tree_ops
    from atask.errors import AtaskError
    cwd = cwd or Path.cwd()
    try:
        data = store.load(cwd)
        if args.task_key:
            tree_ops.add_main_task(data, args.task_key, args.title, args.desc or "")
        elif args.task and args.id:
            tree_ops.add_subtask(data, args.task, args.id, args.title, args.desc or "", args.parent)
        else:
            print("Error: specify --task-key (main task) or --task + --id (subtask)", file=sys.stderr)
            return 1
        store.save(data, cwd)
        return 0
    except FileNotFoundError:
        print(".project.atask not found. Run 'atask init' first.", file=sys.stderr)
        return 1
    except AtaskError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_status(args, cwd: Path = None) -> int:
    from atask import store
    from atask import tree_ops
    from atask import validators
    from atask.errors import AtaskError
    cwd = cwd or Path.cwd()
    try:
        data = store.load(cwd)
        task_key = args.task
        id_ = getattr(args, "id", None)

        if id_:
            node = tree_ops.find_node_by_id(data, task_key, id_)
            if node is None:
                print(f"Error: subtask '{id_}' not found in '{task_key}'", file=sys.stderr)
                return 1
            current_st = node["st"]
        else:
            task = tree_ops.find_task_by_key(data, task_key)
            if task is None:
                print(f"Error: task '{task_key}' not found", file=sys.stderr)
                return 1
            current_st = task["st"]

        target_st = args.target_status
        validators.validate_transition(current_st, target_st)

        if target_st == "done":
            target_node = node if id_ else task
            if not validators.can_mark_done(target_node):
                print(f"Error: cannot mark done — unfinished subtasks exist", file=sys.stderr)
                return 1

        tree_ops.set_task_status(data, task_key, id_, target_st)
        store.save(data, cwd)
        return 0
    except FileNotFoundError:
        print(".project.atask not found. Run 'atask init' first.", file=sys.stderr)
        return 1
    except AtaskError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_tree(args, cwd: Path = None) -> int:
    from atask import store
    from atask import formatters
    cwd = cwd or Path.cwd()
    try:
        data = store.load(cwd)
        print(formatters.format_tree(data))
        return 0
    except FileNotFoundError:
        print(".project.atask not found. Run 'atask init' first.", file=sys.stderr)
        return 1


def cmd_validate(args, cwd: Path = None) -> int:
    from atask import store
    from atask import validators
    cwd = cwd or Path.cwd()
    try:
        data = store.load(cwd)
        errors = validators.validate_project(data)
        if errors:
            for e in errors:
                print(f"  - {e}")
            return 1
        print("Project is valid.")
        return 0
    except FileNotFoundError:
        print(".project.atask not found. Run 'atask init' first.", file=sys.stderr)
        return 1


def cmd_prune(args, cwd: Path = None) -> int:
    from atask import store
    from atask import tree_ops
    from datetime import datetime, timezone
    cwd = cwd or Path.cwd()
    try:
        data = store.load(cwd)
        now = datetime.now(timezone.utc)
        prunable = tree_ops.find_prunable_tasks(data, now)
        if not prunable:
            print("Nothing to prune.")
            return 0
        for scope, key in prunable:
            if scope == "__main__":
                print(f"  Would prune main task: {key}")
            else:
                print(f"  Would prune subtask: {key} (in {scope})")
        if args.apply:
            tree_ops.prune_tasks(data, prunable)
            store.save(data, cwd)
            print(f"Pruned {len(prunable)} task(s).")
        else:
            print("(dry-run) Pass --apply to actually prune.")
        return 0
    except FileNotFoundError:
        print(".project.atask not found. Run 'atask init' first.", file=sys.stderr)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(prog="atask", description="AI task tracking CLI")
    sub = parser.add_subparsers(dest="command")

    # init
    p_init = sub.add_parser("init", help="Initialize .project.atask")
    p_init.add_argument("--title", help="Project title (default: directory name)")

    # add
    p_add = sub.add_parser("add", help="Add main task or subtask")
    p_add.add_argument("--task-key", dest="task_key", help="Main task key (creates main task)")
    p_add.add_argument("--task", help="Main task key to add subtask under")
    p_add.add_argument("--id", help="Subtask id")
    p_add.add_argument("--parent", help="Parent subtask id for nested subtask")
    p_add.add_argument("--title", required=True, help="Title")
    p_add.add_argument("--desc", default="", help="Description")

    # start / done / block / cancel
    for cmd, target in [("start", "doing"), ("done", "done"), ("block", "blocked"), ("cancel", "cancelled")]:
        p = sub.add_parser(cmd, help=f"Set task status to {target}")
        p.add_argument("--task", required=True, help="Main task key")
        p.add_argument("--id", help="Subtask id (omit for main task)")
        p.set_defaults(target_status=target)

    # tree
    sub.add_parser("tree", help="Show task tree")

    # validate
    sub.add_parser("validate", help="Validate .project.atask")

    # prune
    p_prune = sub.add_parser("prune", help="Remove old completed tasks")
    p_prune.add_argument("--apply", action="store_true", help="Actually prune (default: dry-run)")

    args = parser.parse_args()

    if args.command == "init":
        return cmd_init(args)
    if args.command == "add":
        return cmd_add(args)
    if args.command in ("start", "done", "block", "cancel"):
        return cmd_status(args)
    if args.command == "tree":
        return cmd_tree(args)
    if args.command == "validate":
        return cmd_validate(args)
    if args.command == "prune":
        return cmd_prune(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
