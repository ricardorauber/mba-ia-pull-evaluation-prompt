# 0005 - Evaluation and prompt iterations until approval

## Goal
Run `src/evaluate.py` against the published v2 prompt and iterate on `prompts/bug_to_user_story_v2.yml` until all five metrics reach at least 0.8, keeping a record of each iteration.

## Scope
- In: edits to `prompts/bug_to_user_story_v2.yml`, pushes with `src/push_prompts.py`, runs of `src/evaluate.py`, `docs/iterations.md`, sharing the evaluation dataset.
- Out: any change to `src/evaluate.py`, `src/metrics.py`, `src/utils.py` or `datasets/`; README (0006).

## Requirements
- R1: Each iteration SHALL edit only `prompts/bug_to_user_story_v2.yml`, keep `pytest` green, push it, and run `python src/evaluate.py` with the models set in `.env`.
- R2: Each iteration SHALL be recorded in `docs/iterations.md` (Brazilian Portuguese) with: number, date, change made and why (based on the metric reasoning and LangSmith traces), the five scores, the average and the experiment name.
- R3: Iterations SHALL continue until one run reports Helpfulness, Correctness, F1-Score, Clarity and Precision each ≥ 0.8 and the average ≥ 0.8 (`STATUS: APROVADO`), with a budget of up to 6 iterations before stopping to ask the user.
- R4: Few-shot examples added during tuning SHALL remain original (R7 of spec 0003) — tuning SHALL NOT copy dataset examples into the prompt.
- R5: After approval, the evaluation dataset `{LANGSMITH_PROJECT}-eval` SHALL be shared once with `Client().share_dataset(dataset_name=...)`, and the public URL SHALL be recorded in `docs/iterations.md`.
- R6: The approved run's terminal output SHALL be saved to `docs/evaluation-final.txt`.

## Acceptance criteria
- [x] AC1: `docs/iterations.md` lists every run with the R2 fields. (R1, R2)
- [x] AC2: The last recorded run shows all five metrics ≥ 0.8 and `STATUS: APROVADO`. (R3)
- [x] AC3: The approved prompt on the Hub equals the committed YAML (pushing again reports "already up to date"). (R1)
- [x] AC4: `pytest` passes and the dataset-leak test of spec 0003 still passes. (R1, R4)
- [x] AC5: The public dataset URL opens without login and shows the 15 examples and the experiments. (R5)
- [x] AC6: `docs/evaluation-final.txt` contains the approved run output. (R6)
- [x] AC7: `git diff upstream/main -- src/evaluate.py src/metrics.py src/utils.py datasets/` is empty. (Scope)

## Unit tests
- T1: none new — covered by the spec 0003 and 0004 tests, which must stay green after every iteration (AC4).
