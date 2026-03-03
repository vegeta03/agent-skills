{marker}

# Repository Copilot Instructions

Use these instructions for planning and coding tasks in this repository.

## Canonical Source

- Primary skills are in `agent-skills/.agents/skills/`.
- `AGENTS.md` provides cross-agent routing and precedence.
- `.github/instructions/*.instructions.md` provides auto policy/context adapters.
- `.github/skills/*/SKILL.md` provides Copilot Agent Skills adapters.
- `.github/prompts/*.prompt.md` provides manual slash-invoked prompt wrappers.

## Available Skills

{skills_list}

## Operating Rules

- Activate the most relevant skill for the current user intent.
- Keep outputs concise and implementation-focused.
- Prefer high-confidence findings over speculative feedback.
- Keep code modular and avoid large multi-responsibility files.
