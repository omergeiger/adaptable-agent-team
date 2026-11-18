# Profile - alex
**Role:** ML engineer (~7 yrs), builds internal LLM tools at a mid-size logistics company · **Created:** 2026-11-18 · **Last refined:** 2026-11-18
**Source of truth:** steering/personalized-feed/reader-source.md (D8). Nothing here comes from workspace context.

## Goals
- Find things to TRY: a repo to clone on a Friday, a paper with code, a writeup from someone who shipped it. (confirmed)
- Learn new approaches in agent systems and LLM app quality; keep up the "boring reliability" mindset from classic ML. (confirmed)
- Broaden horizons, but only through hands-on items (D1, reader-source 3). (confirmed)

## Content-form preference
- Prefer: hands-on / tryable (repo, paper with code, reproducible writeup, practitioner post-mortem). Weight: strong.
- Neutral: plain technical write-ups with concrete detail.
- Avoid: news/announcements with nothing to try, trend think-pieces ("10 ways AI will change X").

## Interests (weighted)
Weights follow the order Alex listed them (higher = cares more). Ties are only used where order is adjacent and weights are close; list order breaks ties.
| Interest | Weight (1-5) | Status | Notes |
|---|---|---|---|
| agent frameworks / orchestration / tool use | 5 | confirmed | "the main thing right now" |
| evals for LLM apps (agent evals, prompt regression testing) | 4 | confirmed | listed 2nd; "more like this" candidate |
| running models locally / small models / quantization | 4 | confirmed | listed 3rd; owns a 4090 |
| retrieval beyond naive RAG - structured extraction from documents | 3 | confirmed | listed 4th |
| observability / tracing for LLM pipelines | 3 | confirmed | listed 5th |
| AI safety/alignment (technical, hands-on side only) | 2 | confirmed | "less"; conceptual/policy pieces excluded |
| rust tooling | 1 | confirmed | "sometimes"; learning slowly |
| document-processing agents (shipping docs, support copilot) | 2 | inferred | from his job description; overlaps confirmed extraction/agents. Do not let it dominate |
| production reliability / hardening of LLM apps | 2 | inferred | from "still care about evals and boring reliability stuff" |
| classic ML: demand forecasting / time series | 0 | inferred | past experience only; watch-only, excluded from ranking until engagement shows otherwise (critic, cycle 1) |

Inferred rows are proposals: ranking treats weight as capped at 2 until confirmed by engagement (D6/D9).

## Anti-interests / excludes
- crypto (anything)
- funding / valuation news
- prompt "hacks" listicles
- AI art drama
- vendor marketing posts dressed up as tutorials
- generic "how AI will change X" think-pieces
- news/announcement items with nothing to try (stated via simulated 👎 rule)

## Preferred sources / authors
- GitHub trending (repos)
- Hacker News (comment threads valued more than the links)
- r/LocalLLaMA
- arXiv, only when code is available
- a few Medium / Substack engineering blogs (specific ones not named; source-scout to propose)
- lobste.rs (sometimes)
- Constraint: public APIs/RSS only; skip anything needing auth or a ToS decision (reader-source 2).

## Engagement history (signal)
(empty - no editions shipped yet. Simulated reactions are logged here as `simulated` after each edition, per D9.)

## Ranking guardrails (critic pre-mortem, cycle 1)
- Max 40% of an edition's items per interest; dedupe by project/topic cluster, not only URL.
- 1 labeled exploration slot per edition: hands-on, outside the top 3 interests.
- Score each item against its single best-matching interest; never sum overlapping rows.
- Treat weights as coarse tiers (high 4-5 / mid 3 / low 1-2); no decisions on 1-point gaps.
- Do not promote inferred interests from `simulated` reactions.
- Excludes need observable tests (no code/repo/steps = out; vendor domain with product CTA = out).
