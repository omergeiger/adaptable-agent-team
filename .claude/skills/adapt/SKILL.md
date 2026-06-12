# /adapt - AgentTeam Setup Wizard

**Run this skill interactively before launching the loop on a new domain.**

This skill is HUMAN-RUN only. It is never invoked by the loop or by agents.

---

## When to Run

Run `/adapt` when:
- You are setting up AgentTeam for a new domain or purpose for the first time
- You want to create a new project workspace with customized agents and prompts
- The loop exits with an "unadapted project" error

---

## What This Skill Does

This wizard interviews you about your domain and generates:
1. A new project folder at `projects/<your-project-name>/` with `docs/`, `logs/`, and `memory/` subfolders
2. Customized worker agent files in `.claude/agents/` - one per worker role (replaces the generic placeholders). The orchestrator persona does NOT get an agent file: the headless cycle session IS the orchestrator, so its persona is written into PROMPT.md.
3. A tailored `PROMPT.md` embedding the orchestrator persona and domain-specific rules
4. Domain skill files at `.claude/skills/<name>/SKILL.md` - one per convention, template, or rubric that must not drift across cycles. Agents load these during loop cycles.
5. A starter `consensus.md` for the new project (ready to run - no sentinel marker)
6. A starter `human_directives.md` pre-filled with the standing directives gathered in the interview
7. `config.yaml` updates: `active_project`, `squad` (the worker role slugs), and `single_cycle` + `loop_interval_seconds` from the cadence answer

Agent files, skill files, and PROMPT.md are repo-global: adapting to a new domain replaces the previous domain's versions. Tell the user this and confirm before overwriting.

---

## Interview Questions

Ask the user these questions (one at a time, conversationally):

1. **Project name** - What should this project be called? (This becomes the folder name under `projects/`.)

2. **Domain and purpose** - What is this agent team trying to accomplish? (e.g., "research competitor products", "write and refine a technical specification", "build and iterate on a software project")

3. **Agent roles** - What specialist roles do you need? List 2-6 roles with a one-sentence description of each. (e.g., Researcher, Writer, Critic, Engineer.) Establish which ONE role is the coordinator/orchestrator - it becomes the PROMPT.md persona; all the others become worker agent files and the config squad.

4. **Phases** - What are the major phases of work? (e.g., Explore → Draft → Review → Ship, or Discover → Design → Build → Launch)

5. **Output format** - What does a cycle's deliverable look like? Where does it live in the project folder? (e.g., markdown docs in `docs/research/`, code files in `docs/code/`)

6. **Cadence** - How often should cycles run (loop_interval_seconds)? Should single_cycle be true (gated, human reviews each cycle) or false (autonomous, runs until stopped)?

7. **Conventions (skills)** - What formats, templates, rubrics, or protocols must stay identical across cycles? (e.g., a digest template, a review-memo format, a fit-scoring rubric, a test-gate procedure.) Each one becomes a skill file under `.claude/skills/` that agents apply during cycles.

8. **Standing directives** - What persistent rules should the team always follow? (e.g., focus area, exclusions, quality thresholds, things that need human sign-off.) These pre-fill `human_directives.md` as D1, D2, ...

---

## Generation Instructions

After gathering answers, generate the following files:

### `projects/<name>/consensus.md`

All 7 required sections, filled with domain-appropriate placeholder text. **Do NOT include the sentinel marker** `<!-- AGENTTEAM_UNADAPTED -->` - this file must be runnable immediately.

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
<first concrete action the team should take, based on the domain>

## Team State
All agents standing by. First cycle not yet run.
<tracking fields for this domain>

## Open Questions
(none)
```

In `## Team State`, define the tracking fields this domain needs as labeled starter lines (e.g. a pipeline count per stage, a ledger of items already processed, doc maturity per discipline) so every later cycle updates a stable structure instead of inventing one.

### `projects/<name>/human_directives.md`

Pre-fill `## Standing Directives` with the rules gathered in question 8, numbered D1, D2, ... If an answer references something the user must still fill in, keep an explicit `<placeholder>` in the directive text.

```markdown
## Standing Directives

D1. <first standing rule from the interview>
D2. <second standing rule from the interview>

## Cycle Overrides

<!-- Add one-off instructions here. They supersede consensus Next Action. Remove when satisfied. -->

## Answers

<!-- Responses to Open Questions from consensus.md. -->
```

### `.claude/agents/<role>.md` for each WORKER role

Generate one file per worker role from question 3. Do NOT generate an agent file for the orchestrator/coordinator role - that persona goes into PROMPT.md (the headless cycle session is the orchestrator and never delegates to itself).

Use this frontmatter and structure:
```
---
name: <role-slug>
description: <one-line role description>
model: inherit
---

You are the <role> for this agent team. <2-3 sentences describing responsibilities and style.>

## Your Responsibilities

<bullet list of what this agent does each cycle>

## Rules

- Write only inside `projects/<active_project>/`.
- Do not update consensus.md - that is the orchestrator's responsibility.
- Do not run git push.
- Report blockers clearly so the orchestrator can surface them.

## Output Format

<how this agent should structure its output report>
```

### `.claude/skills/<name>/SKILL.md` for each convention from question 7

One skill per convention, kebab-case name. These are loaded by agents during loop cycles (unlike /adapt itself, which is human-run). Structure:

```markdown
# <name> - <Short Title>

<one line: what this convention protects and why it must not drift>

## Template / Rubric / Protocol

<the exact, complete content: the template to fill, the rubric with its scale, or the step-by-step protocol>

## When to Apply

<which roles use this, at which point in the cycle, and what counts as compliant>
```

### `PROMPT.md`

Replace the `<!-- DOMAIN-SPECIFIC -->` placeholders with:
- The orchestrator persona from question 3 (role name, responsibilities, decision style) - this is where the coordinator role lives
- The delegation strategy across the worker roles (ordering rules, when to involve which worker, max workers per cycle if relevant)
- Domain output rules: where deliverables go under `projects/<name>/docs/`, naming patterns, quality bar
- An explicit instruction to apply each generated skill by name (e.g. "format every digest per the digest-format skill")
- Phase semantics from question 4: what `## Current Phase` values exist and what permits advancing

### `config.yaml`

Update:
- `active_project`: the new project name
- `squad`: the worker role slugs from question 3 (NEVER include the orchestrator - the session itself is the orchestrator)
- `single_cycle` and `loop_interval_seconds`: from the cadence answer (question 6)

Leave `cycle_timeout_seconds`, `verbosity`, and `max_cycle_logs` unchanged unless the user expressed a preference; mention they can tune these by hand.

---

## Final Step

Tell the user:
- Their project is ready at `projects/<name>/`
- They can review and edit any generated file before running the loop - especially the standing directives, the generated skills, and the squad list in config.yaml
- Run `.venv/bin/python loop.py` to start the first cycle (single_cycle: true is recommended for the first run)
- Edit `human_directives.md` between cycles to steer the team

For worked end-to-end examples of completed interviews and the files they should produce, see `example_cases.md` at the repo root.
