# Run Report - personalized-feed (re-run)

- **Branch:** `example/personalized-feed` (rebuilt from `main` @ 8657d1a)
- **Date:** 2026-11-19, 01:07-05:24 (Asia/Jerusalem), ~4h17m wall clock, ~3h of it rate-limit waits
- **Launch:** `.venv/bin/python loop.py --cycles 10` (continuous, git_sync on, verbosity on, claude-sonnet-5-5)
- **Mode:** unattended - fictional reader "Alex" (`steering/personalized-feed/reader-source.md`), no human input during the run
- **Outcome:** 3 of 3 feed editions shipped; loop exited cleanly on `Loop Signal: done`

## Why a re-run

The original June run (9 cycles) used the broken agent path: `/adapt` had written agents to `src/resources/loop-plugin/.claude/agents/`, which Claude Code never loads, so the role personas never ran. It was also run for a real reader and renamed to "Alex" afterwards. The re-run fixes both: agents live in `src/resources/loop-plugin/agents/`, and the reader is fictional from the start, sourced only from `reader-source.md` (D8).

## Setup (commits before launch)

| Commit | Content |
|---|---|
| f97da42 | Port of the June adaptation: 7 persona agents, 4 loop skills, PROMPT.md domain rules, starter steering, config |
| 7112496 | `reader-source.md` (fictional Alex + answers given in advance + simulated reaction rules); D8 (reader source only), D9 (unattended: never block, simulate D6 feedback), D10 (3 editions, then `done`); edition naming `feeds/<YYYY-MM-DD>-NN.md` |

**Squad (persona mental models):** tech-lead (DHH, lead), user-profiler (Don Norman), source-scout (Ben Thompson), ranking-engineer (Daniel Kahneman), developer (Kent Beck), qa-engineer (James Bach), critic (Charlie Munger).

**Stop design:** two parts. The intended stop is the domain rule D10 (Build, then Operate; one edition per Operate cycle; `done` after 3 editions). The backstop is `--cycles 10`, which caps successful cycles per launch.

## Cycle by cycle

| # | Start | Result | Phase | What happened |
|---|---|---|---|---|
| 1 | 01:07 | OK · $0.66 · 3m | Profile → Architect | Alex's profile built from `reader-source.md`. Critic GO with guardrails (40% cap per interest, an exploration slot). About 30 sources tested live; Reddit blocked, so it was skipped by default (D9). |
| 2 | 01:11 | OK · $1.31 · 17m | Architect → Build | Architecture and ranking design written. **Slice 1:** HTTP, models, dedup ledger, 5 source adapters. 71 tests pass; 33/33 sources live, 1,946 candidates. |
| 3 | 01:29 | **FAIL** · usage limit · $1.22 | (Build) | Hit the 5-hour usage limit 8 minutes in. Consensus rolled back; partial Slice 2 code and a critic **NO-GO** memo on the selection rules stayed on disk. |
| 4 | 02:37 | FAIL (2 of 5) | - | Retry while still limited. The pre-cycle git sync committed cycle 3's partial work, labeled "capture human edits" (a harmless mislabel). |
| 5 | 03:37 | FAIL (3 of 5) | - | Retry while still limited. |
| 6 | 04:37 | OK · $1.21 · 10m | Build | **Recovered after the 4am reset.** Found Slice 2 and the NO-GO on disk and resolved them. **Slice 3:** the critic's 6 fixes. 150 tests pass. QA defect D-1 (an AI-art repo got past the exclusion) blocks shipping. |
| 7 | 04:47 | OK · $1.20 · 11m | Build | **Slice 4:** clone clustering, strong/weak keyword matches. D-1 to D-3 closed, 182 tests pass. A new ranking must-fix blocks edition 1. |
| 8 | 04:58 | OK · $0.97 · 15m | Build → Verify → **Operate** | **Slice 5:** must-fixes done, 196 tests pass, critic GO. **Edition 1 shipped** (5 items). Simulated feedback: 4 thumbs up. |
| 9 | 05:13 | OK · $0.96 · 6m | Operate | **Slice 6:** honest "why" lines, weak items dropped. **Edition 2 shipped** (3 items, needed the 4th fallback step for loosening the selection rules). **First simulated thumbs-down**, on a vendor-marketing item. 212 tests pass. |
| 10 | 05:20 | OK · $0.72 · 4m | Operate → **done** | **Slice 7:** a rule for generic keywords. **Edition 3 shipped** (3 items). The digest item got a thumbs-down. 219 tests pass. `Loop Signal: done`, clean exit. |

## Key events

1. **The agent-path fix worked.** All 7 `loop-plugin:<role>` personas were really called, which the June run never managed.
2. **The fictional reader held.** The profile came only from `reader-source.md`; the post-run leak scan (real name, email, "AgentTeam") is clean.
3. **Running unattended worked.** There were no Open Questions all run; every judgment call was a recorded D9 default (skip Reddit, ship as-is, an empty slot rather than a weak pick).
4. **The usage limit hit at 01:37** and cost 3 cycle attempts plus ~3 hours. loop.py's built-in hourly retry recovered at 04:37 with 2 failures to spare before the circuit breaker (5). No watchdog was needed.
5. **Review gates were strict:** a critic NO-GO, QA D-1, and a ranking must-fix delayed edition 1 to the 5th successful cycle. After that the team shipped exactly one edition per cycle, as designed.
6. **The candidate pool shrank:** editions went from 5 items to 3 as dedup (D7) excluded earlier items. The critic predicted this, and it remains an open risk.
7. **The simulated feedback discriminated:** it went from all thumbs-up in edition 1 to thumbs-down on marketing and news items, which eased the critic's concern that it would just confirm the profile.

## Deliverables

- `projects/personalized-feed/feeds/2026-11-19-01.md` (5 items), `-02.md` (3), `-03.md` (3), each with a `.json` sidecar
- `projects/personalized-feed/src/pfeed/` - stdlib Python pipeline (ingest, rank, render, ledger, feedback)
- `projects/personalized-feed/tests/` - 219 passing (offline fixtures)
- `projects/personalized-feed/docs/` - architecture and ranking design
- `projects/personalized-feed/profile/` - Alex's profile, dedup ledger, onboarding template
- `auto-outputs/personalized-feed/docs/` - per-cycle persona memos (critic, QA gates, eval notes)

## Totals

| Metric | Value |
|---|---|
| Successful cycles | 7 of 10 allowed (1, 2, 6-10) |
| Failed cycles | 3 (usage limit) |
| Cost, successful cycles | $7.03 |
| Cost, interrupted cycle 3 | ~$1.22 |
| Editions | 3 of 3 |
| Tests | 219 passed |
| Tracked project size | 428K (no large state JSON, unlike June's ~6MB) |

## Open items

- **Config for the published example:** decide whether to turn `git_sync` off and set `single_cycle: true`, as cv-designer did (`fc39fea`).
- **Open risks and defects** (from the final consensus): shrinking candidate pool on later days, a short thought-leadership list, newsletter/roundup pages not yet capped, a lone-keyword cap still needed for "mcp".
- **Public-copy step:** on hold.
