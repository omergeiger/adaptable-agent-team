# AgentTeam - Claude Code Directives

## Project Overview

AgentTeam is a generic multi-agent loop framework for Claude Code. It extracts the core patterns from the Auto-Company repo (https://github.com/omergeiger/Auto-Company) into a reusable template that can be adapted to any domain or purpose.

## Scope

- **LLM provider**: Claude only (Claude Code CLI, `--permission-mode bypassPermissions`).
- **OS**: macOS only.

## Communication Convention

Two working files under `.dev-docs/`, kept distinct:

**`discussions.md` - discussion thread.** For any exchange that needs more than a few lines: design decisions, planning, feedback, open questions.
- Each turn is appended to the file, preceded by `---` and a `[Name]` marker.
- Do not truncate or rewrite prior turns. Append only.
- Read from the last `[User]` marker when picking up a thread.
- Keep responses to ~50 lines per turn in the file.

**`todos.md` - action items only.** No discussion - only concrete, actionable tasks. Two sections: a flat numbered **Pending items** list where each item carries an inline priority (P1 must do next / P2 important / P3 nice to have, same scheme as agent-team priorities), and a short **Next** queue that names the immediate actions by referencing pending items by number. Compact aggressively: delete items once done and renumber Pending from 1. Decisions and rationale belong in `discussions.md`, not here.

## Safety Guardrails

- Never `git push --force` to main.
- Never delete project folders under `projects/` without confirmation.
- Never commit secrets or API keys.
- Never modify `.gitignore` in a way that exposes previously ignored files.

## Loop Agent Guardrails

These apply to agents running inside loop cycles (enforced via the cycle prompt built from `src/resources/PROMPT.md`):

- Write only inside `projects/<active_project>/`. Never modify framework files (`loop.py`, `config.yaml`, `src/`, `.claude/`).
- Never run `git push` - the loop owns git sync.
- Never write `human_directives.md` - it is human-owned and read-only to agents. consensus.md is agent-owned; humans steer only via human_directives.md.

## Adapt Skill

`.claude/skills/adapt/` is a human-run setup wizard for customizing the framework to a new domain before launching the loop. Agents and the loop never invoke it; the loop only detects an unadapted project and exits, directing the user to run /adapt interactively.

## Project Structure

See `README.md` for the full structure and core concepts.
