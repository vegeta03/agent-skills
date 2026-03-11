---
name: ralph-wiggum
description: Implementation of the Ralph Wiggum technique for iterative, self-referential AI development loops. Run the AI assistant in a while-true loop with the same prompt until task completion. Use this skill when the user wants to set up an iterative development loop, wants the AI to keep working on a task until it's done, mentions ralph or ralph-wiggum, wants continuous iteration on a task with automatic retry, or needs a self-correcting development workflow. Make sure to use this skill whenever the user mentions iterative loops, continuous development, self-referential loops, persistent iteration, or automated task completion loops.
---

# Ralph Wiggum — Iterative Development Loops

Implementation of the Ralph Wiggum technique for iterative, self-referential AI development loops.

> **Universal Compatibility Note**: This skill works with any AI coding assistant and any AI model. The loop mechanism uses shell scripts that work with any CLI-based AI assistant. If your environment doesn't support the shell-based stop hook pattern, the same iterative workflow can be implemented manually by re-submitting the same prompt after each AI response.

## What is Ralph?

Ralph is a development methodology based on continuous AI agent loops. As Geoffrey Huntley describes it: **"Ralph is a Bash loop"** — a simple `while true` that repeatedly feeds an AI agent a prompt, allowing it to iteratively improve its work until completion.

The technique is named after Ralph Wiggum from The Simpsons, embodying the philosophy of persistent iteration despite setbacks.

### Core Concept

The loop works by intercepting the AI assistant's exit attempts and feeding the SAME prompt back:

```bash
# You run ONCE:
# Start a ralph loop with: "Your task description" --completion-promise "DONE"

# Then the AI assistant automatically:
# 1. Works on the task
# 2. Tries to exit
# 3. Loop mechanism blocks exit
# 4. Same prompt fed back
# 5. Repeat until completion
```

This creates a **self-referential feedback loop** where:
- The prompt never changes between iterations
- The AI's previous work persists in files
- Each iteration sees modified files and git history
- The AI autonomously improves by reading its own past work in files

## Quick Start

To start a Ralph loop, use the setup script from `scripts/setup-ralph-loop.sh`:

```bash
# Example: Build a REST API with iterative refinement
scripts/setup-ralph-loop.sh "Build a REST API for todos. Requirements: CRUD operations, input validation, tests. Output <promise>COMPLETE</promise> when done." --completion-promise "COMPLETE" --max-iterations 50
```

The AI will:
- Implement the API iteratively
- Run tests and see failures
- Fix bugs based on test output
- Iterate until all requirements met
- Output the completion promise when done

## Commands

### Start a Ralph Loop

**Usage:**
```bash
scripts/setup-ralph-loop.sh "<prompt>" --max-iterations <n> --completion-promise "<text>"
```

**Options:**
- `--max-iterations <n>` — Stop after N iterations (default: unlimited)
- `--completion-promise <text>` — Phrase that signals completion
- `-h, --help` — Show help message

### Cancel a Ralph Loop

To cancel an active Ralph loop:

1. Check if `.claude/ralph-loop.local.md` exists
2. If it exists, read it to get the current iteration number from the `iteration:` field
3. Remove the file: `rm .claude/ralph-loop.local.md`
4. Report: "Cancelled Ralph loop (was at iteration N)"

If the state file doesn't exist, there is no active Ralph loop.

## How the Loop Works

### State File

The setup script creates a state file at `.claude/ralph-loop.local.md` with YAML frontmatter:

```markdown
---
active: true
iteration: 1
max_iterations: 50
completion_promise: "COMPLETE"
started_at: "2024-01-01T00:00:00Z"
---

Your task prompt goes here
```

### Stop Hook

The stop hook script (`scripts/stop-hook.sh`) intercepts exit attempts:

1. Checks if `.claude/ralph-loop.local.md` exists (no file = allow exit)
2. Validates the state file's numeric fields
3. Checks if max iterations reached (stops if so)
4. Reads the last assistant message from the transcript
5. Checks for completion promise in `<promise>` XML tags
6. If not complete: increments iteration, feeds the same prompt back
7. Outputs a JSON decision to block exit and continue the loop

### Completion Promise

