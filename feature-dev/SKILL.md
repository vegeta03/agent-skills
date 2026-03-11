---
name: feature-dev
description: Comprehensive feature development workflow with specialized agents for codebase exploration, architecture design, and quality review. Use this skill when the user wants to build a new feature, especially one that touches multiple files, requires architectural decisions, involves complex integrations with existing code, or has somewhat unclear requirements. Guides through 7 structured phases from discovery to completion. Make sure to use this skill whenever the user mentions building a feature, adding a new capability, implementing a new module, or asks for a guided development workflow.
---

# Feature Development

A comprehensive, structured workflow for feature development with specialized agents for codebase exploration, architecture design, and quality review.

> **Universal Compatibility Note**: This skill works with any AI coding assistant (Cursor, Windsurf, Cline, Aider, JetBrains AI, GitHub Copilot, or any IDE/editor with AI integration) and any AI model. Where this skill references "launching agents" or "parallel tasks," adapt to whatever your environment supports — if parallel execution isn't available, run tasks serially instead. The core workflow remains the same regardless of platform.

## Philosophy

Building features requires more than just writing code. You need to:
- **Understand the codebase** before making changes
- **Ask questions** to clarify ambiguous requirements
- **Design thoughtfully** before implementing
- **Review for quality** after building

This skill embeds these practices into a structured 7-phase workflow.

## Core Principles

- **Ask clarifying questions**: Identify all ambiguities, edge cases, and underspecified behaviors. Ask specific, concrete questions rather than making assumptions. Wait for user answers before proceeding with implementation. Ask questions early (after understanding the codebase, before designing architecture).
- **Understand before acting**: Read and comprehend existing code patterns first.
- **Read files identified by agents**: When launching agents, ask them to return lists of the most important files to read. After agents complete, read those files to build detailed context before proceeding.
- **Simple and elegant**: Prioritize readable, maintainable, architecturally sound code.
- **Track progress**: Use todo lists or task tracking throughout all phases.

---

## The 7-Phase Workflow

### Phase 1: Discovery

**Goal**: Understand what needs to be built

**Actions**:
1. Create a todo list with all phases
2. If the feature is unclear, ask the user for:
   - What problem are they solving?
   - What should the feature do?
   - Any constraints or requirements?
3. Summarize understanding and confirm with the user

**Example:**
```
User: Add caching
Assistant: Let me understand what you need...
         - What should be cached? (API responses, computed values, etc.)
         - What are your performance requirements?
         - Do you have a preferred caching solution?
```

---

### Phase 2: Codebase Exploration

**Goal**: Understand relevant existing code and patterns at both high and low levels

