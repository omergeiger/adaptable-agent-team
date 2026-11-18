# Ranking design - personalized-feed

Status: draft (cycle 2). Owner: tech-lead, to be refined with ranking-engineer. Implements `loop-plugin:relevance-rubric` plus the critic guardrails in `profile/alex.md`. Deterministic, stdlib, no LLM calls.

## Pipeline inside rank.py

1. Exclude filter (hard drop, observable tests only):
   - no code/repo/steps AND item_type in {article} whose title/summary matches announcement patterns ("announces", "launches", "raises", "funding", "valuation", "partnership") -> out
   - keyword excludes: crypto, blockchain, web3, NFT, "prompt hack(s)", "ChatGPT prompts", listicle regex `^\d+ (ways|tips|tricks|prompts)`, "will change", "AI art"
   - vendor test: source domain is a vendor blog AND page links a pricing/signup/demo CTA in summary -> out (S17 LangChain, S16 HF get this check)
   - awesome-lists (repo name `awesome-*`) -> out; arXiv without a repo link -> out
   - profile-driven: excludes come from the profile's Anti-interests list mapped to keyword sets in `rank.py` EXCLUDE_RULES keyed by the profile's exclude text; unknown exclude text is logged, not ignored silently.
2. Interest assignment: match candidate text (title + summary + tags) to each profile interest by keyword sets; take the single BEST-matching interest (highest tier, then match strength). Never sum rows. Weight-0 interests (classic ML) are not eligible. No match -> interest-match 0 (still eligible only as exploration candidate if hands-on).
3. Tiers: weights map to coarse tiers, so 1-point gaps never matter. Effective weight = profile weight, but `inferred` capped at 2. Tier -> interest-match signal: high (4-5) = 5, mid (3) = 3, low (1-2) = 1; keyword match strength can lower by 1 (weak match) but never raise past the tier.
4. Other signals (0-5, heuristic, stated so ranking-engineer can critique):
   - hands-on: repo=5; paper with repo link=4; article with code/steps/"repo"/"notebook"/github link=4; plain technical write-up=2; discussion=2 (HN comments valued: 3 if comments >= 50); announcement=0.
   - novelty: 5 if cluster never in ledger AND author/domain not delivered in last 7 editions; 3 if author/domain delivered recently; 1 if cluster adjacent to a delivered cluster in last 3 editions. (Ledger-seen items are already gone.)
   - source-quality: from the catalog Quality column (S1=5, S8/S9=5, S7=4, HN=4, Medium tags=2, etc.), table in `rank.py`.
   - thought-leadership: 5 for catalog "personal blog" authors flagged notable (Hamel, Eugene Yan, Simon Willison, Chip Huyen, Raschka, Lilian Weng), 3 for maintainers of a repo with >= 5k stars, else 1. Heuristic; ranking-engineer may revise the list.
5. Score = sum(weight_i * signal_i), default weights interest 0.35 / novelty 0.20 / hands-on 0.20 / thought-leadership 0.15 / source-quality 0.10, loaded per user from `<user>-weights.json`. Every Selection item stores the five signals, the total, the matched interest and tier.
6. Form preference: profile says hands-on is a strong preference. Items with hands-on <= 1 are dropped unless needed to meet D2 (see relaxation).

## Selection (greedy, constraint-aware)

Target n = 5 (min 3). Sort by score; pick greedily subject to:
- Interest cap: no interest > floor(0.4 * n), min 1 (n=5 -> 2, n=3-4 -> 1). Counted on the single matched interest.
- Cluster cap: 1 item per cluster_key (same-day dedup) and 1 per author/domain.
- Source-type diversity (D2): after greedy fill, if distinct source_types < 3, swap the lowest-scored item whose type is duplicated for the best remaining candidate of a missing type.
- Exploration slot (one per edition): the best-scoring candidate with hands-on >= 4 whose matched interest is NOT in the top 3 by weight (i.e. not agent frameworks / evals / local models), and that is not an inferred interest being promoted. Gets `exploration=True`, rendered with the label "Broadening pick" in its Why line. If none qualifies, ship without it and report it (do not lower the bar).
- Inferred interests (document-processing agents, production reliability): eligible at cap weight 2, never counted as the exploration pick, and never raised by simulated reactions.

