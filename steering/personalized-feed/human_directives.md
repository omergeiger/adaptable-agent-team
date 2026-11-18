## Standing Directives

D1. User #1 is Alex, an AI professional. Goal: learn new technologies, approaches, and thought leaders, broaden horizons, and get pointers for hands-on coding or repositories to explore. Default interest weight toward agentic systems / LLM tooling - but treat this as a seed, not fixed: the user-profiler must actively capture and refine the real interest profile.

D2. Sources must include GitHub, Medium, and technical forums. Each daily feed spans at least 3 distinct source types - source diversity is required, not optional. Prefer official APIs/RSS; flag any source that needs fragile scraping.

D3. Daily feed = 3 to 5 items. Every item carries a real, verifiable source link and a short "why it's worth investigating." Never fabricate items or links.

D4. Delivery channel is a daily Slack push via a Claude bot. Until Slack credentials are wired by the human, the canonical output is `projects/personalized-feed/feeds/<date>.md`.

D5. The system must support onboarding additional users and capturing their preferences - do not hardcode to a single user.

D6. Ranking must incorporate easy human feedback (e.g. thumbs / more-less-like-this) to iteratively improve recommendation quality.

D7. No item already shown to a user may be resurfaced - maintain a per-user dedup ledger of delivered items.

## Cycle Overrides

<!-- One-off instructions; supersede consensus Next Action. Remove when satisfied. -->

## Answers

<!-- Responses to Open Questions from consensus.md. -->
