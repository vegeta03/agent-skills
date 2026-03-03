# Agent Skills Repository

Standalone, cross-IDE skill source with generator-driven adapters and invocation mode control.

## Canonical Source

- Canonical skills: `.agents/skills/`
- Generator CLI: `scripts/sync.py`
- Templates: `templates/`

This repository is intended to be published independently and consumed by other projects.

## Strict Parity Scope

Converted source plugins:
- `plugins/explanatory-output-style`
- `plugins/learning-output-style`
- `plugins/code-review`
- `plugins/feature-dev`
- `plugins/frontend-design`
- `plugins/ralph-wiggum`

Strictest feasible parity is implemented in canonical skills, with explicit boundaries for non-portable Claude-only mechanisms:
- SessionStart hooks
- Stop hook interception
- Claude command frontmatter/tool contracts

These boundaries are documented inside relevant skill references (especially `ralph-wiggum`).

## Requirements

- Python 3.10+ (standard library only)
- No `bun` or `uv`

## Install Pattern

Recommended in consumer repositories:
1. Add this repository as `agent-skills/` at repo root (clone/submodule/vendor).
2. Run sync from that consumer repo root.

Generated adapter files reference canonical source paths under `agent-skills/.agents/skills/...`.

## CLI Usage

```bash
python scripts/sync.py \
  --target cursor|copilot|augment|all \
  --invocation auto|manual|both \
  --workspace <target-repo> \
  [--source <skills-path>] \
  [--dry-run] [--check] [--force] [--prune]
```

### Flags

- `--target`: output target (`all` default)
- `--invocation`: invocation behavior (`both` default)
- `--workspace`: target repository path (default `.`)
- `--source`: canonical source directory (default `./.agents/skills`)
- `--dry-run`: print operations without writing
- `--check`: drift check (non-zero exit on mismatch/stale generated files)
- `--force`: overwrite non-generated conflicting files
- `--prune`: remove stale generated files for selected target roots

## Invocation Mode Matrix

### Cursor (`.cursor/skills`)

- `auto`: `disable-model-invocation: false`
- `manual`: `disable-model-invocation: true` (slash/manual style)
- `both`: `disable-model-invocation: false` (model may auto-load; user can still invoke)

### GitHub Copilot VSCode

Generated layers:
- `.github/skills/<skill>/SKILL.md` (Agent Skills layer)
- `.github/prompts/<skill>.prompt.md` (manual slash command layer)
- `.github/copilot-instructions.md` and `.github/instructions/*.instructions.md` (auto policy/context layer)

Mode mapping for `.github/skills`:
- `auto`: `user-invokable: false`, `disable-model-invocation: false`
- `manual`: `user-invokable: true`, `disable-model-invocation: true`
- `both`: `user-invokable: true`, `disable-model-invocation: false`

### Augment (`.augment/rules`)

- `auto`: generate `*.md` with `type: agent_requested`
- `manual`: generate `*.md` with `type: manual`
- `both`: generate paired files:
  - `<skill>.auto.md` (`agent_requested`)
  - `<skill>.manual.md` (`manual`)

## Target Paths by IDE

- Cursor: `.cursor/skills/` + `AGENTS.md`
- Copilot: `.github/copilot-instructions.md`, `.github/instructions/`, `.github/skills/`, `.github/prompts/`, `AGENTS.md`
- Augment: `.augment/rules/` + `AGENTS.md`

## Common Commands

All targets, both-mode:

```bash
python scripts/sync.py --target all --invocation both --workspace ../target-repo
```

Auto-only:

```bash
python scripts/sync.py --target all --invocation auto --workspace ../target-repo
```

Manual-only:

```bash
python scripts/sync.py --target all --invocation manual --workspace ../target-repo
```

Deterministic CI check:

```bash
python scripts/sync.py --target all --invocation both --workspace ../target-repo --check
```

Cleanup stale generated files:

```bash
python scripts/sync.py --target all --invocation both --workspace ../target-repo --prune
```

## Publisher Mode

This repository can remain publisher-only (no local root adapters in this repo).  
Consumer repositories run sync to materialize IDE-specific adapters on demand.
