# AgentTeam - Claude Code Directives

## Project Overview

AgentTeam is a generic multi-agent loop framework for Claude Code. It extracts the core patterns from the Auto-Company repo (https://github.com/omergeiger/Auto-Company) into a reusable template that can be adapted to any domain or purpose.

## Scope

- **LLM provider**: Claude only (Claude Code CLI, `--permission-mode bypassPermissions`).
- **OS**: macOS only.

## Communication Convention

For any discussion that requires more than a few lines - design decisions, planning, feedback, open questions - use `comments.txt` in the project root.

**Protocol:**
- Each turn is appended to the file, preceded by `---` and a `[Name]` marker.
- Do not truncate or rewrite prior turns. Append only.
- Read from the last `[User]` marker when picking up a thread.
- Keep responses to ~50 lines per turn in the file.

## Safety Guardrails

- Never `git push --force` to main.
- Never delete project folders under `projects/` without confirmation.
- Never commit secrets or API keys.
- Never modify `.gitignore` in a way that exposes previously ignored files.

## Project Structure

See `PLAN.md` for the full structure and build order.
