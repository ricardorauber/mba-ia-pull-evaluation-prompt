# 0003 - Use OpenRouter through the OpenAI client and OPENAI_BASE_URL

- Date: 2026-10-11
- Spec: 0001-project-setup-and-config
- Status: accepted

## Context
The ready-made `src/utils.py`, `src/evaluate.py` and `src/metrics.py` must not be changed, and `utils.get_llm()` only accepts `LLM_PROVIDER=openai` or `google`. The only LLM key available is an OpenRouter key. `ChatOpenAI` uses the `openai` SDK, which reads `OPENAI_BASE_URL` from the environment when no base URL is passed.

## Options considered
- A: OpenRouter via `LLM_PROVIDER=openai`, `OPENAI_BASE_URL=https://openrouter.ai/api/v1` and the OpenRouter key in `OPENAI_API_KEY` — no code change, reuses the existing key.
- B: OpenAI directly — requires a new key; ~$1-5.
- C: Gemini free tier — low request-per-minute limits may stall 15 examples × 4 calls.

## Decision
"OpenRouter via OpenAI" — option A. Models: `LLM_MODEL=google/gemini-3.1-flash-lite` and `EVAL_MODEL=google/gemini-3.8-flash` ("Gemini lite + Gemini flash"), both listed by OpenRouter with `temperature` support on 2026-10-11.

## Consequences
`.env.example` defaults to `LLM_PROVIDER=openai`, `OPENAI_BASE_URL=https://openrouter.ai/api/v1` and the models above. Removing `OPENAI_BASE_URL` and using an OpenAI key switches to OpenAI directly; `LLM_PROVIDER=google` with `GOOGLE_API_KEY` still works for Gemini.
