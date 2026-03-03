from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .generators import GEN_MARKER


@dataclass(frozen=True)
class ApplyResult:
    writes: int
    updates: int
    unchanged: int
    drifts: int
    conflicts: int
    pruned: int


def apply_file_map(
    file_map: dict[Path, str],
    *,
    dry_run: bool,
    check: bool,
    force: bool,
    prune: bool,
    prune_roots: tuple[Path, ...],
) -> ApplyResult:
    writes = 0
    updates = 0
    unchanged = 0
    drifts = 0
    conflicts = 0
    pruned = 0

    for path in sorted(file_map.keys()):
        desired = file_map[path]
        exists = path.exists()
        current = path.read_text(encoding="utf-8") if exists else None

        if current == desired:
            unchanged += 1
            print(f"UNCHANGED {path}")
            continue

        if check:
            drifts += 1
            state = "MISSING" if not exists else "DIFFERS"
            print(f"DRIFT({state}) {path}")
            continue

        if exists and not force and GEN_MARKER not in (current or ""):
            conflicts += 1
            print(f"CONFLICT {path} (use --force to overwrite non-generated file)")
            continue

        action = "WRITE" if not exists else "UPDATE"
        print(f"{action} {path}")
        if dry_run:
            continue

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(desired, encoding="utf-8")
        if exists:
            updates += 1
        else:
            writes += 1

    if prune:
        generated_paths = {p.resolve() for p in file_map.keys()}
        for root in prune_roots:
            if not root.exists():
                continue
            for path in sorted(p for p in root.rglob("*") if p.is_file()):
                if path.resolve() in generated_paths:
                    continue
                try:
                    content = path.read_text(encoding="utf-8")
                except Exception:
                    continue
                if GEN_MARKER not in content:
                    continue
                if check:
                    drifts += 1
                    print(f"DRIFT(STALE) {path}")
                    continue
                print(f"PRUNE {path}")
                if dry_run:
                    continue
                path.unlink(missing_ok=True)
                pruned += 1

    return ApplyResult(
        writes=writes,
        updates=updates,
        unchanged=unchanged,
        drifts=drifts,
        conflicts=conflicts,
        pruned=pruned,
    )
