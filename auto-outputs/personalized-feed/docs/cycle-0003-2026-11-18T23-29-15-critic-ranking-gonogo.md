# Critic - ranking defaults GO/NO-GO (cycle 3)

Scope: rank.py, rank_data.py, docs/ranking-design.md, developer slice-2 note. Code not edited.

## Verdict: CONDITIONAL GO on weights; NO-GO on shipping the selection rules as-is

Weights (0.35/0.20/0.20/0.15/0.10) are defensible and should NOT be retuned; the failures come from signal definitions and one selection bug, not the weights. Lock weights only after fixes 1-4 below.

## Pre-mortem: the feed has failed Alex. Top causes

### R1. Exploration slot is an unmatched-junk slot (bug; likely the source of the 0-star repo problem)
`_exploration_pick` filters `s.interest not in top and s.interest not in inferred`. An unmatched item has `interest == ""`, which is in neither set, so any item with no interest match and hands-on >= 4 qualifies. It is then added to `chosen` first, bypassing `_fits` (no cluster/author check). Among unmatched items the winner is the highest total, i.e. novelty 5 + hands-on 5 + GitHub quality 4: a random brand-new repo. Design says the pick must come from a real non-top interest (rust, safety, observability, ...). Kill scenario: every day one slot is a random fresh repo labeled "Broadening pick" that Alex has no reason to care about; he learns to skip the label.
Addressed? No. Fix: require `s.interest` truthy and matched tier != "" (and apply `_fits` to the pick).

### R2. Hands-on + novelty structurally favor new repos; no traction signal
Arithmetic with defaults: a bare repo (strong match, new owner) = 1.75+1.0+1.0+0.15+0.40 = 4.30. Plain article by a non-notable blog = 3.60. Plain Simon Willison article = 4.40. So any new repo beats every non-notable article, and ties the notable ones. Novelty is 5 for every new repo (never in ledger, new owner) so freshness is rewarded exactly where quality is unknown. GitHub source-quality is a flat 4, and thought-leadership gives 1 to a 0-star and a 4,900-star repo alike (cliff at 5000). Nothing separates a 0-star from a 3k-star repo. Kill scenario: 3 of 5 daily items are "my-agent-framework" with 0-2 stars; Alex stops opening it in a week.
Addressed? No. Yes, a traction term is needed (see Required change 2).

### R3. Keyword leakage creates noise and inflates hands-on
`_has` is raw substring: `"repo"` matches "report/reporting/repository", `"code"` matches "encoded/decode/barcode", `"tutorial"`, `"notebook"` fine. `_tryable` => hands-on 4 for articles and also exempts announcements from the exclude. A "quarterly report" announcement with "code" anywhere passes. Interest keywords use `\b` prefix (ok) but "agent", "mcp", "production", "document", "trace", "schema", "pdf" are generic; "agent" hits on nearly every 2026 AI repo title, giving strong match from a single title hit.
Addressed? No. Fix: word-boundary regex for TRYABLE_WORDS; remove bare "code"/"repo".

### R4. Echo chamber on agents (and the top-3 interests)
Cap is floor(0.4*5) = 2 per interest, so agents can take 2 of 5 every day, evals and local models 2 more: up to 80% top-3 interests, 1 slot of "broadening" (which R1 corrupts). The final relaxation rung lets 2 of 3 be one interest. Novelty is author/domain only; "adjacent cluster" was dropped, and every new agent repo is a new cluster, so the same topic ("another agent framework") repeats daily with full novelty score. No topic-level fatigue.
Addressed? Partly (cap, D2 types, exploration slot) but each guardrail has a hole. Fix: topic fatigue and a top-3 cap (below).

### R5. Thought-leadership is a six-name list
15% weight, effectively "is it by one of 6 authors", else 1 for everyone. It is a hardcoded confirmation-bias term: it re-surfaces the same few authors (also capped by domain novelty, which drops them to 3 on repeat only 7 editions). Not fatal, but it is 15% of the score carrying near-zero information for ~95% of candidates. Revisit after real feedback, not now.

### R6. Relaxation silently erodes the hands-on guardrail
Floor drops to 1 before n shrinks. Acceptable, but the warning is only in the run report. If D2 (3 source types) is hard to satisfy, floor 1 is the normal state and the "strong preference" quietly disappears. Check in the trial: how often does rung 1+ trigger?

### R7. Minor
- HN item delivered as a repo with source_type HN: stars unknown, so any stars term must fall back to HN points for those.
- No test of the actual trial's selected 5 against "would Alex click"; one-sentence-why rule: a 0-star repo cannot pass it.

## Required changes (small, ordered)

1. Exploration: `s.interest` must be non-empty and not in top/inferred; run `_fits` on it. (2 lines.)
2. Traction term (yes, needed). Add `traction(c)`; for repos use stars, for HN-linked use points if present. Suggested: GitHub source-quality = 1 if stars < 10, 2 if < 50, 3 if < 200, 4 if < 1000, 5 if >= 1000; and thought-leadership 3 at >= 1000 (not 5000). Plus a hard gate: GitHub repos under 10 stars are dropped unless the repo is the target of an arXiv/HN item (so the signal is not zero-traction). Age-adjust: a repo < 7 days old with >= 50 stars counts as 4 (velocity), so genuinely hot new repos still surface.
3. TRYABLE_WORDS: match with `\b` (and drop "code", "repo", keep "github.com", "repository" explicitly). Add a test with "quarterly report".
4. Top-3 guardrail: at most 3 of 5 items from top-3 interests combined (i.e. >= 2 from others incl. exploration), not just 2 per interest. Keep the existing per-interest cap.
5. Cheap topic fatigue: count editions where an interest was delivered; if the same interest hit >= 3 of the last 5 editions, novelty 3 for it. Needs interest tag in ledger (or recompute from ledger titles); if costly, defer and log as a risk, but do not claim "novelty" covers topics.
6. Run report: print signals + total + matched interest for each chosen item, and count of relaxation rungs used across the trial editions.

## What to check on the re-trial before GO is final
- Median stars of delivered GitHub items >= 50; no item that fails the "one sentence why Alex cares" test.
- Agents + evals + local models <= 3 of 5; exploration pick has a real matched non-top interest.
- Source types >= 3 without hitting relaxation rung 1 on most days.
- Weights unchanged (0.35/0.20/0.20/0.15/0.10).

Circle of competence: I did not see live editions or Alex's click data; the arithmetic above is from the code. Treat the numeric thresholds in change 2 as starting guesses for ranking-engineer to tune on real output.
