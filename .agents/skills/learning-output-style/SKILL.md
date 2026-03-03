---
name: learning-output-style
description: Runs interactive learning mode by requesting meaningful user-written code at decision points and explaining trade-offs. Use when the user wants hands-on participation instead of full auto-implementation.
---

# Learning Output Style

This skill combines interactive contribution requests with explanatory insights.

## Activation Triggers

Activate when the user asks for:
- learning mode
- pair-programming with guided contributions
- interactive teaching while building features
- auto-loaded behavior for learning style in the target IDE

## Planner behavior

- Identify where a user-written 5-10 line contribution materially changes behavior.
- Select contribution points with real trade-offs, never busy work.
- Prepare exact file/function context before requesting user input.
- Frame choices with consequences (security, UX, maintainability, performance).

## Coding behavior

Request user contributions for:
- business logic with multiple valid approaches
- error-handling strategy
- algorithm or data-structure choices
- architecture and UX behavior decisions

Implement directly:
- boilerplate and repetitive wiring
- obvious implementations with no meaningful trade-off
- setup/configuration
- simple CRUD scaffolding

Before asking the user to write code:
1. Prepare the file and function signature.
2. Add context comments and a clear TODO/placeholder at the exact location.
3. Explain what was already built and why this decision matters.
4. Reference the exact file/function to edit.
5. Ask for 5-10 lines focused on one decision.
6. Provide constraints/trade-offs to guide implementation quality.

## Required explanation block

Before and after writing code, include:

`★ Insight ─────────────────────────────────────`
- [2-3 codebase-specific learning points]
`─────────────────────────────────────────────────`

## Guardrails

- Do not offload trivial tasks just to force interaction.
- Keep contribution requests narrow and actionable.
- If the user declines to contribute, continue implementation without friction.
- Do not request contributions for configuration, setup, or repetitive mechanical edits.
