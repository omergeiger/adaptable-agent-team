# Developer - slice 4: ranking-engineer tweaks + QA D-1 (cycle 7)

Weights unchanged (0.35/0.20/0.20/0.15/0.10; asserted by a test). Suite: `PYTHONPATH=src .venv/bin/python -m pytest -q` -> 180 passed (150 + 30 new, 1 updated). Not committed.

## Changes
1. Clone clusters: `ledger.name_key()` (distinctive repo name: len >= 8 or has digit/-/_/. ; stoplist agent/agents/examples/demo/starter/playground/tutorial). `rank.drop_name_clones()` keeps the winner by most stars, then earliest created_at, then owner alphabetical; `stats["name_clone_dupes"]`. D7: `Ledger.seen()` also matches name_key derived from stored URLs (no ledger format change).
2. Strong/weak keywords (rank_data WEAK_KEYWORDS), whole-word matching with optional plural s (STEM_KEYWORDS = quantiz, orchestrat stay prefix), rust tooling needs an LLM/ML/agent term unless item is repo/tool. Title hit is strong only for non-weak keywords. Main slots need interest-match >= 2 (`MIN_INTEREST_MATCH_MAIN`); a new last relaxation rung drops it to 1 with an explicit warning.
3. Exploration: interest-match >= 3 and type repo/tool, paper with repo_links, or tryable non-Substack article.
4. MIN_REPO_STARS 25; max 1 delivered repo under 50 stars (`_fits`, never relaxed); NOTABLE_REPO_STARS 5000. Report prints `repo stars: [...] median`.
5. D-1: ai-art keywords widened (artcraft, photoshop, image generation/generator, ai artist, midjourney, text-to-image, generative art...), matched whole-word so "ai artifacts" does not fire.

Tests: tests/test_slice4_ranking_fixes.py (ArtCraft, clone cluster, generic names, D7 later-day clone, strong/weak, sla/documentation, stems, floor and its warning, exploration, star gates). Updated test_slice3 thought-leadership test to 5000.

## Trial (live public sources, temp dir /tmp/pfeed-s4.rjFtEG, 2026-11-19..21; real feeds/ and profile/ hashes unchanged)
| Day | Items | Rung | Exploration | Repo stars | Notes |
|---|---|---|---|---|---|
| 11-19 | 5 | 0 | observability (antigravity-token-monitor, match 3) | 29, 105, 3484 | name_clone_dupes 25 |
| 11-20 | 3 | 3 | none, warned | 32 | clones 21 |
| 11-21 | 3 | 4 | none, warned | 136 | clones 8 |
No clones, no match-1 items, tail <= 1 every day, ArtCraft-type items excluded (ai-art 4-5/day), floor never dropped to 1.

## Deviations / risks
- Day 2 and 3 ship only 3 items (rung 3 and 4, warned). The 2-match floor + tail cap + 25 stars shrinks the pool; low-weight interests (weight <= 2, base tier "low") can only ever score 1, so they never reach main slots now. Ranking-engineer should judge whether that is intended.
- Skipped the "age <= 3 days, 10+ stars, 20+ HN points" star exception: GitHub-source repos have no HN points, and items clustered with a paper/HN post already bypass the gate.
- Optional items 5 and 6 (star-farm tell log, `fatigued: []` line) not done; `stats` already prints `fatigued`.
- Clone-flagged velocity bonus: losers are dropped, so no separate flag needed.
- "Offline" trial = no Slack and no real state; sources were fetched live (read-only), as in slice 3.
- Observed, out of scope: "Show HN: Recalc" matched the evals interest at 5; Lobsters PDF item (D-4) still delivered on day 1.
