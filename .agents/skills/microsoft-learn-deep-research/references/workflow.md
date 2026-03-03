# Workflow

Use this workflow for every deep-research run.

## 1) Scope and assumptions

- Capture user goal in one sentence.
- List hard constraints (version, language, environment, compliance, deadlines).
- Ask clarifying questions when constraints are missing and affect correctness.

## 2) Discovery pass (breadth)

- Run `microsoft_docs_search` with a precise query.
- If results are weak, refine query terms with:
  - product name
  - version/runtime
  - operation (configure, migrate, troubleshoot, secure)
- Build a shortlist of relevant documents.

## 3) Code sample pass (implementation signal)

- Run `microsoft_code_sample_search` for concrete examples.
- Apply language filter when user requested a language.
- Keep only samples that match the user scenario and current platform guidance.

## 4) Deep fetch pass (depth)

- Run `microsoft_docs_fetch` on the highest-value shortlisted URLs.
- Extract:
  - prerequisites
  - required configuration
  - critical API/CLI syntax
  - limits/known caveats
  - security and production notes

## 5) Synthesis pass

- Build answer from fetched evidence only.
- For each major recommendation, include at least one source URL.
- Separate facts from assumptions.
- Explicitly mark unresolved gaps.

## 6) Verification loop

- Re-check critical claims against fetched content.
- If evidence is weak or conflicting, run one more targeted search/fetch cycle.
- Stop only when recommendations are traceable and actionable.

## 7) Write report

- Save output using the required naming convention in `research/microsoft-learn/`.
- Ensure the report matches `references/output-format.md`.
