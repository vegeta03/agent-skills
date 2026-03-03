# MCP Setup And Fallback

This skill requires the Microsoft Learn MCP server to perform retrieval-led research.

## Required server

- Server: Microsoft Learn MCP
- Remote endpoint: `https://learn.microsoft.com/api/mcp`
- Required tools:
  - `microsoft_docs_search`
  - `microsoft_code_sample_search`
  - `microsoft_docs_fetch`

## Setup guidance to provide the user

If the server/tools are unavailable in the current IDE:
1. Ask the user to add Microsoft Learn MCP in their MCP configuration.
2. Share the official setup source:
   - `https://github.com/MicrosoftDocs/mcp`
3. Ask the user to verify the server appears and tools are callable.
4. Resume research only after confirmation.

## Fallback protocol

When MCP is unavailable:
- Do not continue with guessed or pre-trained-only research.
- Return a blocked status with:
  - what is missing (server or tool access)
  - where to install/configure from
  - exact next action ("Configure MCP, then rerun this research request")

## Validation checklist after setup

- MCP server is listed in the IDE.
- `microsoft_docs_search` works.
- `microsoft_code_sample_search` works.
- `microsoft_docs_fetch` works.
- Research run can proceed end-to-end.
