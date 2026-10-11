# 0002 - Pull the seed prompt from the LangSmith Hub

## Goal
Implement `src/pull_prompts.py` so it downloads `leonanluppi/bug_to_user_story_v1` from the LangSmith Prompt Hub and saves it as `prompts/bug_to_user_story_v1.yml`.

## Scope
- In: body of the functions in `src/pull_prompts.py`, `tests/test_pull_prompts.py`, the regenerated `prompts/bug_to_user_story_v1.yml`.
- Out: the optimized prompt (0003), push (0004).

## Requirements
- R1: WHEN `LANGSMITH_API_KEY` is missing, `main()` SHALL print the missing variable (via `utils.check_env_vars`) and return exit code `1` without calling the Hub.
- R2: The script SHALL pull `leonanluppi/bug_to_user_story_v1` with `langsmith.Client().pull_prompt(..., dangerously_pull_public_prompt=True)`; the dangerous flag SHALL be used only for this fixed seed identifier.
- R3: The script SHALL convert the returned `ChatPromptTemplate` into a dict under the top-level key `bug_to_user_story_v1` with the fields of the shipped file: `description`, `system_prompt` (text of the system message template), `user_prompt` (text of the human message template), `version: "v1"`, `created_at` (pull date, ISO `YYYY-MM-DD`), `tags` and `source: "leonanluppi/bug_to_user_story_v1"`.
- R4: The script SHALL write that dict to `prompts/bug_to_user_story_v1.yml` with `utils.save_yaml`, preserving UTF-8 accents.
- R5: WHEN the pull or the save fails, `main()` SHALL print an error in Brazilian Portuguese and return `1`; on success it SHALL print the saved path and return `0`.
- R6: The script SHALL never print the API key value.

## Acceptance criteria
- [x] AC1: Without `LANGSMITH_API_KEY`, `main()` returns `1` and `Client` is never instantiated. (R1)
- [x] AC2: `pull_prompt` is called once with `"leonanluppi/bug_to_user_story_v1"` and `dangerously_pull_public_prompt=True`. (R2)
- [x] AC3: For a template with one system and one human message, the saved YAML has the R3 fields with the exact message texts, including `{bug_report}`. (R3, R4)
- [x] AC4: A pull that raises makes `main()` return `1` and print a Portuguese error. (R5)
- [x] AC5: Running `python src/pull_prompts.py` with a real key creates `prompts/bug_to_user_story_v1.yml` whose `system_prompt` contains `{bug_report}`. (R2–R5)
- [x] AC6: No captured output contains the API key value. (R6)

## Unit tests
- T1: missing env var → exit code `1`, `Client` not called (AC1).
- T2: `Client` patched; asserts identifier and `dangerously_pull_public_prompt=True` (AC2).
- T3: real `ChatPromptTemplate.from_messages([("system", ...), ("human", "{bug_report}")])` returned by the mock; YAML written to `tmp_path` matches R3 (AC3).
- T4: `pull_prompt` raising → exit code `1` and message in Portuguese (AC4).
- T5: `capsys` output from T1–T4 never contains the fake key (AC6).
