---
name: microsoft-learn-deep-research
description: Performs deep, retrieval-led technical research on official Microsoft documentation via Microsoft Learn MCP. Use when the user needs authoritative Microsoft/Azure/.NET guidance, implementation details, or code-sample-backed recommendations.
---

# Microsoft Learn Deep Research

Run thorough Microsoft-focused research with strict traceability and write the result to a reusable report file.

Detailed procedures:
- `references/workflow.md`
- `references/mcp-setup-and-fallback.md`
- `references/output-format.md`

## Activation Triggers

Activate when the user asks for:
- deep research on Microsoft technologies
- official Microsoft Docs/learn content synthesis
- architecture, setup, migration, troubleshooting, or implementation guidance from Microsoft sources
- source-backed recommendations for Azure, .NET, Microsoft 365, Power Platform, Entra, Intune, Fabric, SQL Server, or Windows development

## Required Tool Contract

Use Microsoft Learn MCP tools:
- `microsoft_docs_search`
- `microsoft_code_sample_search`
- `microsoft_docs_fetch`

Do not skip retrieval. Final output must be grounded in fetched Microsoft sources.

## Clarifying Question Gate

Before running research, ask clarifying questions when any of these are unclear:
- target product/service
- version/runtime/SDK
- cloud/environment constraints
- language/framework preference
- expected depth (quick answer vs in-depth implementation plan)

If missing details materially affect correctness, pause and ask first.

## Planner behavior

1. Restate user objective and constraints.
2. Build a research plan with explicit retrieval stages:
   - docs discovery
   - code sample discovery
   - deep fetch and synthesis
3. Define success criteria:
   - authoritative sources only
   - implementation-ready guidance
   - citations for all critical claims
4. Confirm output report path and naming convention before writing.

## Coding behavior

Execute in this order:
1. `microsoft_docs_search` for broad discovery and shortlisting.
2. `microsoft_code_sample_search` for practical implementation examples (filter by language when needed).
3. `microsoft_docs_fetch` for top-ranked pages required to answer the query completely.
4. Synthesize findings with explicit citations.
5. Write results to:
   - `research/microsoft-learn/YYYY-MM-DD-<topic-slug>.md`

## MCP Availability Rules

If Microsoft Learn MCP is unavailable:
1. Stop deep-research execution.
2. Instruct the user to install/configure Microsoft Learn MCP for their IDE.
3. Ask them to retry after setup.

Do not fabricate MCP results or pretend retrieval succeeded.

## Guardrails

- Use Microsoft official sources as primary evidence.
- Avoid unsupported claims; mark uncertain items explicitly.
- Keep source links and evidence near each key conclusion.
- Prefer concrete implementation steps over high-level summaries.
- Maintain reproducible, structured reports for future reference.
