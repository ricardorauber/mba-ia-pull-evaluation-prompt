# 0001 - User-facing text stays in Brazilian Portuguese; everything else is in English

- Date: 2026-10-11
- Spec: 0001-project-setup-and-config
- Status: accepted

## Context
The build process requires every produced file to be in American English, but the challenge statement, the ready-made scripts and the evaluation dataset are in Brazilian Portuguese, and specs 0002, 0003, 0004, 0005 and 0006 require CLI messages, the prompts and the README in Brazilian Portuguese. The same decision was taken in the first challenge.

## Options considered
- A: User-facing text (CLI messages, error messages, prompt content, `.env.example` comments, README, iteration log) in Brazilian Portuguese; code, identifiers, code comments, tests, specs, ADRs and commits in English — follows the specs and the challenge.
- B: Everything in English — diverges from the challenge, the dataset and the ready-made scripts.

## Decision
"Textos ao usuário em PT-BR" (User-facing text in Brazilian Portuguese) — option A, carried over from the first challenge.

## Consequences
Strings printed to the terminal, the prompts, the `.env.example` comments and the README are written in Brazilian Portuguese. Source code, identifiers, code comments, tests, specs, ADRs and commit messages remain in American English.
