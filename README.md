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

Additional repository-native skill:
- `microsoft-learn-deep-research`

Strictest feasible parity is implemented in canonical skills, with explicit boundaries for non-portable Claude-only mechanisms:
- SessionStart hooks
- Stop hook interception
- Claude command frontmatter/tool contracts

These boundaries are documented inside relevant skill references (especially `ralph-wiggum`).

## Canonical Skill Catalog

Current canonical skill IDs:
- `explanatory-output-style`
- `learning-output-style`
- `code-review`
- `feature-dev`
- `frontend-design`
- `ralph-wiggum`
- `microsoft-learn-deep-research`

## Requirements

- Python 3.10+ (standard library only)
- No `bun` or `uv`

## Install Pattern

Recommended in consumer repositories:
1. Add this repository as `agent-skills/` at repo root (clone/submodule/vendor).
2. Run sync from that consumer repo root.

Generated adapter files reference canonical source paths under `agent-skills/.agents/skills/...`.

Consumer repo quick start:

```bash
python agent-skills/scripts/sync.py --target all --invocation both --workspace .
```

## CLI Usage

Run from the `agent-skills/` repository root:

```bash
python scripts/sync.py \
  --target cursor|copilot|augment|all \
  --invocation auto|manual|both \
  [--skills skill1,skill2,...] \
  --workspace <target-repo> \
  [--source <skills-path>] \
  [--dry-run] [--check] [--force] [--prune]
```

### Flags

- `--target`: output target (`all` default)
- `--invocation`: invocation behavior (`both` default)
- `--skills`: optional comma-separated skill names (default: all skills)
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

Single skill only:

```bash
python scripts/sync.py --target all --invocation both --skills microsoft-learn-deep-research --workspace ../target-repo
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

## One-Line Installers (No Clone)

These installers download a temporary archive of this repository, run `scripts/sync.py`, and clean up.
For security, prefer the download-then-run variants over pipe execution.

Installer prerequisites:
- Bash flow: `python3` or `python`, `curl` or `wget`, and `tar`
- PowerShell flow: PowerShell 5.1+ and Python (`py -3`, `python`, or `python3`)

Repository:
- `https://github.com/vegeta03/agent-skills.git`

### Bash (Linux/macOS/Git Bash)

Recommended (download then run):

```bash
curl -fsSL "https://raw.githubusercontent.com/vegeta03/agent-skills/master/scripts/install.sh" -o "/tmp/agent-skills-install.sh" && bash "/tmp/agent-skills-install.sh" --target all --invocation both --workspace .
```

Optional pipe-to-shell:

```bash
curl -fsSL "https://raw.githubusercontent.com/vegeta03/agent-skills/master/scripts/install.sh" | bash -s -- --target all --invocation both --workspace .
```

### PowerShell (Windows)

Recommended (download then run):

```powershell
$u="https://raw.githubusercontent.com/vegeta03/agent-skills/master/scripts/install.ps1"; $f=Join-Path $env:TEMP "agent-skills-install.ps1"; iwr $u -OutFile $f; & $f -Target all -Invocation both -Workspace .
```

Optional pipe execution:

```powershell
iex "& { $(irm https://raw.githubusercontent.com/vegeta03/agent-skills/master/scripts/install.ps1) } -Target all -Invocation both -Workspace ."
```

### Installer Options

Both installers support:
- target selection (`--target` / `-Target`)
- invocation selection (`--invocation` / `-Invocation`)
- optional skill filtering (`--skills` / `-Skills`)
- workspace path (`--workspace` / `-Workspace`)
- ref override (`--ref` / `-Ref`)
- repo override (`--repo` / `-Repo`)
- sync passthrough flags (`--dry-run`, `--check`, `--force`, `--prune`)

Single-skill one-line example:

```bash
curl -fsSL "https://raw.githubusercontent.com/vegeta03/agent-skills/master/scripts/install.sh" | bash -s -- --target copilot --invocation manual --skills microsoft-learn-deep-research --workspace .
```

## Publisher Mode

This repository can remain publisher-only (no local root adapters in this repo).  
Consumer repositories run sync to materialize IDE-specific adapters on demand.
