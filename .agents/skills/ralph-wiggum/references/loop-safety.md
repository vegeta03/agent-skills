# Loop Safety

## Completion Promise Contract

- Promise format: `<promise>YOUR_TEXT</promise>`
- Promise must be exact and truthful.
- Never use false promise output to force loop termination.
- If the completion text is configured, compare exact normalized value before stopping.

## Max Iteration Safety

- Always set a practical max iteration value.
- Use lower limits for unknown tasks and raise only when progress is measurable.
- `0` may be treated as unlimited only when user explicitly accepts the risk.

## Stuck Protocol

If progress stalls:
- summarize blockers
- list evidence from failed checks
- propose a revised prompt or narrower scope
- request user decision to continue, pivot, or stop

## Portability Note

Claude-specific stop-hook interception is not portable.  
Cross-IDE implementations must use explicit iterative planning and checkpointed continuation.

## Integrity Rules

- Never bypass loop constraints by emitting a false `<promise>` tag.
- Preserve state consistency between iterations.
- Stop immediately if state becomes corrupted and request operator intervention.
