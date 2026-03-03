# High-Signal Criteria

Flag an issue only if it is likely real and consequential.

## Include

- compile/parse/type failures
- deterministic logic errors producing incorrect behavior
- clear rule violations with an explicit quote from governing instructions
- concrete security or correctness defects in changed code

## Exclude

- subjective style opinions
- speculative issues requiring unknown runtime state
- lint-only concerns that tooling already covers
- pre-existing issues not introduced by current changes
- duplicate findings phrased multiple ways
- pedantic nits a senior engineer would not escalate
- issues explicitly silenced by project-approved suppressions

## Confidence Rubric

- 0: false positive
- 25: weak signal
- 50: plausible but not critical
- 75: likely real and important
- 100: certain and reproducible

Report only `>= 80`.

## Validation Requirement

Any issue flagged by an initial reviewer must be validated in a separate pass before reporting.
