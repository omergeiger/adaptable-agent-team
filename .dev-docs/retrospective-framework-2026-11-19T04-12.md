# Retrospective (framework) - from the personalized-feed run - 2026-11-19

## Run summary

| | |
|---|---|
| Instantiation | personalized-feed (7 persona sub-agents, 4 domain skills), unattended, fictional reader |
| Cycles | 10 attempted: 7 OK, 3 failed on the 5-hour usage limit; 0 timeouts, 0 no-ops, 0 validation failures |
| Cost | $7.03 successful + $1.22 cut-off cycle 3 = **$8.25** |
| Outcome | 3 of 3 editions, clean exit on `Loop Signal: done` |

**Verdict:** the agent-path fix (8657d1a) works and the loop is robust (rate-limit recovery, signals, consensus rollback), but domain skills silently never load, and the failure path loses time and mislabels history.

### Timeline

| Cycle | Local start | Outcome | Notes |
|---|---|---|---|
| 1-2 | 01:07 | OK | Profile -> Build |
| 3 | 01:29 | FAIL usage limit | 8 min in, $1.22; "resets 4am" in output |
| 4 | 02:37 | FAIL (2/5) | pre-cycle sync commits cycle 3 leftovers as "capture human edits" |
| 5 | 03:37 | FAIL (3/5) | |
| 6-10 | 04:37 | OK | Build -> Operate -> done |

### What worked
- Plugin agents load from `<plugin>/agents/`: the session init lists all 7 `loop-plugin:*` agents and every cycle called them.
- Rate-limit detection + 1h wait + consensus rollback recovered the run unattended.
- Loop Signal `done` ended the run on the domain condition; `--cycles` stayed a backstop.
- Every cycle produced a valid, changed consensus (0 no-ops, 0 validation failures).

---

## P1 - must fix

**1. Domain skills without YAML frontmatter are never registered, and nothing notices.**
*Evidence:* cycle 8 init event (`logs/cycle-0008-*/transcript.jsonl`, line 1) lists skills `['loop-plugin:example-loop-skill', ...]` only; the 4 domain skills are absent. Their SKILL.md files start with `# <name>` and no `---\nname:\ndescription:\n---` block. 0 Skill-tool calls in all 7 cycles; agents read `test-gate`/`relevance-rubric` by path and never read `feed-item-format`. `example/cv-designer` skills have the same defect (`ats-checklist/SKILL.md`).
**Fix:** (a) `/adapt` must emit frontmatter for every generated skill (and agent); (b) `loop.py` preflight: fail fast if any `loop-plugin/skills/*/SKILL.md` or `agents/*.md` lacks `name`/`description`; (c) after cycle 1, parse the init event and warn if any `squad` agent or skill dir is missing from the registered lists.

## P2 - important

**2. Rate-limit wait ignores the reset time it is told.**
*Evidence:* output says `"You've hit your 5-hour limit · resets 4am (Asia/Jerusalem)"`, `api_error_status: 429`, `api_error: usage_limit_reached`. The loop retried at 02:37 and 03:37 (both wasted) and resumed at 04:37, 37 min after the reset. Each retry counted toward the breaker (3/5): a limit that resets >4h out trips the breaker and ends the run.
**Fix:** parse `resets <time> (<tz>)` when present and sleep until reset + 2 min; do not count usage-limit failures toward `MAX_CONSECUTIVE_ERRORS` (cap total rate-limit wait instead, e.g. 12h).

**3. Leftovers from a failed cycle are committed as human edits.**
*Evidence:* `d32cea5 pre-cycle 4: capture human edits` contains cycle 3's agent code (Slice 2), not human edits. Audit trail and `/retrospect` both mislead.
**Fix:** when `loop_state.json` status is `rate_limited`/failed, label the pre-cycle commit `cycle N (failed): partial agent artifacts`; or commit leftovers in the failure branch of `main()` before waiting.

**4. Failed-cycle metadata is inconsistent.**
*Evidence:* cycles 4-5 `metadata.json` have `"cost_usd": "N/A"` (string) while others are floats; all failed cycles report `"subtype": "success"` although the result has `is_error: true`. Retrospective tooling crashed on the string.
**Fix:** write `cost_usd: 0.0` (or null) and record `is_error`, `api_error_status`, `api_error` from the result object.

**5. Unattended mode is a reusable pattern, hand-written per team.**
*Evidence:* D9 + PROMPT rule (never block, default + record, simulate feedback) gave 0 Open Questions and 0 `block` signals over 7 cycles. It had to be authored by hand for this example.
**Fix:** add `unattended: true` to `config.yaml`; `build_prompt` injects a base "no human present" section (never block, adopt the conservative default, record under Key Decisions). `/adapt` asks about it and about a run-length stop condition (N deliverables -> `done`).

## P3 - nice to have

**6. Headless sessions inherit the user's global plugins and risky tools.**
*Evidence:* cycle init lists `claude-hud` and other user plugins, plus tools `CronCreate`, `RemoteTrigger`, `PushNotification`, `ScheduleWakeup`, `EnterWorktree` - none needed by loop agents. **Fix:** pass `--disallowedTools` for scheduling/remote/notification tools in `run_cycle`; consider isolating plugin loading to the loop plugin.

**7. Timestamps mix UTC and local time.** *Evidence:* cycle log dirs `cycle-0006-20261119-023725` (UTC) vs `loop.log` `04:37:25` (local). **Fix:** one timezone everywhere, with the offset in `loop.log`.

**8. `--cycles` is per-launch.** *Evidence:* `remaining_cycles = args.cycles` (loop.py:392); a relaunch after a crash resets the budget. **Fix:** document it, or add `--cycles-total` that reads successful cycles from `loop_state.json`.

**9. `/retrospect` points at `todos.md`, which no longer exists.** *Evidence:* SKILL.md step 5 "Offer to fold chosen findings into `todos.md`". **Fix:** point to the current planning location (or drop the sentence).

**10. Consensus snapshots have gaps on failed cycles.** *Evidence:* `memory/` has steps 1, 2, 6-10 only. Correct behavior, but surprising. **Fix:** write a one-line `consensus-step-000N.FAILED` marker so the timeline is self-explanatory.
