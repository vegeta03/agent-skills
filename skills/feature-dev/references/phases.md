# Seven-Phase Workflow

## Phase 1: Discovery

- confirm problem, outcomes, and constraints
- restate scope before moving forward
- create/update task tracking checklist

## Phase 2: Codebase Exploration

- inspect similar features and architecture boundaries
- identify essential files and conventions
- run 2-3 exploration passes with different focus areas

## Phase 3: Clarifying Questions (mandatory)

- list edge cases, error behavior, integration points, compatibility expectations
- wait for answers before architecture design
- do not proceed until ambiguities are resolved

## Phase 4: Architecture Design

- provide 2-3 viable approaches
- compare trade-offs
- recommend one approach
- ask user to choose
- capture why recommendation fits project conventions

## Phase 5: Implementation (approval-gated)

- start only after explicit user approval
- implement according to chosen architecture
- read all high-priority files identified during exploration

## Phase 6: Quality Review

- review for correctness, simplicity, and convention adherence
- present issues and ask whether to fix now or defer
- run parallel review perspectives when available (correctness, simplicity, conventions)

## Phase 7: Summary

- summarize what shipped, key decisions, modified files, and next steps
- close out tracking checklist
