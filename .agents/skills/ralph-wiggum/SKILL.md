---
name: ralph-wiggum
description: Runs iterative same-prompt development loops with explicit completion promises and max-iteration safety. Use for autonomous refinement tasks with measurable completion criteria.
---

# Ralph Wiggum

This skill adapts Ralph loops to cross-IDE agents without relying on Claude stop hooks.

Safety and stopping guidance is in:
- `references/loop-safety.md`
- `references/claude-stop-hook-parity.md`

## Activation Triggers

Activate when the user asks for:
- Ralph loop style iteration
- autonomous repeated refinement until completion
- persistent iteration on a fixed prompt

## Planner behavior

Define loop contract before execution:
- fixed prompt text
- completion promise text
- max iterations
- verification criteria (tests/checks) per iteration
- stuck policy when completion cannot be reached

## Coding behavior

Run iterative loop protocol:
1. Re-read the same task prompt each cycle.
2. Execute one focused iteration.
3. Run verification checks.
4. If completion promise is true, emit `<promise>TEXT</promise>` and stop.
5. Else continue until max iterations.

If an in-session state file protocol is used, keep at minimum:
- `iteration`
- `max_iterations`
- `completion_promise`
- immutable core prompt text

When max iterations are reached without completion:
- stop loop
- provide blocker summary
- list attempted fixes and recommended next steps

## Guardrails

- Never emit a completion promise unless it is fully true.
- Do not silently change the core task prompt mid-loop.
- Prefer deterministic checks (tests, builds, assertions) for completion.
- Treat hook-based stop interception as non-portable and emulate through explicit iterative checkpoints.
