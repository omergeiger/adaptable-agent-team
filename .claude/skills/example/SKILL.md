# /example — Skill Template

This file shows the pattern for writing AgentTeam skills.

Skills are run interactively by humans in a Claude Code session using `/skillname`. They are never invoked by the loop or by agents.

---

## Skill File Structure

Every `SKILL.md` starts with a brief description of when to use the skill, then contains instructions Claude follows when the skill is invoked.

```
# /skillname — Short Title

Brief description of what this skill does and when to use it.

---

## When to Run

(conditions that trigger this skill)

## What This Skill Does

(step-by-step instructions Claude follows)

## Output

(what the skill produces and where it goes)
```

---

## Key Patterns

- **Human-only**: Skills are run by humans in interactive sessions. Never add logic that assumes loop or agent invocation.
- **Self-contained**: Each skill file should fully specify what to do. Don't rely on other skills being loaded.
- **Generative**: Most skills produce files — new configs, customized agents, scaffolded projects, or reports.
- **Instructional**: Write skills as instructions to Claude, not documentation for humans. Claude reads the SKILL.md and follows it.

---

## Adding a New Skill

1. Create `.claude/skills/<skillname>/SKILL.md`
2. Write instructions Claude should follow when `/skillname` is invoked
3. Test by running `/skillname` in an interactive Claude Code session

Skills do not require registration — any file at `.claude/skills/<name>/SKILL.md` is automatically available as `/<name>`.
