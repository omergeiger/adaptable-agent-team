---
name: significance-rubric
description: Filters and scoring rubric for ranking AI tooling digest candidates by significance over popularity. Apply when the editor ranks candidates in the Rank phase; the orchestrator uses it to sanity-check the shortlist.
---

# significance-rubric - Ranking Candidates

Keeps "most significant" meaning the same thing every cycle: impact on people who build with AI, not buzz.

## Step 1 - Hard filters (drop, do not score)

Drop a candidate if any of these hold, and record the reason:

1. **Repeat**: it matches an item in the last 7 digests (same announcement, release, or event - compare by canonical URL and by substance, not just title). Exception: a genuine follow-up with a material change (preview -> GA, major version, reversal, shutdown); it may stay but must be written as an `Update:`.
2. **Funding <= $100M**: the item is mainly about a funding round of $100M or less. Rounds over $100M may be scored normally. Acquisitions are not funding rounds.
3. **Stale**: publish date is outside the 24 hours before the cycle time, or `date unconfirmed`.
4. **No primary source**: the only links are aggregators, social posts, forums, or secondhand coverage. Primary sources: vendor/project blog, official release notes or changelog, GitHub release or repo, paper (arXiv or venue), official docs, official press release.
5. **Off-topic**: not about AI tooling (developer tools, agent frameworks, model APIs/SDKs, coding assistants, evals/observability, AI infra for builders). General AI policy, consumer apps, or pure research without tooling impact are off-topic unless they directly change what builders can use.

## Step 2 - Score (each 0-5)

| Criterion | 0 | 3 | 5 |
|---|---|---|---|
| **Impact** - how much it changes how builders work | cosmetic | useful new capability | changes default practice or unblocks a major use case |
| **Novelty** - how new it is vs. what already existed | incremental patch | notable improvement | first of its kind or a step change |
| **Breadth** - how many builders it affects | niche tool, few users | a sizable ecosystem | most people building with AI |
| **Source strength** - quality of evidence | (filtered out) | official announcement, details thin | official source with docs, code, benchmarks, or availability |

**Total = Impact x 2 + Novelty + Breadth + Source strength** (max 25).

**Popularity scores zero.** Upvotes, trending status, social reach, and how many outlets covered it are not inputs. Use them only as leads.

## Step 3 - Select

- Sort by total, descending. Ties: higher Impact, then earlier publish time.
- Take the top 5. Include an item only if its total is **10 or more**; if fewer than 5 reach 10, publish fewer (see `loop-plugin:digest-format`).
- At most 2 items from the same vendor/project, unless nothing else reaches the bar.

## When to Apply

- **editor**: in rank-and-write mode, before writing the digest. Return the full scoring table and the dropped list with reasons.
- **Orchestrator**: spot-check that no dropped-by-rule item was published and that published items are ordered by total.
