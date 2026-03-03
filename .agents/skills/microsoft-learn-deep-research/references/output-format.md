# Output Format

Write each research result to:
- `research/microsoft-learn/YYYY-MM-DD-<topic-slug>.md`

`<topic-slug>` should be lowercase kebab-case and specific to the user query.

## Report template

Use this structure:

```markdown
# <Research title>

## Goal
- User objective
- Constraints and scope

## Clarifications
- Answers to clarifying questions
- Assumptions (if any)

## Findings
- Key finding with citation
- Key finding with citation

## Implementation Notes
- Setup/configuration steps
- Production caveats and limits
- Security/operations considerations

## Code Samples
- Sample summary + source URL
- Why it applies to this scenario

## Gaps And Next Queries
- Unresolved questions
- Next retrieval queries to run

## Sources
- <URL 1>
- <URL 2>
- <URL 3>
```

## Citation and traceability rules

- Every critical recommendation must map to at least one source URL.
- Prefer official Microsoft Learn or Microsoft product documentation URLs.
- Keep source links in `## Sources` and inline near major claims when useful.
- If sources conflict, call out the conflict and explain which source was prioritized.
