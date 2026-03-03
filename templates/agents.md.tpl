{marker}

# Cross-Agent Instructions

This repository uses canonical Agent Skills from `agent-skills/.agents/skills/`.

## Skill Routing

{skills_routing}

## Planner behavior

- Use the active skill's planning protocol first.
- For feature work, require clarification and architecture selection before coding.
- For review work, prioritize high-confidence findings.

## Coding behavior

- Follow the active skill's coding protocol and guardrails.
- Keep implementations simple, modular, and production-quality.

## Precedence

Direct user instructions override this file.  
If instructions conflict, prefer the most specific active skill.
