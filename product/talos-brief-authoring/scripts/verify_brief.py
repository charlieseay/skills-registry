#!/usr/bin/env python3
"""
Verify a helmsman task brief against the REAL compile/lint gate before
filing it via POST /tasks — catches brief-lint and brief_compiler failures
locally instead of discovering them from a cancelled task afterward.

This exists because task #3297 was filed, silently cancelled by the compile
gate two seconds later, and nobody noticed until asked to check on it —
exactly the "trust but verify" failure this whole skill is about preventing.
Running this script BEFORE POST /tasks turns that into an immediate,
visible failure instead of a several-minutes-later surprise.

Usage:
    python3 verify_brief.py <task.json>
    python3 verify_brief.py --task "task title" --brief brief.md --owner TALOS --priority 3

task.json shape (same as what you'd POST to /tasks):
    {"task": "...", "owner": "...", "priority": N, "tags": "...", "brief_text": "..."}

Exit code 0 = brief will pass the gate. Exit code 1 = it will be rejected,
with the exact errors printed (same errors POST /tasks or the async
compiler would surface, just found locally and instantly).
"""
import argparse
import json
import sys
from pathlib import Path

BREIF_COMPILER_LIB = Path.home() / "Projects" / "claude-config" / "bin" / "lib"


def load_task(args) -> dict:
    if args.task_json:
        return json.loads(Path(args.task_json).read_text())
    if not (args.task and args.brief and args.owner):
        print("ERROR: either pass a task.json path, or --task/--brief/--owner/--priority", file=sys.stderr)
        sys.exit(2)
    return {
        "task": args.task,
        "owner": args.owner,
        "priority": args.priority or 3,
        "tags": args.tags or "",
        "brief_text": Path(args.brief).read_text(),
        "project": None,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("task_json", nargs="?", help="Path to a task JSON file (same shape as POST /tasks body)")
    p.add_argument("--task", help="Task title (alternative to task_json)")
    p.add_argument("--brief", help="Path to a brief_text markdown file (alternative to task_json)")
    p.add_argument("--owner", help="Task owner, e.g. TALOS or CLAUDE")
    p.add_argument("--priority", type=int, help="Task priority (default 3)")
    p.add_argument("--tags", help="CSV tags string")
    args = p.parse_args()

    task = load_task(args)
    task.setdefault("project", None)

    sys.path.insert(0, str(BREIF_COMPILER_LIB))
    try:
        import brief_compiler
    except ImportError as e:
        print(f"ERROR: could not import brief_compiler from {BREIF_COMPILER_LIB} — is claude-config checked out there? ({e})", file=sys.stderr)
        sys.exit(2)

    brief, meta = brief_compiler.compile_brief(task, allow_llm=False)
    ok, errors = brief_compiler.lint(brief)

    if ok:
        print("✓ Brief will pass the compile/lint gate.")
        return 0

    print("✗ Brief will be REJECTED by the compile/lint gate:", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)
    print(
        "\nDo not just reword the Steps section blindly — check whether this "
        "matches a documented false-positive in talos-brief-authoring's SKILL.md "
        "first (negation, compound identifiers, step-ordering). If it's a new "
        "false positive, fix the gate itself (claude-config/bin/brief-lint) "
        "rather than working around it in every future brief.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