To signal completion, the AI must output a `<promise>` tag:

```
<promise>TASK COMPLETE</promise>
```

The stop hook looks for this specific tag. Without it (or `--max-iterations`), Ralph runs indefinitely.

**CRITICAL RULE**: If a completion promise is set, the AI may ONLY output it when the statement is completely and unequivocally TRUE. Do not output false promises to escape the loop, even if the AI thinks it's stuck or should exit for other reasons. The loop is designed to continue until genuine completion.

### Self-Reference Mechanism

The "loop" doesn't mean the AI talks to itself. It means:
- Same prompt repeated
- AI's work persists in files
- Each iteration sees previous attempts
- Builds incrementally toward goal

## Prompt Writing Best Practices

### 1. Clear Completion Criteria

❌ Bad: "Build a todo API and make it good."

✅ Good:
```markdown
Build a REST API for todos.

When complete:
- All CRUD endpoints working
- Input validation in place
- Tests passing (coverage > 80%)
- README with API docs
- Output: <promise>COMPLETE</promise>
```

### 2. Incremental Goals

❌ Bad: "Create a complete e-commerce platform."

✅ Good:
```markdown
Phase 1: User authentication (JWT, tests)
Phase 2: Product catalog (list/search, tests)
Phase 3: Shopping cart (add/remove, tests)

Output <promise>COMPLETE</promise> when all phases done.
```

### 3. Self-Correction

❌ Bad: "Write code for feature X."

✅ Good:
```markdown
Implement feature X following TDD:
1. Write failing tests
2. Implement feature
3. Run tests
4. If any fail, debug and fix
5. Refactor if needed
6. Repeat until all green
7. Output: <promise>COMPLETE</promise>
```

### 4. Escape Hatches

Always use `--max-iterations` as a safety net to prevent infinite loops on impossible tasks:

```bash
# Recommended: Always set a reasonable iteration limit
scripts/setup-ralph-loop.sh "Try to implement feature X" --max-iterations 20

# In your prompt, include what to do if stuck:
# "After 15 iterations, if not complete:
#  - Document what's blocking progress
#  - List what was attempted
#  - Suggest alternative approaches"
```

**Note**: The `--completion-promise` uses exact string matching, so you cannot use it for multiple completion conditions (like "SUCCESS" vs "BLOCKED"). Always rely on `--max-iterations` as your primary safety mechanism.

## Philosophy

Ralph embodies several key principles:

### 1. Iteration > Perfection
Don't aim for perfect on first try. Let the loop refine the work.

### 2. Failures Are Data
"Deterministically bad" means failures are predictable and informative. Use them to tune prompts.

### 3. Operator Skill Matters
Success depends on writing good prompts, not just having a good model.

### 4. Persistence Wins
Keep trying until success. The loop handles retry logic automatically.

## When to Use Ralph

**Good for:**
- Well-defined tasks with clear success criteria
- Tasks requiring iteration and refinement (e.g., getting tests to pass)
- Greenfield projects where you can walk away
- Tasks with automatic verification (tests, linters)

**Not good for:**
- Tasks requiring human judgment or design decisions
- One-shot operations
- Tasks with unclear success criteria
- Production debugging (use targeted debugging instead)

## Real-World Results

- Successfully generated 6 repositories overnight in Y Combinator hackathon testing
- One $50k contract completed for $297 in API costs
- Created entire programming language ("cursed") over 3 months using this approach

## Bundled Scripts

This skill includes two shell scripts in the `scripts/` directory:

- **`scripts/setup-ralph-loop.sh`** — Initializes a Ralph loop by parsing arguments, creating the state file, and displaying setup information
- **`scripts/stop-hook.sh`** — The stop hook that intercepts exit attempts, checks completion, and feeds the prompt back for the next iteration

These scripts are designed for environments with CLI-based AI assistants that support stop hooks. For environments without stop hook support, the iterative pattern can be replicated by manually re-submitting the prompt.

## Learn More

- Original technique: https://ghuntley.com/ralph/
- Ralph Orchestrator: https://github.com/mikeyobrien/ralph-orchestrator

## Credits

Original plugin by Daisy Hollman (Anthropic). Converted to a universal, platform-agnostic Agent Skill format.
