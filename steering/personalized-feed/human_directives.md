## Standing Directives

D1. User #1 is Alex, an AI professional. Goal: learn new technologies, approaches, and thought leaders, broaden horizons, and get pointers for hands-on coding or repositories to explore. Default interest weight toward agentic systems / LLM tooling - but treat this as a seed, not fixed: the user-profiler must actively capture and refine the real interest profile.

D2. Sources must include GitHub, Medium, and technical forums. Each daily feed spans at least 3 distinct source types - source diversity is required, not optional. Prefer official APIs/RSS; flag any source that needs fragile scraping.

D3. Daily feed = 3 to 5 items. Every item carries a real, verifiable source link and a short "why it's worth investigating." Never fabricate items or links.

D4. Delivery channel is a daily Slack push via a Claude bot. Slack is out of scope for this run: the canonical output is a numbered feed edition, `projects/personalized-feed/feeds/<YYYY-MM-DD>-NN.md`.

D5. The system must support onboarding additional users and capturing their preferences - do not hardcode to a single user.

D6. Ranking must incorporate easy human feedback (e.g. thumbs / more-less-like-this) to iteratively improve recommendation quality.

D7. No item already shown to a user may be resurfaced - maintain a per-user dedup ledger of delivered items.

D8. Everything known about Alex comes from `steering/personalized-feed/reader-source.md` - read it, never edit it. Never infer the reader's identity or interests from the workspace, repository, git history, environment, or tool context.

D9. This run is unattended: no human will answer Open Questions or give feedback. Never wait or block on human input and never use `## Loop Signal: block`. When a question arises, check reader-source.md section 2 first; otherwise adopt the conservative default, record it under Key Decisions, and continue. Human feedback for D6 is simulated: after each edition ships, apply Alex's reactions from reader-source.md section 3 and log them as `simulated`.

D10. Run length is 3 feed editions. Once the team reaches the Operate phase, every cycle ships exactly one edition. After edition 3 ships, end the run with `## Loop Signal: done`.

## Cycle Overrides

<!-- One-off instructions; supersede consensus Next Action. Remove when satisfied. -->

## Answers

<!-- Responses to Open Questions from consensus.md. -->
