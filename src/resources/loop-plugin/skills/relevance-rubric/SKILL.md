# relevance-rubric - Ranking & Feedback Re-weighting

**Audience: agent-applied (loop-plugin:relevance-rubric).** Keeps how items are scored and how human feedback adjusts that scoring stable and explainable across cycles.

## Rubric

Score each candidate item 0-5 on five signals, against the active user's profile:

| Signal | 0 | 5 |
|---|---|---|
| **interest-match** | unrelated to any profile interest | squarely on a top stated interest |
| **novelty** | user has seen this idea/repo many times | genuinely new tech / approach / author to them |
| **source-quality** | low-signal, unvetted | reputable maintainer / author / venue |
| **hands-on** | nothing to try | clear path to clone/run/build something |
| **thought-leadership** | anonymous rehash | from or about a notable thought leader |

**Item score** = weighted sum of the five signals. Default weights: interest-match 0.35, novelty 0.20, hands-on 0.20, thought-leadership 0.15, source-quality 0.10. Record each item's per-signal scores and the weighted total - never emit an opaque score.

Select the top 3-5 after applying the dedup ledger (D7) and ensuring ≥3 distinct source types (D2); if the top-ranked set is too homogeneous, swap the lowest-ranked duplicate-type item for the best item of a missing type.

## Feedback re-weighting

- 👍 / "more like #n": increase the weight of the signals that scored high on item n (small step, e.g. +0.05, renormalize).
- 👎 / "less like #n": decrease the weight of the signals that scored high on item n; and flag any interest tag on that item to user-profiler for possible demotion.
- Keep weights normalized to sum 1.0. Log every adjustment with the triggering feedback so changes are auditable and reversible.

## When to Apply

- ranking-engineer owns this rubric, judges actual feed results against it with human judgment, and specs the scoring for the developer to implement programmatically.
- developer implements the scoring + feedback re-weighting in `src/` per this rubric and the ranking-engineer's spec; the relevance-signal numbers shown per feed item (`loop-plugin:feed-item-format`) are produced by that code and reviewed by ranking-engineer.
- user-profiler consumes the 👎 interest flags to refine the profile.
