# Cycle 10 critic: edition 3 review + Slice 7 GO/NO-GO

## Verdict: SHIP-WITH-NOTES (edition 3) / GO-WITH-CONDITIONS (Slice 7)

## Adversarial read of feeds/2026-11-19-03.md
1. **morajabi/poo** - Real repo (78 stars, Rust, pushed 3 days ago, checked via GitHub API). It is a macOS disk-space cleaner for dev junk (builds, caches, simulators, agent worktrees) with an MCP server on the side. It is NOT an agent framework. The feed's "why" says it "ties to your agent frameworks / orchestration / tool use interest (matched: mcp)". That is an overclaim: one incidental MCP mention inflated to the top interest. Alex would click out of curiosity (Rust, tryable), but would feel mis-sold. Honest label: Rust tooling, broadening.
2. **Rivet (Launch HN)** - Genuine bullseye: repo, agent orchestration, clone-and-run. Mild vendor-launch flavor (YC), but the link is the repo. Would click.
3. **[AINews] The No AI Slop Manifesto** - Noise for Alex. A newsletter digest/opinion piece, nothing to try. The "why" text ("follow the write-up and try the steps") is false. It was scored interest-match 4 / hands-on 4 on a single summary-only `llama.cpp` mention, which is how a news roundup passed the main-slot floor of 3. That is exactly the "news with nothing to try" he said he does not want.

Filter bubble: not the problem here. Two of three are agent items, but the reverse failure is present: the feed is thin (3 items, D3 minimum), D2 is met on the minimum (3 types), and rung 4 relaxations fired (hands-on floor 1, size 5 -> 3, 2nd item for capped interest), with no exploration pick. Staleness: no ledger repeats (QA confirmed). Links: 200s.

## Top risks (pre-mortem)
- R1 Digest/roundup pages pass as hands-on matches (item 3). Kills the feed by training Alex to ignore the Substack slot. Not addressed by Slice 7 (which targets lone generic words, not summary-only mentions of a specific keyword in a news digest). Fix: cap interest-match and hands-on for Substack/newsletter roundups ("AINews", "weekly", "digest", "roundup") the way SUMMARY_CAP_SOURCE_TYPES caps promotional bodies, or require a title/body hit for article items.
- R2 Reason text overclaims (items 1 and 3). Kills trust: a "why" that names an interest the item is not about is worse than no reason. Fix: for summary-only, single-keyword matches use hedged/broadening wording, and never use the "try the steps" template for non-tutorial articles.
- R3 Pool exhaustion on same-day reruns (edition 3 of the day). Expected, and the relaxation ladder degraded gracefully and honestly (warnings are truthful). Not a product bug, but edition 3 should not be read as evidence about steady-state quality. Note for roadmap: warnings are in the JSON sidecar only; the markdown edition does not tell Alex it is a degraded edition.
- R4 Single-keyword `mcp` match still promotes tool-adjacent repos to tier "high". Same class as the lone-generic issue; consider adding `mcp` to a lone-keyword cap (needs a second distinct hit).

## Slice 7 GO/NO-GO: GO, with conditions
- Generic-keyword rule (agent/agents/agentic/llm/ai capped at 2, never strong; ranks by signal first): sound, cheap, and it did its job on item 2 (backed by orchestrat). Note item 1 survived because `mcp` is not generic and the rule counts it as a second hit; see R4.
- Exploration min match 3 -> 2, and pool changed from `eligible` (which required main-slot min match 3) to all scored items at the hands-on floor: this is the riskier half. It is defensible against the failure "exploration never fires" (it did not fire in edition 3 anyway, so the change is unproven in the wild). Conditions: (a) keep the strong-match requirement and the Substack exclusion (present); (b) require the exploration pick to be non-generic-only (the lone-generic cap already forces strong=False, which covers this - verify with a test that a lone `ai` hit cannot be the exploration pick); (c) re-check on the next edition where an exploration item actually ships; if it is an interest-match-2 item with a thin reason, revert to 3. Commitment-bias note: do not defend the lowering because the sunk effort exists; judge it on the first shipped exploration pick.

## Simulated reactions applied (D9), per reader-source.md section 3
Command: `pfeed feedback --user alex --edition feeds/2026-11-19-03.json --event ... --simulated` (all logged tag `simulated` in profile/alex-weights.json).
- 👍 #1 poo: hands-on Rust repo, serves as the "broadening" item (Rust tooling is outside the top interests). Applied despite the mislabel; the signal reward lands on hands-on/novelty/source-quality, not on the agent-frameworks interest, but note the system recorded it under that interest.
- 👍 #2 Rivet: hands-on agent framework repo.
- 👎 #3 AINews manifesto: news/opinion, nothing to try. This raised an interest flag against "running models locally / small models / quantization" for user-profiler, which is a MISATTRIBUTION: Alex has no complaint about local-model content, the item was merely mis-tagged to it. User-profiler must NOT downweight that interest from this flag.
- "More like this": none (no eval-related item in the edition).
- Neutral: none (all three items reacted to).
Resulting weights: interest-match 0.281, novelty 0.203, hands-on 0.250, thought-leadership 0.138, source-quality 0.128.

## Recommendation
Ship edition 3 (it is already written; links live, no repeats). Before edition 4: fix R1 and R2, consider R4, add the exploration test in (b), and have user-profiler discard the simulated local-models flag from #3.
