# 0004 - Push the optimized prompt to the LangSmith Hub

## Goal
Implement `src/push_prompts.py` so it validates `prompts/bug_to_user_story_v2.yml` and publishes it publicly as `{USERNAME_LANGSMITH_HUB}/bug_to_user_story_v2` with its metadata.

## Scope
- In: body of `push_prompt_to_langsmith`, `validate_prompt` and `main` in `src/push_prompts.py`; `tests/test_push_prompts.py`; the first real push.
- Out: evaluation (0005).

## Requirements
- R1: WHEN `LANGSMITH_API_KEY` or `USERNAME_LANGSMITH_HUB` is missing, `main()` SHALL print the missing variable and return `1` without calling the Hub.
- R2: `main()` SHALL load the file with `utils.load_yaml` and read the `bug_to_user_story_v2` entry; WHEN the file or the entry is missing, it SHALL print an error in Brazilian Portuguese and return `1`.
- R3: `validate_prompt` SHALL return `(is_valid, errors)` combining `utils.validate_prompt_structure` with two checks: `user_prompt` is present and the template built from `system_prompt` + `user_prompt` has exactly the input variable `bug_report`. WHEN invalid, `main()` SHALL print every error and return `1` without pushing.
- R4: `push_prompt_to_langsmith` SHALL build `ChatPromptTemplate.from_messages([("system", system_prompt), ("user", user_prompt)])` and call `Client().push_prompt(f"{username}/bug_to_user_story_v2", object=prompt, is_public=True, description=..., readme=..., tags=...)`.
- R5: The push metadata SHALL be: `description` = YAML `description`; `tags` = YAML `tags` plus a slug per entry of `techniques_applied`, deduplicated and in order; `readme` = Markdown in Brazilian Portuguese listing the techniques applied and the version.
- R6: WHEN the Hub reports that nothing changed since the last commit (HTTP 409), the script SHALL print that the prompt is already up to date and return `0`; any other error SHALL print a Portuguese message and return `1`.
- R7: On success the script SHALL print the prompt identifier and the URL returned by `push_prompt`, and return `0`; it SHALL never print the API key value.

## Acceptance criteria
- [x] AC1: Without `USERNAME_LANGSMITH_HUB`, `main()` returns `1` and `Client` is never instantiated. (R1)
- [x] AC2: Missing YAML file or missing `bug_to_user_story_v2` entry → `1` with a Portuguese error. (R2)
- [x] AC3: A prompt with fewer than 2 techniques, an empty `system_prompt`, a missing `user_prompt` or an extra variable is rejected with one error per problem and no push. (R3)
- [x] AC4: A valid prompt is pushed once with the identifier `"<handle>/bug_to_user_story_v2"`, `is_public=True` and a `ChatPromptTemplate` whose input variables are `["bug_report"]`. (R4)
- [x] AC5: `tags` contains the YAML tags plus the technique slugs without duplicates; `description` and `readme` match R5. (R5)
- [x] AC6: A 409 conflict returns `0` with an "already up to date" message; another exception returns `1`. (R6)
- [x] AC7: Running `python src/push_prompts.py` with real credentials publishes the prompt, and it is visible and public at `https://smith.langchain.com/hub/<handle>/bug_to_user_story_v2`. (R4, R7)

## Unit tests
- T1: missing env var → `1`, no `Client` (AC1).
- T2: missing file / missing entry → `1` (AC2).
- T3: `validate_prompt` table-driven over the invalid cases in AC3, plus the valid v2 file → `(True, [])` (AC3).
- T4: `Client` patched; asserts `push_prompt` arguments (AC4, AC5).
- T5: `push_prompt` raising a 409 conflict → `0`; raising a generic error → `1` (AC6).
- T6: captured output never contains the fake key (R7).
