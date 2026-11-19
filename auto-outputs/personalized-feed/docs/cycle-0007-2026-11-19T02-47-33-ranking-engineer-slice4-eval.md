# Ranking-engineer eval - slice 4 (cycle 7)

Judged against: steering/personalized-feed/reader-source.md (Alex), docs/ranking-design.md, loop-plugin:relevance-rubric.
Evidence: developer log (180 tests pass, 3-day trial) plus my own trial, 2026-11-19, `--out /tmp/pfeed-re7.p05w` (real feeds/, ledger and profile untouched; profile hashes verified). Note my trial saw GitHub API 403 on 5 topic queries (rate limit), so the GitHub pool was thinner than the developer's run; rung 0, 5 items, 4 source types.

## Verdict: APPROVE WITH CONDITIONS (slice 4 changes accepted; one must-fix and one should-fix before edition 1)

### What slice 4 got right (checked)
- Weights unchanged and asserted (0.35/0.20/0.20/0.15/0.10). No rubric drift.
- Clone clusters: 25 name-clone dupes removed in my run; no clone pair in output. D7 extension via name_key from stored URLs needs no ledger format change - good.
- ArtCraft-type items gone (ai-art whole-word rule; "ai artifacts" safe). Matches Alex's "AI art drama" exclusion.
- Floor of 2 on main slots removed single-generic-word matches (the slice 3 "sla" and "documentation" class). Warned, never silent, when relaxed to 1.
- Star gates (25 min; max 1 repo under 50) shifted repo quality up: delivered repos 29 and 669 stars.
- Exploration now needs a real match plus tryable type. Mine: antigravity-token-monitor, observability (mid tier, outside top 3), hands-on 5. That is the "one broadening item" Alex 👍s.

### Item-level judgment of my trial edition (Alex's taste)
| # | Item | Verdict |
|---|---|---|
| 1 | aws-emulator (Simon Willison) | Acceptable. Notable author, tryable. Agent link is thin but a shipped writeup is what Alex wants. Keep. |
| 2 | boring-marketing-skills (669 stars, ai-agents topic) | Marginal. Marketing "skills" prompt pack is closer to prompt-hack territory than agent frameworks. Interest-match 5 is generous. Not blocking. |
| 3 | Show HN: Recalc (spreadsheet of Claude Code terminals) | MIS-RANKED. Scored interest-match 5 on "evals for LLM apps". It is a spreadsheet UI; nothing about evals. Rank 3 of 5 on a false top-tier match. Alex would 👎 (nothing eval-related, novelty toy). Already noted by dev as out of scope; I am promoting it to a finding. |
| 4 | antigravity-token-monitor (29 stars) | Borderline. Token monitor is thin observability, but it is hands-on, passes the tail cap, and is a legitimate labelled broadening pick. Accept; weakest-quality item (source-quality 2). |
| 5 | "Catching prompt injections hidden in PDFs" (Lobsters) | OFF-TAXONOMY. Matched retrieval/extraction via the weak keyword "pdf" plus another hit; it is a security piece, hands-on only 2, URL slug does not even look like the title (tomclancy.info/joshua-judges-ruth.html - possible title/URL mismatch or a non-technical page). This is the D-4 item the dev says still ships. It ranks last, so no inversion, but it occupies a main slot at hands-on 2 (the floor). |

Net: 3 of 5 clearly good for Alex, 2 of 5 are false-positive-on-interest (items 3, 5). Better than slice 3 (clones and ArtCraft gone) but interest-match is still the noisiest signal: the 5 for Recalc is a halo error that inflates the dominant 0.35 weight.

## Decision: low-weight-interest consequence is NOT intended (partially)

Current code: tier low (effective weight <= 2) => base signal 1; main slots need >= 2; so every weight-2 and weight-1 interest is permanently shut out of main slots, and also out of exploration (needs >= 3).

Which interests that affects:
- Inferred (document-processing agents, production reliability): shut out is INTENDED. reader-source 2: inferred "stays at weight <= 2 and must not dominate a feed". Their keywords also overlap confirmed interests, so the items still surface through agents/retrieval.
- Confirmed low (AI safety technical side, weight 2; rust tooling, weight 1): shut out is a DEFECT. Alex explicitly confirmed them ("less", "sometimes"). Design intent (ranking-design 3) is coarse tiers where low means rare, not never. Today a hands-on interpretability repo or a Rust LLM-inference repo can never ship, in any edition, which is a pure filter-bubble effect (Kahneman: protecting serendipity). It also makes 2 of 7 confirmed interests dead letters, so the profile and the feed disagree.
- Also check: the design says tier mapping low = 1, and the 2-floor was added by me in cycle 6 without reconciling that. The inconsistency is mine as spec owner, so the fix is a spec fix, not a developer blame.

