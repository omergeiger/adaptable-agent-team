# QA gate - Slice 4 (ranking tweaks + QA D-1), cycle 7

**Verdict: APPROVE the slice. Feed is shippable with caveats (D-5, D-4, D-6 below); none is a hard-rule violation.**

## Suite
`cd projects/personalized-feed && PYTHONPATH=src .venv/bin/python -m pytest -q` -> `180 passed in 0.19s` (green, exit 0).
After QA added tests/test_qa_slice4_gate.py: `182 passed in 0.18s`.

## Live trial (temp dir /tmp/qa-s4.EXRI, --out, dates 2026-11-19..21)
Real profile/ files hashed (shasum) before and after: identical. No real feeds/ dir was created. Ledger written only to temp.
Sources: 29/33, 32/33, 33/33 ok (day 1 had 4 GitHub search HTTP 403 rate-limit failures; the run degraded gracefully).

| Day | Items | Rung | Source types | Stars | Exploration |
|---|---|---|---|---|---|
| 11-19 | 5 | 0 | blog, GitHub, Lobsters | 29, 105, 669 | observability pick, match 3 |
| 11-20 | 3 | 3 | HN, GitHub, blog | 32 | none, warned |
| 11-21 | 3 | 4 | blog, GitHub, HN | 3493 | none, warned |

## Closure of QA defects
- D-1 ArtCraft: CLOSED. Excluded by ai-art rule (unit test + live: ai-art excluded 4-5/day, none delivered). Whole-word match; "ai artifacts" does not fire.
- D-2 clone clusters: CLOSED. name_clone_dupes 25/22/8 per day; no clones in any edition; D7 also matches by name_key across days.
- D-3 weak matches: CLOSED for main slots. No delivered item has interest-match 1; only match-2 item is day 2 #3 (LangSmith, mid-tier weak hit), match floor never dropped to 1.

## Feed-quality check
- D3 (3-5 items): PASS on all days, including the small 3-item editions. Size relaxation is explicitly warned in the report.
- D2 (>=3 distinct source types): PASS all days (3 types each).
- D7 (no resurfacing): PASS. 11 items across 3 days, zero URL overlap (ledger.md); ledger_seen 0 / 5 / 9.
- Why-line present on every item: PASS.
- Link validity: all 11 links actually fetched with curl -L, all HTTP 200.

## Specific concerns
1. Small-edition outcome: 3-item editions on day 2/3 meet D3 and D2 but at the cost of quality: rung 3-4 relaxations (hands-on floor, size, capped-interest 2nd item), no exploration slot. Pool shrinks fast because the live trial replays a rolling ~3 days of fresh content against a ledger; this is probably less acute in real daily use but is unmeasured. Acceptable, but watch it.
2. Low-weight interests: CONFIRMED (code: rank.match_interest, tier "low" base 1, strong or not, signal <= 1; main floor is 2, exploration floor 3). Interests with effective weight <= 2 (rust tooling, confirmed AI safety hands-on, document-processing agents, reliability) can never reach main slots except on the last warned rung. This contradicts the profile ("rust tooling - sometimes", AI safety "less" not "never"). Characterized by test_low_weight_interest_matches_cap_at_one (weak/conditional; flip if the ranking-engineer changes the rule). Needs a ranking-engineer decision, e.g. let a strong (>=2 hits / non-weak title) hit on a weight-2 interest score 2.

## Defects
- D-5 (medium, design): low-weight interests unreachable, see above. Not blocking.
- D-4 (still open, low-medium, link/content): Lobsters "Catching prompt injections hidden in PDFs" -> tomclancy.info/joshua-judges-ruth.html (HTTP 200 but a Bible-chapter page) delivered again on day 1 at match 3. Upstream RSS pair, adapter faithful, but a user would see a junk link. Suggest title-vs-page sanity check or Lobsters-link quarantine.
- D-6 (low, precision): "Show HN: Recalc - spreadsheet where cells are Claude Code terminals" delivered as evals interest (matched via HN query "eval"); erkamyaman/rust-anything (Rust app-rewriting tool from topic:mcp) scored as agent frameworks 5. Topic-derived matching over-credits. Item 3 on day 3 is thus marginal.
- Note: GitHub search 403s on day 1 (unauthenticated rate limit); no token configured. Not a code defect.

## New tests
tests/test_qa_slice4_gate.py (2 tests: low-weight cap characterization, small-edition D3 bound). Both pass.

## Blockers
None.
