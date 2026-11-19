---
name: adapt
description: Human-run setup wizard for adapting the framework to a new domain. Only the human user invokes this interactively before launching the loop; loop agents must never invoke it.
---

# /adapt - AgentTeam Setup Wizard

**Run this skill interactively before launching the loop on a new domain.** It is HUMAN-RUN only - never invoked by the loop or by agents.

`/adapt` does not march through a fixed question list. It works as a loop:

1. **Extract** everything it can from the human's opening request.
2. **Triage** every field it needs into *provided* / *missing* / *ambiguous*, and show that read back.
3. **Propose** a concrete preview of all files it will generate (written to a temp file) and flag any concerns.
4. **Iterate** on the human's fixes until the proposal is approved, then generate the real artifacts and delete the temp file.

---

## Orchestration model (read first - do not violate)

- The **main headless cycle session** (the `claude -p` invocation the loop makes) is the orchestrator. Its coordinator persona is generic and already lives in `src/resources/PROMPT.md`.
- **The orchestrator is never a domain role.** Every specialist role the human names becomes a **sub-agent**: one `src/resources/loop-plugin/agents/<role>.md` file plus an entry in the full `config.yaml > squad`.
- Therefore: do NOT ask "which role coordinates", do NOT write an orchestrator agent file, and do NOT embed any domain role's persona into `PROMPT.md`. The orchestrator's *domain-specific decision logic* (priorities, when to advance a phase, what "done" means, delegation order) goes into `PROMPT.md`'s domain sections - as rules the generic session follows, not as a role.

---

## When to Run

- Setting up AgentTeam for a new domain for the first time.
- Creating a new project workspace with customized sub-agents and prompt.
- The loop exited with an "unadapted project" error.

If invoked with no accompanying request ("bare `/adapt`"), open with one line - *"What are you building, and what should the team do each cycle?"* - then run the loop above.

---

## Information the setup needs

Everything below exists only to fill the generated artifacts (see Generation). Triage each into one of three buckets and handle accordingly:

**Must-ask - cannot be guessed:**
- **Domain & purpose** - what the team is chartered to accomplish.
- **Roles** - the 2-20 specialist sub-agents, each with a one-line responsibility. (All become sub-agents.)
- **Hard constraints / standing directives** - non-negotiables: exclusions, quality bars, anything needing human sign-off.

**Propose-and-confirm - infer from the request + the worked cases in `.dev-docs/example_cases.md`, then let the human correct:**
- **Project name** (kebab-case slug, usually derivable from the domain).
- **Phases** (e.g. Explore → Draft → Review → Ship).
- **Deliverable format & location** under `projects/<name>/`.
- **Conventions → skills** - which formats/rubrics/protocols must not drift across cycles.
- **Delegation strategy** - ordering rules, max sub-agents per cycle.

**Default silently - state the assumption, do not ask:**
- **Cadence**: `single_cycle: true`, `loop_interval_seconds: 30` (gated first run).
- `cycle_timeout_seconds`, `verbosity`, `max_cycle_logs`: leave template defaults.

Spend the question budget only on must-ask fields and genuinely blocking ambiguities. Make the orchestrator/role split and everything in "propose-and-confirm" a *proposal you confirm*, not a question you ask.

---

## Question protocol

- Ask in rounds; **at most 3 questions per round, 30 lines max per round**. Multiple rounds are fine.
- **Every question must offer 2-3 diverse candidate answers** - meaningfully different options (not minor variants) - so the human can pick one, combine, or redirect. In an interactive session prefer the `AskUserQuestion` tool for this; otherwise list the options inline.
- Batch related questions into one round rather than trickling them out.
- Prefer "here is my proposal - ok?" framing over open-ended asks; it converges faster and respects the budget.

---

## Proposal preview (the temp file)

Before writing any real artifact, write the full proposal to **`ADAPT_PROPOSAL.tmp.md`** at the repo root. Open it with this banner verbatim:

```
> ⚠️ TEMPORARY - /adapt proposal for review only. Not authoritative; not committed.
> This file is deleted automatically once you approve. Edit it or reply with fixes, then tell /adapt to proceed.
```

Below the banner, lay out exactly what will be generated, one section per artifact:
- **Project**: name (slug), domain & purpose.
- **Sub-agents**: each role + one-line responsibility (all are sub-agents / squad members).
- **Phases** and the delegation strategy the session will follow.
- **Deliverables**: format + location under `projects/<name>/`.
- **Skills**: each convention that becomes a `loop-plugin:<name>` skill.
- **Standing directives**: D1, D2, ... as they will appear in `human_directives.md`.
- **config.yaml**: the exact values to be set.
- **Concerns / risks**: anything underspecified, contradictory, or likely to need a second pass.

Then ask the human to approve or send fixes. On fixes, update the temp file and re-present. **Do not generate real artifacts until the human approves.**

---

## Generation (after approval)

### `steering/<name>/consensus.md`

All 7 sections, domain-appropriate placeholder text. **No sentinel marker** - this file must be runnable immediately.