**Actions**:
1. Launch 2-3 exploration tasks in parallel (or serially if parallel isn't available). Each task should use the `agents/code-explorer.md` reference and:
   - Trace through the code comprehensively, focusing on getting a comprehensive understanding of abstractions, architecture, and flow of control
   - Target a different aspect of the codebase (e.g., similar features, high-level understanding, architectural understanding, user experience, etc.)
   - Include a list of 5-10 key files to read

   **Example task prompts**:
   - "Find features similar to [feature] and trace through their implementation comprehensively"
   - "Map the architecture and abstractions for [feature area], tracing through the code comprehensively"
   - "Analyze the current implementation of [existing feature/area], tracing through the code comprehensively"
   - "Identify UI patterns, testing approaches, or extension points relevant to [feature]"

2. Once the tasks return, read all files identified by the agents to build deep understanding
3. Present comprehensive summary of findings and patterns discovered

**Example output:**
```
Found similar features:
- User authentication (src/auth/): Uses JWT tokens, middleware pattern
- Session management (src/session/): Redis-backed, 24hr expiry
- API security (src/api/middleware/): Rate limiting, CORS

Key files to understand:
- src/auth/AuthService.ts:45 - Core authentication logic
- src/middleware/authMiddleware.ts:12 - Request authentication
- src/config/security.ts:8 - Security configuration
```

---

### Phase 3: Clarifying Questions

**Goal**: Fill in gaps and resolve all ambiguities before designing

**CRITICAL**: This is one of the most important phases. DO NOT SKIP.

**Actions**:
1. Review the codebase findings and original feature request
2. Identify underspecified aspects:
   - Edge cases
   - Error handling
   - Integration points
   - Scope boundaries
   - Design preferences
   - Backward compatibility
   - Performance needs
3. **Present all questions to the user in a clear, organized list**
4. **Wait for answers before proceeding to architecture design**

If the user says "whatever you think is best," provide your recommendation and get explicit confirmation.

**Example:**
```
Before designing the architecture, I need to clarify:

1. OAuth provider: Which OAuth providers? (Google, GitHub, custom?)
2. User data: Store OAuth tokens or just user profile?
3. Existing auth: Replace current auth or add alongside?
4. Sessions: Integrate with existing session management?
5. Error handling: How to handle OAuth failures?
```

**Critical**: This phase ensures nothing is ambiguous before design begins.

---

### Phase 4: Architecture Design

**Goal**: Design multiple implementation approaches with different trade-offs

**Actions**:
1. Launch 2-3 architecture tasks in parallel (or serially) using the `agents/code-architect.md` reference, each with different focuses:
   - **Minimal changes**: Smallest change, maximum reuse
   - **Clean architecture**: Maintainability, elegant abstractions
   - **Pragmatic balance**: Speed + quality
2. Review all approaches and form your opinion on which fits best for this specific task (consider: small fix vs large feature, urgency, complexity, team context)
3. Present to user: brief summary of each approach, trade-offs comparison, **your recommendation with reasoning**, concrete implementation differences
4. **Ask user which approach they prefer**

**Example output:**
```
I've designed 3 approaches:

Approach 1: Minimal Changes
- Extend existing AuthService with OAuth methods
- Add new OAuth routes to existing auth router
- Minimal refactoring required
Pros: Fast, low risk
Cons: Couples OAuth to existing auth, harder to test

Approach 2: Clean Architecture
- New OAuthService with dedicated interface
- Separate OAuth router and middleware
- Refactor AuthService to use common interface
Pros: Clean separation, testable, maintainable
Cons: More files, more refactoring

Approach 3: Pragmatic Balance
- New OAuthProvider abstraction
- Integrate into existing AuthService
- Minimal refactoring, good boundaries
Pros: Balanced complexity and cleanliness
Cons: Some coupling remains

Recommendation: Approach 3 - gives you clean boundaries without
excessive refactoring, and fits your existing architecture well.

Which approach would you like to use?
```

---

### Phase 5: Implementation

**Goal**: Build the feature

**DO NOT START WITHOUT USER APPROVAL**

**Actions**:
1. Wait for explicit user approval
2. Read all relevant files identified in previous phases
3. Implement following chosen architecture
4. Follow codebase conventions strictly
5. Write clean, well-documented code
6. Update todos as you progress

**Notes:**
- Implementation only starts after the user approves
- Follow patterns discovered in Phase 2
- Use architecture designed in Phase 4
- Continuously track progress

---

### Phase 6: Quality Review

**Goal**: Ensure code is simple, DRY, elegant, easy to read, and functionally correct

**Actions**:
1. Launch 3 review tasks in parallel (or serially) using the `agents/code-reviewer.md` reference, each with a different focus:
   - **Simplicity/DRY/Elegance**: Code quality and maintainability
   - **Bugs/Functional Correctness**: Logic errors and correctness issues
   - **Project Conventions/Abstractions**: Standards and patterns
2. Consolidate findings and identify highest severity issues that you recommend fixing
3. **Present findings to user and ask what they want to do** (fix now, fix later, or proceed as-is)
4. Address issues based on user decision

**Example output:**
```
Code Review Results:

High Priority Issues:
1. Missing error handling in OAuth callback (src/auth/oauth.ts:67)
2. Memory leak: OAuth state not cleaned up (src/auth/oauth.ts:89)

Medium Priority:
1. Could simplify token refresh logic (src/auth/oauth.ts:120)
2. Consider extracting OAuth config validation

All tests pass. Code follows project conventions.

What would you like to do?
```

---

### Phase 7: Summary

**Goal**: Document what was accomplished

**Actions**:
1. Mark all todos complete
2. Summarize:
   - What was built
   - Key decisions made
   - Files modified
   - Suggested next steps

**Example:**
```
Feature Complete: OAuth Authentication

What was built:
- OAuth provider abstraction supporting Google and GitHub
- OAuth routes and middleware integrated with existing auth
- Token refresh and session integration
- Error handling for all OAuth flows

Key decisions:
- Used pragmatic approach with OAuthProvider abstraction
- Integrated with existing session management
- Added OAuth state to prevent CSRF

Files modified:
- src/auth/OAuthProvider.ts (new)
- src/auth/AuthService.ts
- src/routes/auth.ts
- src/middleware/authMiddleware.ts

Suggested next steps:
- Add tests for OAuth flows
- Add more OAuth providers (Microsoft, Apple)
- Update documentation
```

---

## Agents (Subagent Reference Files)

This skill includes three specialized agent reference files in the `agents/` subdirectory. Read the relevant file when performing that agent's role:

### `agents/code-explorer.md`

**Purpose**: Deeply analyzes existing codebase features by tracing execution paths

**When used**: Automatically in Phase 2, or manually when exploring code

**Output**: Entry points with file:line references, step-by-step execution flow, key components and their responsibilities, architecture insights, list of essential files to read

### `agents/code-architect.md`

**Purpose**: Designs feature architectures and implementation blueprints

**When used**: Automatically in Phase 4, or manually for architecture design

**Output**: Patterns and conventions found, architecture decision with rationale, complete component design, implementation map with specific files, build sequence with phases

### `agents/code-reviewer.md`

**Purpose**: Reviews code for bugs, quality issues, and project conventions

**When used**: Automatically in Phase 6, or manually after writing code

**Output**: Critical issues (confidence 75-100), important issues (confidence 50-74), specific fixes with file:line references, project guideline references

---

## Usage Patterns

### Full workflow (recommended for new features):
Tell the AI assistant: "Use the feature-dev skill to add rate limiting to API endpoints"

Let the workflow guide you through all 7 phases.

### Manual agent invocation:

**Explore a feature:**
"Use the code-explorer agent to trace how authentication works"

**Design architecture:**
"Use the code-architect agent to design the caching layer"

**Review code:**
"Use the code-reviewer agent to check my recent changes"

---

## Best Practices

1. **Use the full workflow for complex features**: The 7 phases ensure thorough planning
2. **Answer clarifying questions thoughtfully**: Phase 3 prevents future confusion
3. **Choose architecture deliberately**: Phase 4 gives you options for a reason
4. **Don't skip code review**: Phase 6 catches issues before they reach production
5. **Read the suggested files**: Phase 2 identifies key files — read them to understand context

## When to Use This Skill

**Use for:**
- New features that touch multiple files
- Features requiring architectural decisions
- Complex integrations with existing code
- Features where requirements are somewhat unclear

**Don't use for:**
- Single-line bug fixes
- Trivial changes
- Well-defined, simple tasks
- Urgent hotfixes

## Troubleshooting

### Agents take too long
**Issue**: Code exploration or architecture agents are slow
**Solution**: This is normal for large codebases. Agents run in parallel when possible. The thoroughness pays off in better understanding.

### Too many clarifying questions
**Issue**: Phase 3 asks too many questions
**Solution**: Be more specific in your initial feature request. Provide context about constraints upfront. Say "whatever you think is best" if you truly have no preference.

### Architecture options overwhelming
**Issue**: Too many architecture options in Phase 4
**Solution**: Trust the recommendation — it's based on codebase analysis. If still unsure, ask for more explanation. Pick the pragmatic option when in doubt.

## Tips

- **Be specific in your feature request**: More detail = fewer clarifying questions
- **Trust the process**: Each phase builds on the previous one
- **Review agent outputs**: Agents provide valuable insights about your codebase
- **Don't skip phases**: Each phase serves a purpose
- **Use for learning**: The exploration phase teaches you about your own codebase

## Requirements

- Git repository (for code review)
- Project with existing codebase (workflow assumes existing code to learn from)

## Credits

Original plugin by Sid Bidasaria (Anthropic). Converted to a universal, platform-agnostic Agent Skill format.
