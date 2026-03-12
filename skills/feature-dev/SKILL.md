---
name: feature-dev
description: Guides end-to-end feature delivery through discovery, exploration, clarification, architecture, implementation, and review gates. Use when building non-trivial features that need structured planning and execution.
---

# Feature Development

Follow a gated workflow for high-confidence feature delivery.

Detailed phase instructions are in:
- `references/phases.md`
- `references/agent-topology.md`

## Activation Triggers

Activate when the user asks to:
- build a new feature
- implement multi-file behavior changes
- design and ship a non-trivial enhancement

## Planner behavior

- Run phases 1-4 before implementation.
- Require clarifying questions for underspecified behavior.
- Present architecture approaches with trade-offs and recommendation.
- Require explicit user approval before coding starts.
- Never skip the clarifying-question gate.
- If user says "whatever you think is best", provide recommendation and ask explicit confirmation.

## Coding behavior

- Implement only after architecture choice is confirmed.
- Follow existing project conventions and discovered patterns.
- Keep changes modular and focused by concern.
- Run a quality review pass after implementation and present findings.
- Maintain explicit progress tracking throughout the seven phases.

## Guardrails

- Do not skip clarification and approval gates.
- Prefer simple, maintainable implementation over speculative complexity.
- Track progress across phases and close with a concrete summary.
