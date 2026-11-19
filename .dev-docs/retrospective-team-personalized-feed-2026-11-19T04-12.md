# Retrospective (team) - personalized-feed - 2026-11-19

## Run summary

| | |
|---|---|
| Cycles | 10 attempted: 7 OK (1, 2, 6-10), 3 failed on the usage limit (3, 4, 5); 0 timeouts, 0 no-ops |
| Cost | $7.03 successful + $1.22 for cycle 3 (cut off mid-run; its work survived on disk) = **$8.25** |
| Wall clock | 01:07-05:24, ~3h of it rate-limit waits |
| Deliverable | 3 of 3 editions (`feeds/2026-11-19-01..03.md`, 5/3/3 items), stdlib pipeline `src/pfeed/`, 219 tests green |
| Exit | `Loop Signal: done` after edition 3 (D10); the `--cycles 10` backstop was not needed |

**Verdict:** the team works end to end unattended and ships honest, link-valid editions, but the ranking barely discriminates (scores saturated at 5) and the feedback loop tunes the wrong knob.

### Phase timeline (from consensus snapshots)

| Cycle | Phase after | Editions | Agents |
|---|---|---|---|
| 1 | Architect | 0 | user-profiler, source-scout, critic |
| 2 | Build | 0 | tech-lead, developer, qa-engineer |
| 6 | Build | 0 | developer, qa-engineer, ranking-engineer |
| 7 | Build | 0 | developer, qa-engineer, ranking-engineer |
| 8 | Operate | 1 | critic, developer, qa-engineer |
| 9 | Operate | 2 | critic, developer, qa-engineer |
| 10 | Operate (done) | 3 | critic, developer, qa-engineer |

### What worked
- Fictional-reader isolation (D8): profile built only from `reader-source.md`; post-run leak scan clean.
- Unattended mode (D9): zero Open Questions all run; every judgment call recorded as a default (skip Reddit, ship as-is, empty slot over weak pick).
- Recovery: cycle 6 found cycle 3's orphaned Slice 2 + critic NO-GO on disk and resolved them without redoing work.
- Edition discipline after Operate: exactly one edition per cycle, then `done`, as designed.
- Simulated feedback discriminated: all thumbs-up in edition 1, thumbs-down on vendor-marketing (ed. 2 #1) and news-only (ed. 3 #3) items.

---

## P1 - must fix

None. Nothing broke the run or produced an invalid deliverable.

## P2 - important

**1. Ranking scores are saturated, so ranking hardly ranks.**
*Evidence:* across 11 shipped items, `interest-match 5` on 8, `novelty 5` on 10, `thought-leadership 1` on 9 (`feeds/*.md` relevance lines). Ed. 3 #1 (`morajabi/poo`) gets interest-match 5 on one incidental "mcp" hit (critic memo, cycle 10).
**Fix:** in `loop-plugin:relevance-rubric`, define each 0-5 signal with anchored examples and a required distribution (e.g. at most 1 item per edition at 5 on interest-match unless title-level strong match). Add a qa-engineer check that fails an edition where any signal has zero variance.

**2. Feedback re-weights global signals, not Alex's interests.**
*Evidence:* `profile/alex-weights.json` logs simulated thumbs as changes to the 5 signal weights; interest-match fell 0.35 -> 0.28 after thumbs-ups on high-interest items (saturation makes "liked" items look like they were liked for other signals). `profile/alex.md` "Engagement history" still reads "empty - no editions shipped yet". `loop-plugin:profile-schema` says feedback should adjust interests.
**Fix:** route D6 through per-interest weights (profile-schema) with the signal weights fixed; have user-profiler own the feedback step in Operate and write the engagement history into `alex.md`.

**3. Back-to-back editions exhaust the day's candidate pool.**
*Evidence:* 3 editions shipped within about 25 minutes (cycles 8-10, 04:58-05:24) on the same live data; items fell 5 -> 3 -> 3 and edition 2 needed relaxation rung 4 (consensus, cycle 9) because D7 dedup removes the previous editions' winners from the same pool.
**Fix:** in D10 / PROMPT Operate rules, either space editions (Operate cycles wait for fresh data, e.g. `loop_interval_seconds` of hours in Operate) or define an edition's candidate window as "new since the previous edition" and accept a shorter, honest edition. Document the trade-off in the example README.

**4. Review gates kept finding new must-fixes, delaying edition 1 to the 5th successful cycle.**
*Evidence:* critic NO-GO (cycle 3) -> Slice 3; QA D-1 blocks (cycle 6) -> Slice 4; ranking must-fix (cycle 7) -> Slice 5; edition 1 only in cycle 8. With `--cycles 10`, 3 editions fit with 2 spare.
**Fix:** PROMPT Verify rule: a candidate ships once the previous review's must-fixes are closed and links/dedup/diversity pass; new findings go to the next Operate cycle's slice, not back to Build.

**5. Agent utilization is lopsided; the specified Operate chain never ran.**
*Evidence:* user-profiler and source-scout ran only in cycle 1, tech-lead only in cycle 2. PROMPT's Daily feed chain (source-scout -> developer -> ranking-engineer -> critic -> qa) conflicts with the 3-agents-per-cycle cap; Operate cycles ran critic + developer + qa only. Critic was skipped in cycles 2, 6, 7 for the cap.
**Fix:** rewrite the Operate chain to what fits the cap (developer runs pipeline -> critic -> qa) and give user-profiler the feedback step (P2-2), or raise the cap to 4 in Operate. Consider folding source-scout into developer after Architect.

## P3 - nice to have

**6. Why-lines are templated.** *Evidence:* 7 of 11 end "clone it and run the quickstart", 3 "follow the write-up and try the steps", including for a manifesto (ed. 3 #3). **Fix:** feed-item-format requires a why-line that names one concrete thing in the item (a feature, a result, a command); qa checks no two why-lines share a tail.

**7. D2 says Medium; no Medium item shipped.** *Evidence:* source mix GitHub 5, blog 2, HN 2, arXiv 1, Substack 1; the catalog lists Medium 6 times. **Fix:** either relax D2 to "long-form blogs (Medium/Substack/personal)" or have qa flag a missing directive-named source type per edition.

**8. Editions are indistinguishable by title.** *Evidence:* all three files open with `# Personalized Feed - 2026-11-19`. **Fix:** feed-item-format header includes `Edition NN`.

**9. Thought-leadership list is too short.** *Evidence:* `thought-leadership 1` on 9 of 11 items; critic flagged "only six names" (cycles 9-10). **Fix:** source-scout expands the list in Architect with reasons per name; or drop the signal until it has coverage.

**10. Domain skills were read as files, not invoked.** *Evidence:* see the framework retrospective P1-1; agents read `test-gate` and `relevance-rubric` by path, `feed-item-format` never. **Fix (team side):** add YAML frontmatter (`name`, `description`) to the 4 SKILL.md files.
