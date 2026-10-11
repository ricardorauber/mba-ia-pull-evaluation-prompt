# 0001 - Project setup and configuration

## Goal
Make the fork installable and runnable against OpenRouter without touching the ready-made `src/evaluate.py`, `src/metrics.py` and `src/utils.py`, and record the project conventions as ADRs.

## Scope
- In: `.env.example`, `pytest.ini`, local venv check of `requirements.txt`, `adrs/0001`–`adrs/0003`.
- Out: pull (0002), optimized prompt and its tests (0003), push (0004), evaluation runs (0005), README (0006). Any change to `src/evaluate.py`, `src/metrics.py`, `src/utils.py` or `datasets/`.

## Requirements
- R1: `.env.example` SHALL keep every variable it ships with (`LANGSMITH_TRACING`, `LANGSMITH_ENDPOINT`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`, `USERNAME_LANGSMITH_HUB`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `LLM_PROVIDER`, `LLM_MODEL`, `EVAL_MODEL`) and SHALL add `OPENAI_BASE_URL`.
- R2: `.env.example` SHALL default to OpenRouter through the OpenAI-compatible client: `LLM_PROVIDER=openai`, `OPENAI_BASE_URL=https://openrouter.ai/api/v1`, `LLM_MODEL=google/gemini-3.1-flash-lite`, `EVAL_MODEL=google/gemini-3.8-flash`, with comments in Brazilian Portuguese explaining that `OPENAI_API_KEY` holds the OpenRouter key and that removing `OPENAI_BASE_URL` switches back to OpenAI directly. Model names SHALL be confirmed against OpenRouter's model list (and their support for `temperature`) at build time.
- R3: All key values (`LANGSMITH_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`) and `USERNAME_LANGSMITH_HUB` SHALL be empty in `.env.example`; `.env` SHALL stay git-ignored.
- R4: `pytest.ini` SHALL make `pytest` run from the repository root, discover `tests/`, and put `src/` on the import path so tests can import `utils`, `pull_prompts` and `push_prompts`.
- R5: The pinned `requirements.txt` SHALL install in a fresh Python 3.14 venv; a version SHALL only be changed if installation fails, and the change SHALL be recorded in an ADR.
- R6: The repository SHALL contain `adrs/0001-user-facing-text-in-brazilian-portuguese.md`, `adrs/0002-fast-forward-default-branch-after-each-spec.md` and `adrs/0003-openrouter-through-openai-base-url.md`, following the format of the ADRs in the first challenge (`../Busca_Semantica-LangChain-Postgres/adrs/`).
- R7: Through `src/utils.get_llm()`, unchanged, a `ChatOpenAI` built with `LLM_PROVIDER=openai` and `OPENAI_BASE_URL` set SHALL target the OpenRouter base URL.

## Acceptance criteria
- [ ] AC1: `.env.example` contains all original variables plus `OPENAI_BASE_URL`, with the defaults in R2. (R1, R2)
- [ ] AC2: No key value and no `USERNAME_LANGSMITH_HUB` value is filled in `.env.example`; `git check-ignore .env` succeeds. (R3)
- [ ] AC3: `pytest` from the repository root collects `tests/` without import errors. (R4)
- [ ] AC4: `pip install -r requirements.txt` succeeds in a fresh Python 3.14 venv. (R5)
- [ ] AC5: The three ADR files exist and each has Date, Spec, Status, Context, Options considered, Decision and Consequences. (R6)
- [ ] AC6: With `LLM_PROVIDER=openai`, `OPENAI_API_KEY=dummy` and `OPENAI_BASE_URL=https://openrouter.ai/api/v1`, `utils.get_llm()` returns a `ChatOpenAI` whose client base URL is the OpenRouter URL. (R7)
- [ ] AC7: `git diff upstream/main -- src/evaluate.py src/metrics.py src/utils.py datasets/` is empty. (Scope)

## Unit tests
- T1: `tests/test_config.py` — `utils.get_llm()` with the env in AC6 (set via `monkeypatch`) returns `ChatOpenAI` with the OpenRouter base URL and the `LLM_MODEL` value; no network call (AC6).
- T2: `tests/test_config.py` — `.env.example` parses into a dict that contains every variable in R1 and has empty values for the variables in R3 (AC1, AC2).
