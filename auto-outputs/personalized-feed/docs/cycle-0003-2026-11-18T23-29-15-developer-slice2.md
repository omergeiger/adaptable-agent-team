# Cycle 3 - developer - Slice 2 notes

Implemented: QA-1 fix (non-list items/hits -> FetchError, xfails removed), recency filter, profile parser, rank + rank_data, feedback (D6 weights), render + sidecar, pipeline + CLI (`daily`, `feedback`). Ledger now adds a table header to a preamble-only file (alex-delivered.md has none).

Default weights (rubric, unchanged): interest 0.35, novelty 0.20, hands-on 0.20, thought-leadership 0.15, source-quality 0.10. Critic GO/NO-GO still required before locking.

Judgment calls for ranking-engineer / critic:
- Design says "hands-on <= 1 dropped" and "relax floor to 2": inconsistent. Default floor = 2 (drop <=1), relaxation lowers to 1.
- Novelty: 5, or 3 if author/domain (GitHub owner or host) delivered in last 7 editions. The "adjacent cluster = 1" case is NOT implemented (undefined); ledger lacks interest tags.
- Match strength: strong = >=2 distinct keyword hits or a title hit; weak lowers the signal by 1. Ties within a tier break on hit count.
- Unmatched items are eligible only as the exploration pick.
- Recency window default 14 days; undated kept.
- Feedback renormalization can slightly lower a boosted weight when others are small; group share still rises.
- Not done: appending to the profile's Engagement history (feedback returns interest flags and logs to weights.json only).

Live trial (temp dir only, ledger in temp): 33/33 sources ok, 1947 fetched, 1454 stale, 5 items across blog/GitHub/HN. Quality observation: brand-new GitHub repos with 0-2 stars dominate (source-quality flat 4 for GitHub; no stars signal). Suggest ranking-engineer consider a stars/traction term in source-quality; HN item #4 delivered as a repo (target link), source_type HN.
