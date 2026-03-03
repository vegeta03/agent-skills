# Link Format Requirements

When linking to GitHub code in comments, use full SHA links with a line range:

`https://github.com/<owner>/<repo>/blob/<full_sha>/<path>#L<start>-L<end>`

## Rules

- use full 40-character SHA
- repo name must match the PR repository
- include at least one line of context before and after the issue location
- use `#Lstart-Lend` format exactly

## Invalid Pattern

Do not use command substitution in link text (for example `$(git rev-parse HEAD)`), because rendered comments need concrete static URLs.
