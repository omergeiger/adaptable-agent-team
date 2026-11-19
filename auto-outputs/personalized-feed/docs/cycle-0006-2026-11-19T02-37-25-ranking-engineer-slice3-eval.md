# Ranking-engineer eval: Slice 3 ranking fixes (cycle 6)

Reviewed: `rank.py`, `rank_data.py`, developer note, `profile/alex.md`, `loop-plugin:relevance-rubric`. Code read only; the 3-day trial figures are the developer's, not re-run by me.

## Verdict: APPROVE WITH GAPS (4 spec tweaks required before the eval is "done"; 2 optional)
Direction is right and weights are untouched (rubric intact). The score is still explainable per item. But three defects will visibly annoy Alex: clones, thin keyword matches filling slots, and a traction signal that is both too weak in the score and double counted.

## Findings

**1. Traction thresholds - mostly sound, two flaws**
- Ladder (<10/<50/<200/<1000) is reasonable for a "repo to clone on a Friday" reader. Median 62 passes, but a delivered set of 12, 29, 62, 62 stars means 3 of 7 repos are weak. A median hides a weak tail.
- Source-quality carries weight 0.10, so the full 1-to-5 ladder swing is worth only 0.4 total. A 12-star repo (quality 2) with hands-on 5 still outranks a good article. The hard gate (`MIN_REPO_STARS=10`) is therefore doing the real work, and 10 is too low: 12-star repos get through.
- Halo / double count (Kahneman): `NOTABLE_REPO_STARS` 5000 -> 1000 gives thought-leadership 3 to any repo with 1000+ stars, while source-quality already gives it 5 for the same stars. One fact (popularity) is scored in two signals, which is the inflation the decomposed rubric exists to prevent. Thought-leadership means "from or about a notable person", not "popular".
- Velocity bonus (<=7 days old, >=50 stars -> quality 4) is exactly what a star-farmed fresh clone satisfies (62 stars, new account). It must not apply to clone-flagged repos.

**2. Loose keywords - confirmed, and the cause is wider than the two examples**
- Match is `\b<kw>` prefix-only (rank.py match_interest). Consequences: "sla" fires on "slack/slate"; "document" fires on "documentation"; "trace", "form..." similar. `_has` was fixed to whole-word but `match_interest` was not.
- "production" and "rust" are single generic hits that give match 1. Match 1 contributes only 0.35 but with 3-5 slots and hands-on/novelty/quality all high, these items still make it in. Interest-match is the 0.35 signal and a match of 1 should mean "do not ship in a main slot".
- "rust" for Alex means rust tooling for his LLM/ML work (weight 1, "sometimes"). A Substack headline mentioning Rust is not tryable; the exploration slot should not be filled by it.

**3. Clone defect - confirmed in code**
- `cluster_key` = `gh:<owner>/<repo>`; two owners with the same repo name never collide. Identical star counts (62/62) plus an odd name (`ai--manus2.0`) is the classic farmed-copy tell. Note D7 applies: if only same-day dedupe is fixed, the other clone ships tomorrow.

## Spec tweaks for the developer (priority order)

1. **Repo-name clustering (clone defect).**
   - Add `name_key(c)` = lowercase repo name for GitHub repo URLs. In the same-day dedupe in `select()`, two GitHub repo candidates with the same `name_key` but different owners are one cluster; keep the one with higher stars, tie-break earliest `created_at`, then owner alphabetically (deterministic).
   - Apply only to distinctive names to avoid merging unrelated "demo"/"agent"/"examples" repos: name length >= 8, or contains a digit, `-`, `_`, or `.`; and not in a small generic stoplist (`agent`, `agents`, `examples`, `demo`, `starter`, `playground`, `tutorial`).
   - Ledger (D7): when a repo is delivered, a later candidate with the same distinctive `name_key` is treated as `ledger_seen`. Implement by deriving the name from the stored URL; no ledger format change.
   - Clone-flagged losers are not eligible for the velocity bonus. Stat: `stats["name_clone_dupes"]`.
   - Acceptance: test with `a/ai--manus2.0` and `b/ai--manus2.0` (62 stars each) yields exactly 1 item; test that `a/demo` and `b/demo` still both survive; test that day 2 does not ship `b/ai--manus2.0` after `a/ai--manus2.0` was delivered.

