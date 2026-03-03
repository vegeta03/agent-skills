# GitHub PR Workflow

## Skip Gates

Stop early when any is true:
- PR is closed
- PR is draft
- change is trivial/automated/non-actionable
- same automated reviewer already commented on this PR

## Required Review Topology

- Reviewer A: CLAUDE/AGENTS compliance
- Reviewer B: CLAUDE/AGENTS compliance
- Reviewer C: bug-focused diff-only scan
- Reviewer D: bug-focused changed-code scan

Each candidate issue from bug/compliance reviewers must be validated in a separate pass before final inclusion.

## Comment Posting Semantics

- If comment mode is disabled: print terminal summary only.
- If comment mode is enabled and no issues: post summary comment only.
- If comment mode is enabled and issues exist: post one inline comment per unique issue.

## Suggestion Block Rule

Use committable suggestion blocks only when applying the suggestion fully resolves the issue with no follow-up required.
