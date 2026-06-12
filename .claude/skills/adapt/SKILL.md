# /adapt — AgentTeam Setup Wizard

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
1. A new project folder at `projects/<your-project-name>/`
2. Customized agent files in `.claude/agents/` (replaces the generic orchestrator/worker placeholders)
3. A tailored `PROMPT.md` with domain-specific rules
4. A starter `consensus.md` for the new project (ready to run — no sentinel marker)
5. A starter `human_directives.md` with empty sections

After generating, it updates `config.yaml` to point `active_project` at the new project.

---

## Interview Questions

Ask the user these questions (one at a time, conversationally):

1. **Project name** - What should this project be called? (This becomes the folder name under `projects/`.)

2. **Domain and purpose** - What is this agent team trying to accomplish? (e.g., "research competitor products", "write and refine a technical specification", "build and iterate on a software project")

3. **Agent roles** - What specialist roles do you need? List 2-6 roles with a one-sentence description of each. (e.g., Researcher, Writer, Critic, Engineer)

4. **Phases** - What are the major phases of work? (e.g., Explore → Draft → Review → Ship, or Discover → Design → Build → Launch)

5. **Output format** - What does a cycle's deliverable look like? Where does it live in the project folder? (e.g., markdown docs in `docs/research/`, code files in `docs/code/`)

6. **Cadence** - How long should each cycle run? Should single_cycle be true (gated, human reviews each cycle) or false (autonomous, runs until stopped)?

---

## Generation Instructions

After gathering answers, generate the following files:

### `projects/<name>/consensus.md`

All 7 required sections, filled with domain-appropriate placeholder text. **Do NOT include the sentinel marker** `<!-- AGENTTEAM_UNADAPTED -->` — this file must be runnable immediately.

```markdown
## Last Updated
<current ISO timestamp>

## Current Phase
<first phase name>

## What We Did This Cycle
- (Initial setup — first cycle not yet run)

## Key Decisions
- Project initialized via /adapt for domain: <domain>

## Next Action
<first concrete action the team should take, based on the domain>

## Team State
All agents standing by. First cycle not yet run.

## Open Questions
(none)
```

### `projects/<name>/human_directives.md`

```markdown
## Standing Directives

<!-- Add numbered directives here: D1. ..., D2. ..., etc. -->

## Cycle Overrides

<!-- Add one-off instructions here. Remove when satisfied. -->

## Answers

<!-- Responses to Open Questions from consensus.md. -->
```

### `.claude/agents/<role>.md` for each role

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
- Do not update consensus.md — that is the orchestrator's responsibility.
- Do not run git push.
- Report blockers clearly so the orchestrator can surface them.

## Output Format

<how this agent should structure its output report>
```

### `PROMPT.md`

Replace the `<!-- DOMAIN-SPECIFIC -->` placeholders with domain-appropriate rules, output conventions, naming patterns, and quality bar.

### `config.yaml`

Update `active_project` to the new project name, and set `single_cycle` based on the user's cadence preference.

---

## Final Step

Tell the user:
- Their project is ready at `projects/<name>/`
- They can review and edit any generated file before running the loop
- Run `python loop.py` to start the first cycle
- Edit `human_directives.md` between cycles to steer the team
