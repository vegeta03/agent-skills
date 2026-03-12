# Suggested Agent Topology

This reference mirrors the source plugin's role split and can be adapted for any IDE that supports planner/coding agents.

## Exploration Phase

Run 2-3 exploration passes in parallel:
- similar-feature tracing
- architecture/abstraction mapping
- UX/testing/extension-point analysis

Each pass should return a short list of essential files to read.

## Architecture Phase

Run 2-3 architecture passes in parallel:
- minimal-change approach
- clean-architecture approach
- pragmatic balance approach

Then synthesize into one recommendation for user approval.

## Quality Phase

Run 3 review perspectives:
- simplicity/DRY/elegance
- bugs/functional correctness
- project conventions and abstractions

Report highest-severity issues first and request user decision: fix now, fix later, or proceed as-is.
