# Developer - slice 3: ranking fixes for critic NO-GO (cycle 6)

Weights unchanged (0.35/0.20/0.20/0.15/0.10). Suite: 150 tests green (130 + 20 new), all offline.

## Done (critic required changes)
1. Exploration: pick needs a non-empty matched interest outside top-3/inferred, and passes `_fits` (rank.py `_exploration_pick`).
2. Traction: `source_quality` for repos/tools = ladder on stars (HN points when stars unknown): <10:1, <50:2, <200:3, <1000:4, else 5; repo <=7 days old with >=50 stars gets at least 4 (needs `created_at`). `thought_leadership` 3 at >=1000 stars. Hard gate "zero-traction repo": GitHub repo <10 stars dropped unless another candidate clusters to it (paper repo_links / HN link). Gate shows in `stats.excluded`. Constants in rank_data.py.
3. `_has` is whole-word (+ optional plural s); TRYABLE_WORDS dropped "code"/"repo", added "repository". Test with "quarterly report".
4. Top-3 guardrail: max round(0.6n) items (3 of 5) from top-3 interests combined, inside `_fits` (so it also binds the D2 swap); last relaxation rung gets +1. Per-interest cap kept.
5. Topic fatigue: DONE (cheap). `fatigued_interests(ledger, profile)` re-derives interests from ledger titles (no ledger format change) for last 5 editions; >=3 hits -> novelty 3 for that interest. Caveat: titles only, so it undercounts; never overcounts.
6. Report: each chosen item prints signals, total, interest, [exploration]; `relaxation rung used: N`; `stats["rung"]` recorded. `select(..., today=)` added; pipeline passes it.

QA D-3: `pfeed feedback` has `--root DIR` and `--weights FILE` (weights wins). README.md added with the `PYTHONPATH=src python -m pfeed daily --user alex` entry.

## Live trial (temp dir /tmp/pfeed-trial.Q0Bunx, dates 11-19..11-21, 33/33 sources ok; real feeds/ and ledger untouched)
| Criterion | Result |
|---|---|
| Median stars of delivered GitHub items >= 50 | 62 (stars 12, 29, 62, 62, 105, 136, 3469) PASS, but see risk 1 |
| Top-3 interests <= 3 of 5 | 3, 3, 3 PASS |
| Real exploration interest | d1 observability; d2 rust (weak: Substack newsletter); d3 none, warning emitted. PARTIAL |
| >= 3 source types | 3, 3, 3 (blog/GitHub/Lobsters; blog/GitHub/Substack; blog/GitHub/HN/Substack = 4) PASS |
| Relaxation rung | 0 on all 3 days (no silent floor erosion) PASS |
Gate effect: ~160 of ~480 daily candidates dropped as zero-traction repos (so the old 0-star junk is gone).

## Risks left (for ranking-engineer/critic)
1. Day 3 delivered two clones, `abodeahsz00az-cmd/ai--manus2.0` and `alphafalcongamer-creator/ai--manus2.0` (both 62 stars): same repo name under different owners, likely star-farmed copies. Per-cluster/owner dedupe does not catch them. Suggest: same repo-name across owners = one cluster.
2. Weak keyword matches still leak: "production" -> production reliability (TimeNet, AINews), "rust" in a Substack headline (ArtCraft). Interest-match is 1 for these; they fill slots at the end. Candidate for tightening, not done (out of scope).
3. Exploration slot sometimes empty (d3) because the bar needs hands-on>=4 and a matched non-top interest; acceptable, warned.
4. Fatigue is title-based; did not trigger in the 3-day trial (stats.fatigued = []), so it is tested only by unit tests.
5. Numeric thresholds are the critic's starting guesses; thought-leadership (R5) untouched.

## Handoff to QA
Run `PYTHONPATH=src .venv/bin/python -m pytest -q` (150). New tests: tests/test_slice3_ranking_fixes.py, tests/test_slice3_feedback_cli.py. Not committed.
