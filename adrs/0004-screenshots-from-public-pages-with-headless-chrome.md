# 0004 - Capture LangSmith screenshots from the public pages with headless Chrome

- Date: 2026-10-11
- Spec: 0006-readme-and-delivery
- Status: proposed (pending user confirmation)

## Context
Spec 0006 (R3) says the screenshots are captured by Claude in the user's Chrome session (Claude in Chrome). When the spec was built, no Chrome browser was connected to the Claude in Chrome extension. Every required piece of evidence (dataset with 15 examples, approved experiment, example traces, public prompt) is available on public pages that need no login: the shared dataset URL and the public Hub prompt.

## Options considered
- A: Capture the public pages with the locally installed Google Chrome in headless mode, driven by Playwright from a temporary virtual environment outside the repository — no login involved, proves the pages are public; the screenshots do not show the logged-in workspace.
- B: Stop and wait for the extension to be connected — delays delivery; same content, captured from the logged-in workspace.
- C: Ask the user to take the screenshots — extra manual work for the user.

## Decision
Option A was applied so the user's request to "run everything to the end" could be completed. The user has to confirm it, or ask for the screenshots to be recaptured with Claude in Chrome (option B).

## Consequences
`docs/images/` holds seven screenshots of public LangSmith pages, captured in dark mode. If option B is chosen, only the images change; the README references stay the same. Spec 0006 R3 should be updated with `update-spec` if option A is confirmed.