2. **Interest-match floor (kills "production"/"rust" filler).**
   - `MIN_INTEREST_MATCH_MAIN = 2`: a main-slot item needs interest-match >= 2. Not applicable to the exploration slot (see tweak 3). Lowest relaxation rung may drop this to 1 but must print it as a warning, never silently.
   - Split keywords into strong and weak. Weak (single hit scores one tier lower and never "strong" via title alone): `production`, `document`, `form`, `schema`, `trace`, `retrieval`, `benchmark`, `monitoring`, `incident`, `ticket`. A weak keyword needs a second distinct hit, or one strong hit, to count as strong.
   - Fix prefix matching: short or ambiguous keywords (`sla`, `mcp`, `otel`, `mlx`, `pdf`, `ocr`, `eval`, `trace`, `rust`) match as whole word with optional trailing `s`; `sla` -> `slas` only. Keep prefix (`quantiz`, `orchestrat`) only where listed as stems.
   - `rust tooling`: require co-occurrence with an LLM/ML/agent/inference term, or item_type in (repo, tool).
   - Acceptance: "Why production matters" (no other hit) and a Substack headline with "Rust" and no LLM term both score interest-match <= 1 and are not delivered; "Slack announces ..." does not match production reliability; "documentation site" does not match document-processing; a repo titled "candle-based LLM runner" still matches.

3. **Exploration slot quality.**
   - Exploration candidate must be item_type repo/tool, or a paper with repo_links, or a tryable article from a reputable source (not Substack newsletter headline). Empty slot with the existing warning remains acceptable (d3 behaviour is correct, better than a weak fill).
   - Acceptance: d2-style "rust in a Substack headline" is not picked as exploration.

4. **Traction retune.**
   - `MIN_REPO_STARS` 10 -> 25. Exception: repo age <= 3 days AND stars >= 10 AND (HN points >= 20 or clustered with a paper/HN item) is allowed.
   - Edition-level: at most 1 delivered GitHub repo under 50 stars (a "tail" cap), in addition to the median >= 50 check. Report prints `repo stars: [..] median`.
   - `NOTABLE_REPO_STARS` back to 5000 (or remove the star rule; use `NOTABLE_AUTHORS` plus a short notable-org list instead). Thought-leadership must not restate traction.
   - Velocity bonus keeps 50 stars but also requires not clone-flagged (tweak 1) and `created_at` present.
   - Acceptance: a 12-star repo is dropped; a 3-day-old 15-star repo with 25 HN points survives; 3469-star repo gets source-quality 5 and thought-leadership 1 unless its owner is notable.

5. (Optional) Star-farm tell: flag two same-day candidates with identical star count and similar names (edit distance <= 2) even across different name keys; log only, no drop yet.
6. (Optional) Make fatigue visible: print `fatigued: []` in the report line so a reviewer sees it ran; unit-tested only so far.

## Rubric / feedback changes
No rubric weight change. Clarification added by this note: thought-leadership excludes popularity; interest-match <= 1 is non-shippable in main slots. Feedback semantics unchanged (+/-0.05, renormalize, logged).

## Feedback integration (for the next edition)
- A thumbs-down on a clone or weak-keyword item should NOT lower the interest weight (production reliability, rust); the defect is match quality, not taste. Spec: on thumbs-down, if the item's interest-match <= 1, log the event but skip the interest flag to user-profiler.
- Thumbs-up on a repo item raises hands-on and source-quality weights; keep step small so the traction ladder does not dominate (cap source-quality weight at 0.20).
- Inferred interests stay capped at 2 (D6/D9); do not promote from simulated reactions.

## Blockers
None. Real trial numbers are developer-reported; re-run the 3-day offline trial after tweaks 1-4 and I will re-judge the actual feed (target: no clones, no match-1 items in main slots, repo tail <= 1, exploration filled or warned).
