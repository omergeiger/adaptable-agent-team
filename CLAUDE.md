# AgentTeam - Claude Code Directives

## Project Overview

AgentTeam is a generic multi-agent loop framework for Claude Code. It extracts the core patterns from Autonomous-Company (https://github.com/MaxMiksa/Autonomous-Company, MIT) into a reusable template that can be adapted to any domain or purpose.

## Scope

- **LLM provider**: Claude only (Claude Code CLI, `--permission-mode bypassPermissions`).
- **OS**: macOS only.

## Safety Guardrails

- Never `git push --force` to main.
- Never delete project folders under `projects/` without confirmation.
- Never commit secrets or API keys.
- Never modify `.gitignore` in a way that exposes previously ignored files.

## Loop Agent Guardrails

These apply to agents running inside loop cycles (enforced via the cycle prompt built from `src/resources/PROMPT.md`):

- Write deliverables to `projects/<active_project>/` and per-cycle by-product docs to `auto-outputs/<active_project>/docs/` (the orchestrator writes one per persona turn; sub-agents write only deliverables). Never modify framework files (`loop.py`, `config.yaml`, `src/`, `.claude/`) or steering files in `steering/` - except `consensus.md`, which only the orchestrator writes.
- Never invoke the human-run skills in `.claude/skills/` (`/adapt`, `/retrospect`).
- Never run `git push` - the loop owns git sync.
- Never write `human_directives.md` - it is human-owned and read-only to agents. consensus.md is agent-owned; humans steer only via human_directives.md.

## Skills

Skills are reusable, callable units rather than instructions baked into agent prompts. There are two homes, split by audience:

- **`.claude/skills/<name>/SKILL.md`** - human-run setup skills (currently `/adapt` and `/retrospect`). Discovered by both interactive Claude Code sessions and headless loop sessions (same cwd), so loop agents are explicitly forbidden from invoking them by the runtime guardrails `loop.py` appends to the cycle prompt. Invoked interactively as `/<name>`.
- **`src/resources/loop-plugin/skills/<name>/SKILL.md`** - agent-applied skills, loaded only into headless loop sessions via `claude -p --plugin-dir` (see `run_cycle` in `loop.py`). Invisible to interactive sessions; addressed namespaced as `loop-plugin:<name>`. This is the home for both framework loop skills and the domain-convention skills `/adapt` generates (digest templates, scoring rubrics, test-gate protocols - anything that must not drift across cycles).

Authoring conventions: each `SKILL.md` starts with YAML frontmatter (`name` matching the directory, `description` saying when to apply it) - without it Claude Code silently skips the skill, and `loop.py` refuses to start (the same applies to `loop-plugin/agents/*.md`, where `name` matches the file stem). It declares its audience at the top, is self-contained (does not rely on other skills being loaded), and is written as instructions Claude follows when the skill runs (not human documentation). See `src/resources/loop-plugin/skills/example-loop-skill/` for the agent-applied pattern.

## Adapt Skill

`.claude/skills/adapt/` is a human-run setup wizard for customizing the framework to a new domain before launching the loop. It generates the sub-agent files (one per domain role - **all** domain roles are sub-agents; the headless cycle session itself is the generic orchestrator, never a domain role), a tailored `src/resources/PROMPT.md`, the domain-convention skills (into `src/resources/loop-plugin/skills/`), and the starter steering files. Agents and the loop never invoke it; the loop only detects an unadapted project and exits, directing the user to run /adapt interactively.

## Project Structure

See `README.md` for the full structure and core concepts.
