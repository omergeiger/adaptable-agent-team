# Critic: edition 1 Verify gate (cycle 8)

Candidate: /tmp/pfeed-critic-rCGj/2026-11-19-01.md (temp dir only; real feeds/ and profile untouched). All 4 URLs fetched 200 and descriptions match titles. No fabricated or broken links.

## Verdict: GO (conservative D9 default), with 3 logged defects for slice 6

Format passes: 5 items, 3 source types (blog, GitHub, arXiv), links real, no duplicates, no not-interested topics (no crypto/funding/listicles). Echo-chamber check: agents is NOT dominating (2 of 5 labelled agents, 1 local models, 2 observability) - the opposite risk is present: labels are loose.

## Item-level concerns
1. aws-emulator (Simon Willison): real, hands-on, good. But it is a local AWS test emulator, not an agent framework; "agent frameworks" interest-match 5 is over-credited (adjacent to testing/evals at best). Why-line is generic template text.
2. rust-anything: real, 3504 stars. It is a Rust-migration tool; matched via topic:mcp. Honest fit is "rust tooling" (Alex's LOWEST weight), scored as top-weight agent interest 5. Still try-able; a plausible click.
3. inside-llm (gguf): fine fit for local models, hands-on. Unverified depth beyond README; acceptable.
4. antigravity-token-monitor: 29 stars, source-quality 2, Google Antigravity-specific; labelled "broadening" but is inside top-5 observability interest, so it is not really serendipity. Weak but harmless.
5. ALIVE (streaming video models): WRONG-MATCH. Why-line claims it ties to "observability / tracing for LLM pipelines"; it is a video-generation paper. This is a false rationale, would be a 👎 click-skip. Kept only because it supplies the third source type. Interest-match 2 should not clear the bar; it indicates the relaxation/diversity filler.

## Risks (pre-mortem)
- Keyword-topic mislabeling (items 1, 2, 5): the "why" sentence asserts a tie the content does not have. Trust killer once Alex notices. Addressed? No.
- Weak-only match (QA's known issue): not visible in this edition (no Lobsters item surfaced), so it is masked, not fixed. Addressed? Partly (slice 5 tests).
- Over-quarantine noise: log shows many valid-seeming items dropped (OCaml/ML pages "not technical", cert-verify failures on one host = local CA issue, medium 403). Cert failure is environmental, not content; it silently shrinks the pool and may bias against older/academic hosts. Not a shipping blocker.
- Arxiv item with no abstract-level evidence of relevance: diversity enforced by quota over relevance.
- Staleness: ledger written for dedup; all dates within 8 days. OK. Cross-edition repeat protection untested until edition 2.

## Must-fix (not blocking edition 1)
- Rationale must only cite interests with a genuine content match; ALIVE-type items (match <=2) should be dropped even if a source-type quota goes unmet (3-5 items allowed; log the shortfall instead).
- Distinguish true "broadening" (outside top-5 interests) from exploration inside them.
- Simulated reactions: expect 👎 on #5, neutral on #4, 👍 on #2/#3 (hands-on).
