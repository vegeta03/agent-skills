# Canonical Skill Source

This directory is the canonical source of truth for portable Agent Skills.

## Plugin to Skill Mapping

- `plugins/explanatory-output-style` -> `.agents/skills/explanatory-output-style`
- `plugins/learning-output-style` -> `.agents/skills/learning-output-style`
- `plugins/code-review` -> `.agents/skills/code-review`
- `plugins/feature-dev` -> `.agents/skills/feature-dev`
- `plugins/frontend-design` -> `.agents/skills/frontend-design`
- `plugins/ralph-wiggum` -> `.agents/skills/ralph-wiggum`

## Portability Notes

- Claude lifecycle hooks are translated into explicit behavior protocols.
- Planner and coding behavior are split in each skill for cross-agent compatibility.
- Target-specific adapters are generated from this source via `scripts/sync.py`.
