# Claude Stop-Hook Parity Boundaries

This document explains what can and cannot be reproduced outside Claude plugin hooks.

## Native Claude Behavior (not portable)

Original Ralph plugin capabilities include:
- Stop-hook interception that blocks session exit.
- Automatic prompt replay using transcript-derived context.
- In-session state file updates coordinated by hook scripts.

These depend on Claude-specific hook APIs and transcript plumbing.

## Cross-IDE Portable Approximation

Use explicit loop checkpoints:
1. Keep a fixed prompt and explicit loop state.
2. Run one iteration at a time.
3. Execute deterministic verification checks.
4. Continue only when promise is not yet true.
5. Stop on exact promise match or max-iteration limit.

## Recommended State Shape

```yaml
iteration: 1
max_iterations: 20
completion_promise: "COMPLETE"
prompt: "..."
```

## Behavioral Guarantee

Portable mode preserves:
- same prompt intent across iterations
- truth-bound completion promise
- bounded/unbounded loop semantics by policy

Portable mode cannot guarantee:
- automatic exit interception without agent cooperation
- transcript-level hook control
