# QA gate - Slice 3 (ranking fixes), cycle 6

**Verdict: APPROVE the slice (code + the six critic fixes), with one feed-quality condition: D-1 must be fixed before a feed ships to the user.**

## Suite
`cd projects/personalized-feed && PYTHONPATH=src .venv/bin/python -m pytest -q` -> `150 passed in 0.14s` (green, exit 0).

## Probes (live, temp dir /tmp/qa-s3.LJR5, --out; real profile/ and feeds/ hashes verified unchanged before/after)
- Two daily runs (2026-11-19, 2026-11-20), 33/33 sources ok, rung 0 both days, no warnings.
- Zero-traction gate: ~158 repos/day excluded (stats.excluded). Delivered GitHub items show source-quality 2-5 (no 1s).
- Top-3 cap: day 1 = 3 of 5, day 2 = 3 of 5 from top-3 interests (agent frameworks, local models, evals). PASS.
- Exploration: day 1 observability (interest-match 3, hands-on 5) ok. Day 2 "rust tooling" is interest-match 1 (see D-1).
- D7: 10 items across 2 days, zero URL overlap; day-2 stats ledger_seen=5; ledger rows written to temp ledger only. PASS.
- D2/D3: 5 items each day; source types 3 each (blog/GitHub/Lobsters; blog/GitHub/Substack). PASS. Each item has a "why" line.
- Links: all 10 returned HTTP 200 (actually fetched).
- Word boundary: "quarterly reports" no match for repo; "preportion" no; "repository", "repos", "notebooks" match; "code" no longer tryable. PASS.
- `pfeed feedback`: `--root T` wrote T/profile/alex-weights.json; `--weights T/w.json` wrote w.json (wins over --root). Real profile untouched. PASS.

## Defects
- **D-1 (medium, blocks shipping a feed): anti-interest leak.** Day-2 item #5 "AI Ambition: ArtCraft Cloned Photoshop..." (latent.space) was delivered as the exploration pick. Alex's profile excludes "AI art drama"; rule `ai-art` only matches the literal substring "ai art" (rank_data.EXCLUDE_KEYWORDS), so it never fired. It also qualified as exploration on a single weak keyword ("rust" in a headline, interest-match 1). Fix: widen ai-art keywords (art, image generation, photoshop clone...) and require exploration picks to have interest-match >= 3 (or strong match). Add a regression test with this title.
- **D-2 (low):** developer risk 1 confirmed as known: same repo name under different owners (ai--manus2.0 clones) not clustered.
- **D-3 (low):** weak keyword leaks ("production" -> reliability, "rust" in headline) fill late slots with interest-match 1-3. Developer-disclosed.
- **D-4 (info):** Lobsters item "Catching prompt injections hidden in PDFs" links (HTTP 200) to tomclancy.info/joshua-judges-ruth.html, a Bible-chapter page. Adapter is faithful: the live lobste.rs RSS serves exactly this title/link pair, so it is upstream, not a code bug. Consider a title-vs-page sanity check for Lobsters links or accept the risk.
- Not verified live: topic-fatigue (never triggers in a 2-day run; covered by unit tests only).

## New tests
None added by QA this pass (no new code bug in slice 3 itself). D-1 regression test should be added when it is fixed.

## Blockers
None for the slice. D-1 blocks delivering to the user (explicit exclude violated).
