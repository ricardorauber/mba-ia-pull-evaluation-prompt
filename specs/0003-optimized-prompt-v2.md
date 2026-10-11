# 0003 - Optimized prompt v2 and its validation tests

## Goal
Write `prompts/bug_to_user_story_v2.yml`, a prompt that turns a bug report into a User Story in Brazilian Portuguese using Few-shot, Role Prompting and internal Chain of Thought, and validate it with the six required pytest tests.

## Scope
- In: `prompts/bug_to_user_story_v2.yml`, the six tests in `tests/test_prompts.py`.
- Out: push (0004), evaluation and tuning iterations (0005). The prompt text will be tuned in 0005; this spec fixes its structure and first version.

## Requirements
- R1: The YAML SHALL have the top-level key `bug_to_user_story_v2` with `description`, `system_prompt`, `user_prompt`, `version: "v2"`, `created_at`, `tags` and `techniques_applied` (list naming `Few-shot Learning`, `Role Prompting` and `Chain of Thought`).
- R2: The `system_prompt` SHALL define a persona (Role Prompting) starting with "Você é um Product Manager sênior" and the context of turning bug reports into backlog User Stories.
- R3: The `system_prompt` SHALL contain explicit numbered behavior rules: write in Brazilian Portuguese; use the format "Como um <persona>, eu quero <ação>, para que <benefício>."; follow it with "Critérios de Aceitação:" written as "Dado que / Quando / Então / E" bullets; use only facts present in the report (no invented numbers, endpoints or systems); output only the User Story, without preamble, reasoning or closing remarks.
- R4: The `system_prompt` SHALL instruct the model to reason step by step internally before writing (Chain of Thought): identify the affected user, the expected behavior, the impact and the technical details, then classify the report as simple, medium or complex — and SHALL forbid printing that reasoning.
- R5: The `system_prompt` SHALL scale the output to the classification: simple → story + acceptance criteria; medium with technical details → also "Contexto Técnico:"; complex with several problems → sections delimited with `=== ... ===` (main story, acceptance criteria grouped by problem, technical criteria, bug context, suggested technical tasks).
- R6: The `system_prompt` SHALL cover edge cases: very short or vague report, report with several problems, report with logs or stack traces, report with sensitive data (must not be copied), and input that is not a bug report.
- R7: The `system_prompt` SHALL contain at least three original Few-shot examples (not copied or adapted from `datasets/bug_to_user_story.jsonl`) — one simple, one medium, one complex — each with a clearly marked input ("Relato de bug:") and output ("User Story:").
- R8: The bug report SHALL appear only in `user_prompt`, as the single variable `{bug_report}`; the `system_prompt` SHALL contain no template variables, and any literal braces in it SHALL be escaped as `{{` / `}}`.
- R9: The file SHALL contain no `[TODO]` or `TODO` marker and SHALL pass `utils.validate_prompt_structure`.
- R10: `tests/test_prompts.py` SHALL implement, against the v2 file, `test_prompt_has_system_prompt`, `test_prompt_has_role_definition`, `test_prompt_mentions_format`, `test_prompt_has_few_shot_examples`, `test_prompt_no_todos` and `test_minimum_techniques`.

## Acceptance criteria
- [x] AC1: The YAML loads with `yaml.safe_load` and has every R1 field, with at least 2 entries in `techniques_applied`. (R1)
- [x] AC2: `system_prompt` contains "Você é um Product Manager". (R2)
- [x] AC3: `system_prompt` contains "Como um", "eu quero", "para que", "Critérios de Aceitação" and "Dado que". (R3)
- [x] AC4: `system_prompt` contains the step-by-step reasoning instruction and the rule not to print it. (R4)
- [x] AC5: `system_prompt` mentions "Contexto Técnico" and the `===` section format for complex reports. (R5)
- [x] AC6: Each edge case in R6 is addressed by a rule in `system_prompt`. (R6)
- [x] AC7: `system_prompt` has at least three "Relato de bug:" / "User Story:" pairs, and none of the dataset bug reports appears in it. (R7)
- [x] AC8: `ChatPromptTemplate.from_messages([("system", system_prompt), ("user", user_prompt)]).input_variables == ["bug_report"]`. (R8)
- [x] AC9: `utils.validate_prompt_structure` returns `(True, [])` and no TODO appears. (R9)
- [x] AC10: `pytest tests/test_prompts.py` passes all six tests. (R10)

## Unit tests
- T1: `test_prompt_has_system_prompt` — field exists and is non-empty (AC1).
- T2: `test_prompt_has_role_definition` — matches "Você é um" followed by a role (AC2).
- T3: `test_prompt_mentions_format` — mentions "User Story" or "Markdown" and the "Como um ... eu quero ... para que" pattern (AC3).
- T4: `test_prompt_has_few_shot_examples` — at least two input/output example pairs (AC7).
- T5: `test_prompt_no_todos` — no `[TODO]`/`TODO` in any text field (AC9).
- T6: `test_minimum_techniques` — `techniques_applied` has at least 2 entries (AC1).
- T7: extra — the template built from the YAML has exactly `["bug_report"]` as input variables (AC8).
- T8: extra — no dataset `bug_report` text is contained in `system_prompt` (AC7).
