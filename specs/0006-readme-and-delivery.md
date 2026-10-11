# 0006 - README, LangSmith evidence and GitHub delivery

## Goal
Document the techniques, results and how to run the project in the README, attach the LangSmith evidence, and leave the public fork with the final code on `main`.

## Scope
- In: `README.md` rewrite (Brazilian Portuguese), screenshots in `docs/images/`, push to `ricardorauber/mba-ia-pull-evaluation-prompt`.
- Out: code and prompt changes.

## Requirements
- R1: The README SHALL have a section "Técnicas Aplicadas (Fase 2)" explaining Few-shot Learning, Role Prompting and Chain of Thought: why each was chosen and a short practical excerpt of how it appears in the v2 prompt.
- R2: The README SHALL have a section "Resultados Finais" with: the public dataset URL from spec 0005, the final scores table, screenshots, the iteration history summary (linking `docs/iterations.md`), and a v1 vs v2 comparison (what changed and why).
- R3: The screenshots SHALL be captured by Claude in the user's Chrome session (Claude in Chrome) and saved in `docs/images/`: the dataset with 15 examples, the approved v2 experiment with its scores, at least 3 example traces, and the public v2 prompt in the Hub.
- R4: The README SHALL have a section "Como Executar" with prerequisites (Python 3.10+, LangSmith account with API key and Hub handle, OpenRouter key or OpenAI/Gemini key), venv creation, `pip install -r requirements.txt`, copying `.env.example` to `.env`, every `.env` variable with its purpose (including how `OPENAI_BASE_URL` selects OpenRouter), and the commands `python src/pull_prompts.py`, `python src/push_prompts.py`, `python src/evaluate.py` and `pytest`.
- R5: The repository SHALL be the public fork `ricardorauber/mba-ia-pull-evaluation-prompt` with all code, specs, ADRs, tests, prompts and docs on `main`; `.env` SHALL never be committed.

## Acceptance criteria
- [x] AC1: The three README sections exist with the content in R1, R2 and R4. (R1, R2, R4)
- [x] AC2: Every image referenced in the README exists in `docs/images/` and shows the items listed in R3; no screenshot exposes an API key. (R3)
- [x] AC3: Every variable in `.env.example` appears in the README. (R4)
- [x] AC4: Following "Como Executar" on a clean clone runs all four commands. (R4)
- [x] AC5: `https://github.com/ricardorauber/mba-ia-pull-evaluation-prompt` is public, a fork of `devfullcycle/mba-ia-pull-evaluation-prompt`, and its `main` contains the final work; `git ls-files` does not list `.env`. (R5)

## Unit tests
- T1: none — documentation and delivery only; verified by AC1–AC5.
