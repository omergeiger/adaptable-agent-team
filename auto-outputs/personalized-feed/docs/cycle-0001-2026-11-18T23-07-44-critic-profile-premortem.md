# Critic pre-mortem: alex profile (cycle 1)
Sources read: projects/personalized-feed/profile/alex.md, steering/personalized-feed/reader-source.md (D8).

## Assume the feed failed Alex. Top causes
1. **Echo chamber on agents.** Weight 5 vs 4/4/3/3 is a steep ladder, and the "tryable" form filter stacks on top. Result: 10 agent-framework repos, near-duplicate (same framework, same week's HN spike). Fix: cap any single interest at ~40% of an edition and dedupe by project/topic cluster, not only by URL.
2. **Hands-on-only filter kills the broadening he asked for.** Goal 3 ("broaden horizons") is satisfied only via hands-on items; if the ranker treats "tryable" as a hard gate, safety (w2), rust (w1) and anything new gets zero slots. Fix: reserve 1 explicit exploration slot per edition, drawn from outside the top 3 interests, and label it as such.
3. **Inferred interests leak.** The 3 inferred rows overlap confirmed ones, so double-counting is the risk:
   - document-processing agents: overlaps agents (5) + extraction (3). One item can score on all three and rise above its true worth. Fix: score an item against its single best-matching interest, never sum.
   - production reliability: overlaps evals (4) + observability (3). Same double-count. Also a "boring reliability" quote is a mindset, not a topic request.
   - forecasting / time series: no stated wish to read it. Recommend keeping it OUT of ranking entirely (weight 0, "watch only") until engagement shows otherwise. Past job is not a current interest.
4. **Weights read as precise when they are only list order.** "4 vs 4" for evals/local models and "3 vs 3" are ties made up from ordering. Over-fitting to ordinal data. Fix: treat as coarse tiers (high / mid / low), not decimals; no ranking decisions on 1-point gaps.
5. **Source skew.** Preferred sources are all high-volume and trend-driven (GitHub trending, HN, r/LocalLLaMA): social-proof risk, "popular" is not "valuable to Alex". Fix: require items to pass the one-sentence test ("why Alex would try this Friday"); source-scout to add 2-3 low-volume engineering blogs (he named none).
6. **Simulated feedback loop is self-confirming.** Reactions come from a fixed rule in the same file the profile is built from, so engagement will only confirm confirmed interests (D6/D9 bias). Do not treat simulated thumbs-up as evidence to promote inferred interests; mark `simulated` and keep inferred caps.
7. **Ambiguous exclusions.** "Vendor marketing dressed as tutorial" and "announcement with nothing to try" need an observable test (no code/repo/steps = out; vendor domain with product CTA = out), else the ranker lets them through and Alex downvotes them.

## Is the plan addressing it?
Partly. Inferred cap at 2 and the excludes list are good. Missing: per-interest share cap, cluster dedupe, exploration slot, no-sum rule, tiering of weights.

## Verdict: GO (conditional)
Concrete changes before ranking spec is frozen:
1. Max 40% of items per interest; cluster dedupe.
2. 1 labeled exploration slot per edition (hands-on, outside top 3).
3. Score by best single interest; no summing across overlapping rows.
4. Drop forecasting to weight 0; keep the other two inferred rows capped at 2.
5. Treat weights as tiers; no tie-breaking on 1-point gaps.
6. Write observable tests for each exclude.
7. Do not promote inferred interests from simulated reactions.
