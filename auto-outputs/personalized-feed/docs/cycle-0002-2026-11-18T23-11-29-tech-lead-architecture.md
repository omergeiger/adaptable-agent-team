# Cycle 2 - tech-lead - architecture decision record

Slice: architecture + ranking design docs (no code). Outputs: projects/personalized-feed/docs/architecture.md, ranking-design.md.

Decisions (one-line rationale each)
- Single stdlib Python package `pfeed`, one CLI entry `python -m pfeed daily --user <id>` - majestic monolith, nothing to deploy.
- Markdown ledger and profile, JSON only for 5 signal weights - human-readable, git-diffable, tiny data (D5, D7).
- Dedup on canonical URL OR cluster key (gh owner/repo, arxiv id), HN/lobste.rs resolve to target URL - critic guardrail "cluster, not only URL".
- Ranking is deterministic, no LLM in code path; heuristics are plain data tables ranking-engineer can tune - testable and cheap to change.
- Selection: 40% cap via floor(0.4n) min 1, one exploration slot (hands-on, outside top 3 interests), tiered interest-match (5/3/1), inferred capped at 2 - straight from profile guardrails.
- Relaxation order defined; never relax D2 source types, links, ledger, excludes - the feed-quality bar is non-negotiable.
- Skip GitHub trending HTML, Reddit, Papers with Code - scraping/blocked/ToS (D8).
- Slack out of scope (D4); renderer is the single output seam.

Gate status: no code yet, so test suite N/A (not red). Feed-quality bar: not applicable until first edition.
Maturity deltas: architecture missing->draft; ranking design missing->draft; ingestion/ledger/render/feedback remain missing.
Open for others: ranking-engineer to review heuristic tables (notable authors, hands-on scores, quality map); critic GO/NO-GO on ranking defaults before slice 2 is locked; qa-engineer to confirm slice 1 acceptance criteria are testable.
Next slice: Slice 1 = ingestion adapters + dedup ledger with offline tests (criteria in ranking-design.md, section "Slice 1"). Developer builds; qa-engineer runs the test gate.
