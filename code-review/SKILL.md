---
name: code-review
description: Automated code review for pull requests using multiple specialized agents with confidence-based scoring to filter false positives. Use this skill when the user wants to review a pull request, perform code review, check for bugs in PR changes, verify project guideline compliance, or automate PR review. Make sure to use this skill whenever the user mentions code review, PR review, reviewing changes, checking a pull request, or auditing code changes.
---

# Code Review

Automated code review for pull requests using multiple specialized review tasks with confidence-based scoring to filter false positives and ensure only high-quality, actionable feedback is produced.

> **Universal Compatibility Note**: This skill works with any AI coding assistant and any AI model. Where this skill references "launching agents" or "parallel tasks," adapt to whatever your environment supports — if parallel execution isn't available, run tasks serially instead. The core review workflow remains the same regardless of platform. This skill uses GitHub CLI (`gh`) for GitHub integration; adapt the specific commands if using a different Git hosting platform.

## Overview

This skill automates pull request review by launching multiple tasks in parallel to independently audit changes from different perspectives. It uses confidence scoring to filter out false positives, ensuring only high-quality, actionable feedback is posted.

## Review Workflow

Follow these steps precisely:

### Step 1: Pre-Flight Check

Launch a quick check task to determine if any of the following are true:
- The pull request is closed
- The pull request is a draft
- The pull request does not need code review (e.g., automated PR, trivial change that is obviously correct)
- The AI assistant has already commented on this PR (check `gh pr view <PR> --comments` for existing comments)

If any condition is true, stop and do not proceed.

Note: Still review AI-generated PRs.

### Step 2: Gather Project Guidelines

Launch a task to return a list of file paths (not their contents) for all relevant project guideline files including:
- The root project guidelines file (e.g., CLAUDE.md, AGENTS.md, CONVENTIONS.md, or equivalent), if it exists
- Any guideline files in directories containing files modified by the pull request

### Step 3: Summarize Changes

Launch a task to view the pull request and return a summary of the changes.

### Step 4: Independent Review (4 Parallel Tasks)

Launch 4 tasks in parallel (or serially) to independently review the changes. Each task should return the list of issues, where each issue includes a description and the reason it was flagged.

**Tasks 1 & 2: Project Guidelines Compliance**
Audit changes for project guidelines compliance in parallel. When evaluating guideline compliance for a file, only consider guideline files that share a file path with the file or its parents.

**Task 3: Bug Detection (Diff-Only)**
Scan for obvious bugs. Focus only on the diff itself without reading extra context. Flag only significant bugs; ignore nitpicks and likely false positives. Do not flag issues that cannot be validated without looking at context outside of the git diff.

**Task 4: Bug Detection (Context-Aware)**
Look for problems that exist in the introduced code. This could be security issues, incorrect logic, etc. Only look for issues that fall within the changed code.

**CRITICAL: Only flag HIGH SIGNAL issues.** Flag issues where:
- The code will fail to compile or parse (syntax errors, type errors, missing imports, unresolved references)
- The code will definitely produce wrong results regardless of inputs (clear logic errors)
- Clear, unambiguous project guideline violations where you can quote the exact rule being broken

Do NOT flag:
- Code style or quality concerns
- Potential issues that depend on specific inputs or state
- Subjective suggestions or improvements

If you are not certain an issue is real, do not flag it. False positives erode trust and waste reviewer time.

In addition to the above, each task should be given the PR title and description for context regarding the author's intent.

### Step 5: Validate Issues

For each issue found in Step 4 by Tasks 3 and 4, launch parallel validation tasks. These tasks should get the PR title and description along with a description of the issue. The task's job is to review the issue to validate that the stated issue is truly an issue with high confidence. For example, if an issue such as "variable is not defined" was flagged, the task should validate that this is actually true in the code. Another example would be guideline issues — the task should validate that the guideline rule that was violated is scoped for this file and is actually violated.

Use higher-capability model tasks for bugs and logic issues, and standard model tasks for guideline violations.

### Step 6: Filter

Filter out any issues that were not validated in Step 5. This gives the final list of high-signal issues for the review.

### Step 7: Output Results

Output a summary of the review findings to the terminal:
- If issues were found, list each issue with a brief description.
- If no issues were found, state: "No issues found. Checked for bugs and project guideline compliance."

If `--comment` argument was NOT provided, stop here. Do not post any GitHub comments.

If `--comment` argument IS provided and NO issues were found, post a summary comment using `gh pr comment` and stop.

If `--comment` argument IS provided and issues were found, continue to Step 8.

### Step 8: Prepare Comments

Create a list of all comments that you plan on leaving. This is only for internal review to ensure you are comfortable with the comments. Do not post this list anywhere.

### Step 9: Post Inline Comments

