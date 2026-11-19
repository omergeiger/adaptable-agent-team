# Try It: A Daily AI Tooling Digest

A hands-on walkthrough of the framework on its smallest useful team: two agents who publish a daily markdown digest of the 5 most significant developments in AI tooling. It is Case 1 from [`.dev-docs/example_cases.md`](.dev-docs/example_cases.md), set up end to end.

You will:
1. run `/adapt` and watch it turn the bare template into a team,
2. check what it generated,
3. run the loop for one or three cycles and check the digests it produces.

Steps 1-2 take a few minutes. Running cycles uses Claude usage: each cycle does web searches and calls two sub-agents, and takes a few minutes.

---

## 1. Set up a clone

Work in a separate clone on its own branch, so your main checkout stays a clean template:

```bash
git clone https://github.com/omergeiger/adaptable-agent-team.git adaptable-agent-team-digest
cd adaptable-agent-team-digest
git checkout -b try-digest
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests     # expect all tests to pass
```

Then start Claude Code at the repo root:

```bash
claude
```

Type `/` and check that `adapt` and `retrospect` appear in the skill list.

## 2. Run /adapt

Type this into the session:

```
/adapt Build a daily tech news digest team called ai-tooling-digest, with two roles: an editor (lead) who picks the theme, ranks candidates by significance over popularity and writes the digest, and a researcher who finds 10-15 candidate items from the last 24 hours with source links. Each cycle produces one markdown digest of the 5 most significant developments in AI tooling, each with a 2-sentence "why it matters" and a primary-source link. Phases: Collect, Rank, Publish. Never repeat an item covered in the last 7 digests. Skip funding-round news unless it's over $100M.
```

What you should see:

- **A read-back** of what `/adapt` took from your request. This request covers everything essential, so it may ask no questions at all; if it does, it asks at most 3 per round, each with 2-3 options.
- **A proposal** in `ADAPT_PROPOSAL.tmp.md` at the repo root: project name, sub-agents, phases, deliverables, skills, standing directives, `config.yaml` values, and any concerns. It may add a directive or two you didn't ask for (for example, "publish fewer than 5 rather than padding"). Read it, ask for changes if you want any, then reply `proceed`.
- **Generation**: the real files are written and the proposal file is deleted.

Both roles become sub-agents, including the editor marked "lead". The cycle session itself is the generic orchestrator; the editor's coordination rules (ranking, gating, what counts as done) go into `src/resources/PROMPT.md` as rules it follows.

## 3. Check what it generated

Paste this into the same session:

```
/adapt is done. Verify what it generated - check and report only, don't fix anything.

1. Run: git status --short && git diff --stat
2. Run: .venv/bin/python -c "from pathlib import Path; from src.plugin_check import check_plugin; print(check_plugin(Path('src/resources/loop-plugin')) or 'ok')"
3. Check each item and mark it pass/fail with a one-line reason:
   a. src/resources/loop-plugin/agents/ has one file per role (editor, researcher), each with name/description frontmatter, and NO orchestrator agent file.
   b. At least one convention skill (e.g. a digest format) exists at src/resources/loop-plugin/skills/<name>/SKILL.md with frontmatter whose name matches the directory; example-loop-skill is still there.
   c. src/resources/PROMPT.md has no remaining DOMAIN-SPECIFIC placeholders; the ranking rule, the 7-digest no-repeat rule and the exactly-5-items rule are written as orchestrator rules (directly, or by telling agents to apply a skill that holds them, by its loop-plugin:<name> name); the orchestrator has no domain persona.
   d. steering/ai-tooling-digest/consensus.md has all 7 required sections (Last Updated, Current Phase, What We Did This Cycle, Key Decisions, Next Action, Team State, Open Questions).
   e. steering/ai-tooling-digest/human_directives.md has numbered Standing Directives (D1, D2, ...) covering the AI tooling focus and the funding rule, plus Cycle Overrides and Answers sections.
   f. config.yaml: active_project is ai-tooling-digest and squad lists exactly the two role slugs; other values unchanged.
   g. ADAPT_PROPOSAL.tmp.md no longer exists.
4. Quote the standing directives verbatim, and paste the full config.yaml diff.

End with a summary table (item, pass/fail, note).
```

