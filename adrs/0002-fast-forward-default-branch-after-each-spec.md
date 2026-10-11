# 0002 - Fast-forward the default branch after each spec

- Date: 2026-10-11
- Spec: 0001-project-setup-and-config
- Status: accepted

## Context
The build process never commits to the default branch, but spec 0006 requires the default branch of the public fork to contain the final code. The same decision was taken in the first challenge.

## Options considered
- A: Open one pull request per spec and merge them in order at the end.
- B: Open pull requests and let the user merge them.
- C: Fast-forward `main` to each spec branch once it is green.

## Decision
"Commit direto na main" (Commit straight to main) — option C, carried over from the first challenge.

## Consequences
Each spec is still built in its own worktree and branch. Once a spec is green, committed and pushed, `main` is fast-forwarded to that spec branch and pushed, and the next spec branches from the updated `main`.