```markdown
## Last Updated
<current ISO timestamp>

## Current Phase
<first phase name>

## What We Did This Cycle
- (Initial setup - first cycle not yet run)

## Key Decisions
- Project initialized via /adapt for domain: <domain>

## Next Action
<first concrete action, based on the domain>

## Team State
All agents standing by. First cycle not yet run.
<labeled starter tracking fields this domain needs - e.g. per-stage pipeline counts, a ledger of processed items, doc maturity per discipline - so every later cycle updates a stable structure>

## Open Questions
(none)
```

### `steering/<name>/human_directives.md`

Pre-fill `## Standing Directives` from the must-ask constraints, numbered D1, D2, ... Keep explicit `<placeholder>` text for anything the human still needs to fill.

```markdown
## Standing Directives

D1. <first standing rule>
D2. <second standing rule>

## Cycle Overrides

<!-- One-off instructions; supersede consensus Next Action. Remove when satisfied. -->

## Answers

<!-- Responses to Open Questions from consensus.md. -->
```

### `src/resources/loop-plugin/agents/<role>.md` - one per role (ALL roles)

Every domain role becomes a sub-agent file. Never create an orchestrator agent file.

```
---
name: <role-slug>
description: <one-line role description>
model: inherit
---

You are the <role> for this agent team. <2-3 sentences on responsibilities and style.>

## Your Responsibilities

<what this sub-agent does when delegated to>

## Rules

- Write only inside `projects/<active_project>/`.
- Do not update consensus.md - the orchestrator session owns it.
- Do not run git push.
- Report blockers clearly so the orchestrator can surface them.

## Output Format

<how this sub-agent structures its report back to the orchestrator>
```

**Cleanup (required):** after writing the new files, delete every other `src/resources/loop-plugin/agents/*.md` whose `name` is not in the new squad (leftovers from a previous domain). List the deletions in the overwrite confirmation.

### `src/resources/PROMPT.md`

Replace the `<!-- DOMAIN-SPECIFIC -->` placeholders. Do **not** add a domain role persona - the orchestrator stays generic. Fill in:
- **Delegation strategy** across the sub-agents (ordering, when to involve which, max per cycle).
- **Domain output rules**: deliverables → `projects/<name>/` (domain-native filenames, no framework stamps); by-product docs → `auto-outputs/<name>/docs/` named `cycle-NNNN-<timestamp>-<persona>-<slug>.md`; quality bar; when to escalate to Open Questions.
- **An explicit instruction to apply each generated skill by its namespaced name** (e.g. "format every digest per the `loop-plugin:digest-format` skill").
- **Phase semantics**: which `## Current Phase` values exist and what permits advancing.

### `src/resources/loop-plugin/skills/<name>/SKILL.md` - one per convention

These load only into headless loop sessions via the `loop-plugin` plugin; agents apply them as `loop-plugin:<name>`. Never put domain skills in `.claude/skills/`. Leave the framework-provided `example-loop-skill` in place; delete only domain skills from a previous domain.

The leading frontmatter block is **required**: Claude Code registers a plugin skill only when `SKILL.md` starts with `name` and `description`; without it the skill is silently skipped and agents never get it. `name` must equal the directory name. Write `description` as when to apply the skill and by whom (e.g. "Feed item template. Apply when the developer renders an edition and when QA checks one."), since that is what the session uses to pick it up.

```markdown
---
name: <name>
description: <what this convention covers; which sub-agents apply it, and when>
---

# <name> - <Short Title>

<one line: what this convention protects and why it must not drift>

## Template / Rubric / Protocol

<the exact, complete content: the template to fill, the rubric with its scale, or the step-by-step protocol>

## When to Apply

<which sub-agents use this, at which point in the cycle, and what counts as compliant>
```

### `config.yaml`

- `active_project`: the new project slug.
- `squad`: **all** the role slugs (every role is a sub-agent).
- `single_cycle` and `loop_interval_seconds`: from the cadence (default `true` / `30`).
- Leave `cycle_timeout_seconds`, `verbosity`, `max_cycle_logs` unless the human asked otherwise; mention they can hand-tune them.

Agent files, skill files, and `PROMPT.md` are **repo-global** - adapting a new domain replaces the previous one's versions. Confirm before overwriting.

---

## Final step

1. **Delete `ADAPT_PROPOSAL.tmp.md`** - the proposal is now realized in the actual files.
2. **Check frontmatter:** every `src/resources/loop-plugin/agents/*.md` and `src/resources/loop-plugin/skills/*/SKILL.md` must start with a `---` block whose `name` matches the file stem / directory name and whose `description` is non-empty. Run `.venv/bin/python -c "from pathlib import Path; from src.plugin_check import check_plugin; print(check_plugin(Path('src/resources/loop-plugin')) or 'ok')"` and fix anything it reports - `loop.py` refuses to start otherwise.
3. Tell the human:
   - Steering files are at `steering/<name>/` (`consensus.md` + `human_directives.md`); deliverables accumulate in `projects/<name>/` and the process trail in `auto-outputs/<name>/` (both created by the loop on first run).
   - They can review/edit any generated file before running - especially the standing directives, the generated skills, and the squad in `config.yaml`.
   - Run `.venv/bin/python loop.py` to start the first cycle (`single_cycle: true` recommended for the first run).
   - Edit `human_directives.md` between cycles to steer the team.

For worked end-to-end examples of completed setups, see `.dev-docs/example_cases.md`.
