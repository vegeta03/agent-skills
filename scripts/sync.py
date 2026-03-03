#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from lib.file_ops import apply_file_map
from lib.generators import (
    generate_agents_file,
    generate_augment_files,
    generate_copilot_files,
    generate_cursor_files,
)
from lib.skill_loader import Skill, load_skills


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate and sync Cursor/Copilot/Augment adapters from canonical skills."
    )
    parser.add_argument(
        "--target",
        choices=["cursor", "copilot", "augment", "all"],
        default="all",
        help="Adapter target to generate (default: all).",
    )
    parser.add_argument(
        "--workspace",
        default=".",
        help="Target workspace path where adapter files will be written (default: current directory).",
    )
    parser.add_argument(
        "--source",
        default=None,
        help="Canonical skills path (default: <this-repo>/.agents/skills).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned writes/updates without writing files.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check for drift only. Exits non-zero if output differs.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing non-generated target files.",
    )
    parser.add_argument(
        "--invocation",
        choices=["auto", "manual", "both"],
        default="both",
        help="Invocation mode for generated skill/rule artifacts (default: both).",
    )
    parser.add_argument(
        "--prune",
        action="store_true",
        help="Remove stale generated files for selected targets.",
    )
    parser.add_argument(
        "--skills",
        default=None,
        help="Optional comma-separated canonical skill names to generate (default: all).",
    )
    return parser.parse_args()


def _filter_skills(skills: list[Skill], skills_arg: str | None) -> list[Skill]:
    if skills_arg is None:
        return skills

    requested = [name.strip() for name in skills_arg.split(",") if name.strip()]
    if not requested:
        raise ValueError("`--skills` was provided but no valid skill names were found.")

    available = {skill.name for skill in skills}
    missing = sorted({name for name in requested if name not in available})
    if missing:
        available_csv = ", ".join(sorted(available))
        missing_csv = ", ".join(missing)
        raise ValueError(
            f"Unknown skill(s): {missing_csv}. Available skills: {available_csv}"
        )

    requested_set = set(requested)
    return [skill for skill in skills if skill.name in requested_set]


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    template_dir = repo_root / "templates"
    source_dir = Path(args.source).resolve() if args.source else repo_root / ".agents" / "skills"
    workspace = Path(args.workspace).resolve()

    try:
        skills = _filter_skills(load_skills(source_dir), args.skills)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    file_map: dict[Path, str] = {}

    include_cursor = args.target in ("cursor", "all")
    include_copilot = args.target in ("copilot", "all")
    include_augment = args.target in ("augment", "all")

    if include_cursor:
        file_map.update(generate_cursor_files(template_dir, workspace, skills, args.invocation))
    if include_copilot:
        file_map.update(generate_copilot_files(template_dir, workspace, skills, args.invocation))
    if include_augment:
        file_map.update(generate_augment_files(template_dir, workspace, skills, args.invocation))

    # Keep AGENTS.md in sync for all target modes.
    file_map.update(generate_agents_file(template_dir, workspace, skills))

    prune_roots: list[Path] = []
    if include_cursor:
        prune_roots.append(workspace / ".cursor" / "skills")
    if include_copilot:
        prune_roots.append(workspace / ".github")
    if include_augment:
        prune_roots.append(workspace / ".augment" / "rules")

    result = apply_file_map(
        file_map,
        dry_run=args.dry_run,
        check=args.check,
        force=args.force,
        prune=args.prune,
        prune_roots=tuple(prune_roots),
    )

    print(
        f"SUMMARY writes={result.writes} updates={result.updates} unchanged={result.unchanged} "
        f"drifts={result.drifts} conflicts={result.conflicts} pruned={result.pruned}"
    )

    if args.check and result.drifts > 0:
        return 1
    if result.conflicts > 0:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