Relaxation order if constraints cannot be met (warn in run report each time): (1) lower hands-on floor to 2; (2) lower n to 4, then 3; (3) allow a 2nd item for a capped interest. Never relax: >= 3 source types, real links, no ledger repeats, excludes. If still unsatisfiable, ship nothing and report why (a short honest feed beats a bad one, but D2/D3 say 3-5 items so this is an alarm, not a normal state).

## Feedback re-weighting (D6)

Exactly per the rubric: on 👍 / "more like #n" add +0.05 to each signal that scored >= 4 on item n; on 👎 / "less like #n" subtract 0.05 from those; renormalize to 1.0; clamp each weight to [0.05, 0.50] before renormalizing; log (date, event, item, deltas, before/after) in `<user>-weights.json`. 👎 also emits an interest flag (matched interest + reason) in the engagement log for user-profiler; code never edits the profile's interest table. Simulated events (reader-source section 3) are tagged `simulated`, adjust signal weights normally, but do not promote inferred interests (guardrail).
Unit property: weights always sum to 1.0 (+/- 1e-9); a 👍 then identical 👎 returns to the starting weights within clamp effects.

## Where human judgment plugs in

ranking-engineer reviews real editions against taste and revises: keyword sets, notable-author list, quality table, hands-on heuristics. Those are data tables in `rank.py` (plain dicts), so changes are small diffs, not redesigns. Any change to default signal weights or the selection rules needs a critic GO/NO-GO.

## Slice 1 (first build): ingestion adapters + dedup ledger

Scope: `pfeed/http.py`, `models.py`, `adapters/*` (github, hn, lobsters, arxiv, rss; hfpapers optional), `ledger.py` (canonical_url, cluster_key, Ledger read/append), `requirements.txt` (pytest), `tests/` with fixtures. NOT in this slice: profile parsing, ranking, rendering, feedback, pipeline.

Acceptance criteria:
1. `cd projects/personalized-feed && .venv/bin/python -m pytest -q` exits 0 with zero failures/errors; QA reports the exact command and summary line (test-gate).
2. Every adapter returns `list[Candidate]` from a fixture via an injected fake `http`; no test touches the network. Fixtures are captured from the verified endpoints (S1, S3, S5, S7, a blog RSS, a Substack RSS, an Atom feed).
3. Fields: each Candidate has non-empty title, https url, canonical_url, source_type, item_type; malformed entries are skipped, not raised.
4. Fail-soft: `http` raising timeout/HTTP 429/500/garbage body yields an empty list and a recorded error for that source; other sources still return. One retry with backoff is exercised (fake sleep).
5. arXiv adapter drops papers with no `github.com/...` link in abstract/comment; GitHub adapter drops `awesome-*` repos.
6. `canonical_url` tests: utm/ref stripped, `www.` and trailing slash and fragment normalized, http->https, HN story pointing at a GitHub repo canonicalizes to the repo URL.
7. `cluster_key` tests: repo URL and repo link extracted from an arXiv abstract give the same `gh:owner/repo`; arXiv `v1`/`v2` give the same `arxiv:<id>`.
8. Ledger: append then reload round-trips; `seen()` hits on same canonical_url OR same cluster_key; file is markdown table readable by humans; appending to a missing file creates it with header; a crash before append (not calling append) leaves ledger unchanged.
9. A separate explicit `python -m pfeed check-live` (not in pytest) hits each endpoint once and prints status counts; run once by QA and recorded (not part of the gate).
10. No dependency other than pytest; no secrets; User-Agent `personalized-feed/0.1`.

Critic GO/NO-GO: not required for slice 1 (reversible plumbing). Required before locking the ranking defaults in slice 2.