## 4. Run the loop

### One cycle (gated)

The generated `config.yaml` has `single_cycle: true`, so one run of the loop is one cycle. Paste this:

```
Run one gated cycle: .venv/bin/python loop.py
A cycle can take several minutes (the cycle timeout is 30 min), so run it in the background or with a timeout of at least 30 minutes - don't let your shell command time out first.

When it finishes, report:
1. Exit code, and the cycle's line from auto-outputs/ai-tooling-digest/logs/loop.log (OK or FAIL and the reason).
2. From the cycle folder under auto-outputs/ai-tooling-digest/logs/: metadata.json (validation_outcome, cost_usd, duration_seconds, timed_out).
3. Whether steering/ai-tooling-digest/consensus.md changed, still has all 7 sections, and whether Last Updated matches the cycle time from prompt.md. Quote its Current Phase, What We Did This Cycle, Next Action and Team State.
4. The digest under projects/ai-tooling-digest/digests/: paste it in full, and check it against the digest format skill (exactly 5 items or a note saying why fewer, 2 sentences each, primary-source links).
5. List the files in auto-outputs/ai-tooling-digest/docs/ - is there one per sub-agent turn?
6. Whether a ledger of covered items exists and lists the published items.

If it fails, show the last 30 lines of loop.log and the cycle's output.json. Report only - don't fix anything.
```

Prefer to watch it live? Run `.venv/bin/python loop.py` in a terminal at the repo root instead (the log prints as the cycle runs), then paste the prompt above without its first two lines so the session only checks the results.

### Three cycles (continuous)

`single_cycle: true` exits after one cycle regardless of `--cycles`, so this switches to continuous mode and caps the run at three. Three digests on the same day are a good test of the no-repeat rule. Paste this:

```
Run three cycles of the loop.

1. In config.yaml, set single_cycle: false (leave everything else as is).
2. Run: .venv/bin/python loop.py --cycles 3
   Each cycle can take several minutes (30 min timeout each, 30s sleep between), so run it in the background and wait for it to finish - don't let a shell timeout cut it off.

When it finishes, report:
1. Exit code, and each cycle's OK/FAIL line from auto-outputs/ai-tooling-digest/logs/loop.log.
2. A table, one row per cycle, from each cycle folder's metadata.json: validation_outcome, cost_usd, duration_seconds, timed_out. Add a total cost row.
3. steering/ai-tooling-digest/consensus.md after the last cycle: all 7 sections present? Quote Current Phase, Next Action and Team State.
4. The digests under projects/ai-tooling-digest/digests/: list them, paste the last one in full, and check each against the digest format skill (exactly 5 items or a note saying why fewer, 2 sentences each, primary-source links).
5. No-repeat rule: does any item (same URL or same announcement) appear in more than one digest? Does the covered-items ledger list every published item exactly once?
6. List the files in auto-outputs/ai-tooling-digest/docs/ - one per sub-agent turn, per cycle?

If any cycle fails, show the last 30 lines of loop.log and that cycle's output.json. Report only - don't fix anything.
```

While it runs, watch `loop.log` for:
- **`FAIL`**: the loop restores the consensus from before that cycle and continues; five failures in a row stop it.
- **A rate-limit message**: in continuous mode the loop waits an hour before retrying. Ctrl-C stops it cleanly after the cycle in progress.
- **`Loop Signal 'block'`**: the team decided it can't continue (for example, web search returned nothing).

## 5. Steer it and review it

- **Steer between cycles** by editing `steering/ai-tooling-digest/human_directives.md`: add a one-off instruction under `## Cycle Overrides` (numbered O1, O2, ...), or a new standing rule (the next D number). The next cycle acknowledges the IDs it acted on in consensus `## What We Did This Cycle`.
- **Review the run** with `/retrospect` in an interactive session. It reads the steering files, logs, by-products and digests, and writes team-level and framework-level improvement notes to `.dev-docs/` without committing them.

## 6. Clean up

The clone is a throwaway. Delete it when you're done:

```bash
cd .. && rm -rf adaptable-agent-team-digest
```