Post inline comments for each issue on the pull request. For each comment:
- Provide a brief description of the issue
- For small, self-contained fixes, include a committable suggestion block
- For larger fixes (6+ lines, structural changes, or changes spanning multiple locations), describe the issue and suggested fix without a suggestion block
- Never post a committable suggestion UNLESS committing the suggestion fixes the issue entirely. If follow-up steps are required, do not leave a committable suggestion.

**IMPORTANT: Only post ONE comment per unique issue. Do not post duplicate comments.**

## False Positive Filter

Use this list when evaluating issues in Steps 4 and 5 (these are false positives, do NOT flag):

- Pre-existing issues not introduced in PR
- Something that appears to be a bug but is actually correct
- Pedantic nitpicks that a senior engineer would not flag
- Issues that a linter will catch (do not run the linter to verify)
- General code quality concerns (e.g., lack of test coverage, general security issues) unless explicitly required in project guidelines
- Issues mentioned in project guidelines but explicitly silenced in the code (e.g., via a lint ignore comment)

## Confidence Scoring

Each issue is independently scored 0-100:
- **0**: Not confident, false positive
- **25**: Somewhat confident, might be real
- **50**: Moderately confident, real but minor
- **75**: Highly confident, real and important
- **100**: Absolutely certain, definitely real

Scoring considers evidence strength and verification. The default threshold of 80 filters low-confidence issues. For project guideline issues: verify the guideline explicitly mentions the flagged behavior.

## Review Comment Format

```markdown
## Code review

Found 3 issues:

1. Missing error handling for OAuth callback (project guideline says "Always handle OAuth errors")

https://github.com/owner/repo/blob/abc123.../src/auth.ts#L67-L72

2. Memory leak: OAuth state not cleaned up (bug due to missing cleanup in finally block)

https://github.com/owner/repo/blob/abc123.../src/auth.ts#L88-L95

3. Inconsistent naming pattern (conventions file says "Use camelCase for functions")

https://github.com/owner/repo/blob/abc123.../src/utils.ts#L23-L28
```

## Link Format

When linking to code in comments, follow this format precisely (otherwise Markdown preview won't render correctly):
```
https://github.com/owner/repo/blob/[full-sha]/path/file.ext#L[start]-L[end]
```
- Requires full git SHA (not abbreviated)
- Must use `#L` notation
- Line range format is `L[start]-L[end]`
- Provide at least 1 line of context before and after, centered on the line you are commenting about

## Notes

- Use `gh` CLI to interact with GitHub (e.g., fetch pull requests, create comments). Do not use web fetch.
- Create a todo list before starting.
- Cite and link each issue in inline comments (e.g., if referring to a project guideline file, include a link to it).
- If no issues are found and `--comment` argument is provided, post a comment reading: "No issues found. Checked for bugs and project guideline compliance."

## Best Practices

- Maintain clear project guideline files for better compliance checking
- Trust the 80+ confidence threshold — false positives are filtered
- Run on all non-trivial pull requests
- Review agent findings as a starting point for human review
- Update project guidelines based on recurring review patterns

## When to Use

**Good for:**
- All pull requests with meaningful changes
- PRs touching critical code paths
- PRs from multiple contributors
- PRs where guideline compliance matters

**Not good for:**
- Closed or draft PRs (automatically skipped anyway)
- Trivial automated PRs (automatically skipped)
- Urgent hotfixes requiring immediate merge
- PRs already reviewed (automatically skipped)

## Configuration

### Adjusting Confidence Threshold
The default threshold is 80. To adjust, modify the filter step to use your preferred threshold (0-100).

### Customizing Review Focus
You can customize the review by modifying the task prompts:
- Add security-focused tasks
- Add performance analysis tasks
- Add accessibility checking tasks
- Add documentation quality checks

## Requirements

- Git repository with remote hosting integration (GitHub, GitLab, etc.)
- Platform CLI tool installed and authenticated (e.g., `gh` for GitHub)
- Project guideline files (optional but recommended for guideline checking)

## Troubleshooting

### Review takes too long
**Issue**: Tasks are slow on large PRs
**Solution**: Normal for large changes — tasks run in parallel. 4 independent tasks ensure thoroughness. Consider splitting large PRs into smaller ones.

### Too many false positives
**Issue**: Review flags issues that aren't real
**Solution**: Default threshold is 80 (already filters most false positives). Make project guideline files more specific about what matters. Consider if the flagged issue is actually valid.

### No review comment posted
**Issue**: Review runs but no comment appears
**Solution**: Check if PR is closed (reviews skipped), PR is draft (reviews skipped), PR is trivial/automated (reviews skipped), PR already has review (reviews skipped), or no issues scored ≥80 (no comment needed).

## Credits

Original plugin by Boris Cherny (Anthropic). Converted to a universal, platform-agnostic Agent Skill format.
