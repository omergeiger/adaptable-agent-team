---
name: retrospect
description: Human-run retrospective for a team instantiation run. Iterates the run's artifacts and deliverables and produces two prioritized, actionable improvement docs - one at the team (instantiation) level, one at the framework level - written uncommitted to .dev-docs/. Human-invoked only; loop agents must never invoke it.
---

# /retrospect - AgentTeam Run Retrospective

**Run this skill interactively after (or during) a team instantiation's loop run.** It is HUMAN-RUN only - never invoked by the loop or by agents. It lives in `.claude/skills/`, the human-run home alongside `/adapt`; PROMPT.md forbids loop agents from invoking anything here.

It reads everything a run produced - steering, per-cycle by-products, logs, deliverables, and the instantiation's generated config (agents, skills, tailored prompt) - and writes **two separate, prioritized improvement docs** to `.dev-docs/`:

- **Team-level** - improvements to THIS instantiation: its sub-agents, domain skills, PROMPT domain rules, steering/directives, deliverable quality, and delegation flow.
- **Framework-level** - improvements to the generic, reusable framework that would help ANY instantiation: `loop.py`, the consensus protocol, `src/`, the base PROMPT structure, `/adapt`, guardrails, validation, cost/loop control.

The two output files are **NOT added to source control** - the human decides whether to keep them.

---

## When to Run

- After a loop run completes (or stalls), to convert the run into actionable improvements.
- Mid-run, to course-correct an instantiation that is misbehaving.

## Inputs

- **Target project:** default to `active_project` in `config.yaml`. Accept an optional argument naming a different project under `steering/` / `auto-outputs/` / `projects/`.
- If the named project has no artifacts (no `auto-outputs/<project>/` and no `steering/<project>/`), stop and tell the human - there is nothing to retrospect.

---

## Procedure

### 1. Resolve and inventory

- Determine `<project>` (argument, else `config.yaml > active_project`).
- Inventory the run's artifacts:
  - `steering/<project>/consensus.md`, `human_directives.md`
  - `auto-outputs/<project>/memory/consensus-step-*.md` - per-cycle consensus snapshots (the run's spine)
  - `auto-outputs/<project>/logs/` - `loop_state.json`, per-cycle `metadata.json` (cost, duration, `validation_outcome`, `timed_out`), `loop.log`
  - `auto-outputs/<project>/docs/` - per-cycle persona by-product docs
  - `projects/<project>/` - the actual deliverables
  - The instantiation's generated config: `src/resources/loop-plugin/agents/*.md`, `src/resources/loop-plugin/skills/*/SKILL.md`, the domain sections of `src/resources/PROMPT.md`, `config.yaml > squad`.

### 2. Reconstruct the run

- From `metadata.json` across cycles, compute: total cycles, total cost, cost per cycle, duration, count of failed / timed-out / no-op cycles, and where cost concentrated.
- From the consensus snapshots, build a phase timeline: which cycles sat in which phase, where it stalled, where it looped.
- Identify waste explicitly: no-op cycles, a `## Next Action` that repeats, re-processing of already-handled instructions, failed-then-rolled-back cycles, cycles spent blocked on absent human input.

### 3. Analyze each layer

For each, ask "what worked, what hurt, and what is the concrete fix":

- **Deliverable quality** - do the products in `projects/<project>/` meet the domain bar? Gaps, fabrication risks, format/ATS issues, missed requirements.
- **Agents** - did each sub-agent earn its place? Overlap, never-invoked agents, weak/ambiguous instructions, missing guardrails.
- **Domain skills** - were the rubrics / templates / checklists actually applied, and did they change outcomes?
- **PROMPT domain rules** - delegation order, phase-advance semantics, escalation rules - did they match what the run actually needed?
- **Steering / directives** - were standing directives clear and enforced? Did the human have to intervene repeatedly for the same thing?
- **Framework mechanics** - loop control, consensus validation, signals/blocking, cost efficiency, git sync.

### 4. Categorize and prioritize every finding

- **Level test:** "Would this fix help a *different* domain too?" -> **framework**. "Only relevant to this instantiation's domain?" -> **team**. When unsure, default to **team** and note the framework angle.
- **Priority**: **P1** must fix (broke the run or the deliverable), **P2** important (meaningful waste or quality loss), **P3** nice to have (polish).
- Every finding must be **actionable and grounded**: cite the specific artifact - cycle number, file path, cost figure. No vague advice. Pair each with a concrete fix.

### 5. Write two files (do NOT commit)

Use a file-safe UTC timestamp `YYYY-MM-DDTHH-MM` (colons -> hyphens), matching existing retrospectives.

- `.dev-docs/retrospective-team-<project>-<timestamp>.md`
- `.dev-docs/retrospective-framework-<timestamp>.md`

Each file contains:
- A header **run summary**: cycles, total cost, deliverable outcome, and a one-line verdict.
- (Framework file) a short timeline table for context.
- **Findings grouped by priority**, each as: **title** -> *evidence* (artifact + figures) -> **fix** (concrete change). Keep them scannable.

Do **not** `git add` or `git commit` either file. Do **not** modify `.gitignore`. After writing, tell the human the two paths and that they are untracked in `.dev-docs/` until the human decides to keep them. Offer to fold chosen findings into `todos.md` (team) or a framework-branch plan (framework) if the human wants.

### 6. Report

Summarize the top ~3 findings across both levels in chat, then point to the two files.

---

## Guardrails

- **HUMAN-RUN only.** Never invoked by the loop or by agents.
- **Read-only on everything except the two output files.** This skill analyzes; it does not modify agents, skills, `PROMPT.md`, `loop.py`, `config.yaml`, or steering. Its only writes are the two `.dev-docs/` retrospective files.
- **Never auto-commit.** The human owns whether retrospective output enters source control; do not touch `.gitignore`.