### Minimal spec fix (do not widen beyond this)
1. Tier mapping by status, in `match_interest`: low tier base = 2 when `it.status == "confirmed"`, stays 1 when `inferred`. Strong/weak logic unchanged (a lone weak hit on a confirmed-low interest drops to 1 and is still excluded by the floor, which is correct). Mid and high unchanged.
2. Do NOT change MIN_INTEREST_MATCH_MAIN, weights, or caps. A confirmed-low item scores 0.35*2 = 0.70 on interest vs 1.05 mid and 1.75 high, so it only wins a slot when hands-on, novelty and source-quality are high - that is the "rare, earned" behavior wanted. Existing 40% interest cap and top-3 cap keep it from dominating anyway.
3. Exploration: replace `interest-match >= 3` with "strong match (>= STRONG_HITS distinct hits or a non-weak title keyword) and interest-match >= 2" so confirmed-low interests are eligible for the broadening slot; keep the existing exclusions (top-3 interests, inferred interests, hands-on >= 4, tryable type). Add `strong: bool` to Scored.
4. Update docs/ranking-design.md section 3 tiers line: "low = 2 for confirmed, 1 for inferred" (I will keep the doc in sync; developer should only mirror it in rank.py and tests).

Acceptance criteria:
- A: confirmed weight-2 interest (AI safety) with a strong hands-on match (e.g. repo titled with "interpretability" + sparse autoencoder) scores interest-match 2 and is eligible for main slots at rung 0.
- B: inferred weight-2 interest (production reliability) with the same strength still scores 1 and never reaches main slots; no inferred interest is ever an exploration pick (existing test must still pass).
- C: rust tooling with no LLM/ML/agent term (non-repo) still returns no match (CONTEXT_REQUIRED unchanged); rust repo with LLM term scores 2.
- D: over a 3-day trial no confirmed-low interest exceeds 1 item per edition, and total weight-0 and inferred items in main slots stay 0.
- E: weights test still passes; 180 existing tests green except the slice 4 test asserting low interests cannot reach main slots, which is replaced by A-C.

Priority: SHOULD-FIX before edition 1, not blocking (the feed is still good without it; edition 1 simply cannot contain safety/rust). Fix in slice 5 or as a small patch; either is fine if the note in the edition report states the known gap.

## Must-fix before shipping edition 1
- MF1 (interest-match false positives, halo on the dominant signal): Recalc scored 5 on evals; PDF prompt-injection piece got a main slot at hands-on 2. Spec: (a) log per item the matched keywords and whether each came from title or summary (render in the JSON, not necessarily the markdown) so the next eval can audit rather than guess; (b) for HN/Lobsters items, keyword hits from `story_text`/summary alone (no hit in title) cap interest-match at 3 (one tier below tier max), because Show HN text bodies are long and promotional; (c) "pdf" and "extraction" become weak keywords unless a second distinct retrieval keyword is present. Acceptance: Recalc scores <= 3 and cannot outrank item 4; the injection-in-PDF piece scores <= 2 or fails hands-on >= 2 in a rung-0 edition; no previously good item (Willison writeup, agent repos titled with agent keywords) drops below 5 because of the cap. I could not verify which keywords fired on Recalc (the source label "HN: eval" is not in the scored text; the hit came from story_text), which is exactly why (a) is required.
  Severity: edition 1 can ship with this only if the user-visible report warns; I recommend fixing first because Alex's simulated 👎 on item 3 would then wrongly down-weight the evals interest via feedback (it is the interest Alex wants "more like this" on). A bad match feeding the 👎 loop damages the profile, so this is the one real blocker.
- MF2 (verify before shipping): confirm the Lobsters link tomclancy.info/joshua-judges-ruth.html resolves to a technical article matching the title. If it does not, it is a link-validity defect for QA (D3), not ranking.

## Should-fix / watch (not blocking)
- boring-marketing-skills: consider a rule that repos whose topics/description are marketing/copywriting get interest-match capped at 3. Low priority; monitor in edition 2 feedback.
- Days 2-3 shrink to 3 items at rung 3-4 (dev trial). Acceptable while stars/clone gates are young (an honest short edition beats a padded one), but if edition 1-3 average < 4 items, relax TAIL_REPO cap before the 25-star floor. The fix above for confirmed-low interests widens the pool slightly and may help.
- Weights on first feedback: step 0.05 on signals high for the item, renormalized; do not let simulated 👎 on item 3 touch evals interest weight until MF1 is done.

## Feedback integration (how weights should shift once edition 1 ships)
- Alex's simulated reactions (reader-source 3): 👍 hands-on repo/code items on agents/evals/local models; 👍 the one broadening item if hands-on (item 4 qualifies); 👎 news-only and not-interested slips; "more like this" on the best eval item - in this edition there is no real eval item, so do not apply it to Recalc (log as "none eligible").
- 👎 on Recalc after MF1: attributable to a false match, not a taste signal. Flag to user-profiler as "match-noise", no interest demotion.
- Raising hands-on and source-quality weights modestly after 👍 on repo items is fine; keep the sum at 1.0 and log each step. Keep novelty at its current weight so the broadening item survives (anti-bubble).
- Never promote inferred interests from simulated reactions (profile guardrail); confirmed-low interests (safety, rust) get no weight change until a real reaction exists.

## Rubric / spec changes
- ranking-design.md section 3: tier mapping low = 2 confirmed / 1 inferred (to be applied by me in docs, not code).
- ranking-design.md exploration clause: strong match required instead of signal >= 3.
- New: MF1 keyword provenance logging and summary-only cap.

## Blockers
- None for developer to start. MF1 is the only item I would hold edition 1 for; the low-weight fix and MF2 can ride along.
