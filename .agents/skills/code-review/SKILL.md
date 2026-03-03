---
name: code-review
description: Performs high-signal pull request and change review with confidence filtering, validation, and concise actionable findings. Use for PR review requests and quality gates before merge.
---

# Code Review

Review pull requests or diffs for correctness and explicit project-rule compliance with a strict high-signal threshold.

Detailed criteria live in:
- `references/high-signal.md`
- `references/review-output.md`
- `references/github-pr-workflow.md`
- `references/link-format.md`

## Activation Triggers

Activate when the user asks to:
- review a PR or diff
- identify bugs/regressions
- validate rule or convention compliance

## Planner behavior

1. Confirm review scope (`PR`, branch diff, or file set) and whether comment posting is requested.
2. Apply skip checks early:
   - closed/draft/non-actionable PR
   - trivial automated changes
   - already reviewed by the same automated workflow
3. Gather governing rules scoped to changed files (`CLAUDE.md`, `AGENTS.md`, and repo instructions).
4. Plan independent review passes:
   - 2 guideline-compliance reviewers
   - 2 bug-focused reviewers
5. Plan a separate validation pass for each candidate issue before final reporting.

## Coding behavior

Execute review in stages:
1. Summarize intent and changed areas.
2. Run independent review passes (compliance + bug-focused) in parallel when available.
3. Validate each candidate issue before reporting.
4. Filter to confidence >= 80 only.
5. Deduplicate findings: one unique issue -> one finding/comment.
6. If no issues remain, use exact no-issues wording from `references/review-output.md`.
7. If comment mode is requested:
   - post summary comment when no issues
   - post one inline comment per validated issue
   - only include committable suggestion blocks for fully-contained fixes

## Guardrails

- Prefer no finding over a low-confidence finding.
- Do not report style nits unless explicitly required by project rules.
- Distinguish introduced issues from pre-existing issues.
- Do not run exploratory tool checks; use only task-required calls.
- Keep output concise, severity-ordered, and fix-oriented.
