# Review Output Contract

## Findings-first format

1. `Critical`: correctness, security, or guaranteed failure
2. `Important`: high-confidence defects with meaningful impact
3. If none: explicit no-issues statement

## Per-finding fields

- title
- confidence score
- file path and line reference
- why this is a problem
- concrete fix direction

## Response quality rules

- one unique issue -> one finding/comment
- keep wording factual and specific
- avoid long prose and avoid repeating the diff summary

## Exact No-Issues Text

Use this exact line when no validated issues remain:

`No issues found. Checked for bugs and CLAUDE.md compliance.`

## Comment Mode Output

When summary comment mode is enabled and no issues are found, use:

```markdown
## Code review

No issues found. Checked for bugs and CLAUDE.md compliance.
```
