---
name: example-loop-skill
description: Template/reference for loop-only skills - applied BY AGENTS during loop cycles, never available to interactive Claude Code. Addressed as loop-plugin:example-loop-skill.
---

# loop-plugin:example-loop-skill - Loop-Only Skill Template

This is a **domain convention skill applied by agents during loop cycles**. It is
delivered through the `loop-plugin` plugin, which `loop.py` loads with
`--plugin-dir` on every `claude -p` invocation. It is therefore invisible to
interactive Claude Code sessions running in this repo - only headless loop agents
can see and invoke it.

Use this directory (`src/resources/loop-plugin/skills/`) for any skill that should
steer agent behavior mid-cycle without leaking into the human's interactive
session. This is also where `/adapt` writes the domain-convention skills it
generates (digest templates, scoring rubrics, test-gate protocols). For human-run
setup skills (like /adapt itself), use `.claude/skills/` instead.

---

## When to Run

(Conditions, decided by the agent during a cycle, that trigger this skill.)

## What This Skill Does

(Step-by-step instructions the agent follows when the skill is invoked.)

## Output

(What the skill produces and where it goes - usually files under
`projects/<active_project>/`.)

---

## Notes for Authors

- **Namespacing**: plugin skills are invoked as `loop-plugin:<name>`, not bare
  `<name>`. Reference them by the namespaced form in `PROMPT.md` and agent files.
- **Audience**: write for headless agents, not humans. The agent reads this
  SKILL.md and follows it.
- **Self-contained**: do not rely on other skills being loaded.
- **Adding a skill**: create
  `src/resources/loop-plugin/skills/<name>/SKILL.md` - no registration needed;
  the plugin exposes every skill under its `skills/` directory automatically.
