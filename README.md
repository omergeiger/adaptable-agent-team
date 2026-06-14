# AgentTeam

A generic, reusable multi-agent loop framework for Claude Code. Point it at a project, adapt it to your domain, and run a structured multi-agent loop that makes incremental progress on it - one headless Claude Code cycle at a time, coordinated through a shared consensus file.

The patterns are extracted and generalized from the [Auto-Company](https://github.com/omergeiger/Auto-Company) repo into a template that can be adapted to any domain.

## Scope

- **LLM provider**: Claude only, via the Claude Code CLI (`--permission-mode bypassPermissions`). No multi-provider abstraction.
- **OS**: macOS only. No Linux/Windows/WSL scaffolding.

## Quick Start

1. **Set up the environment** (Python 3.13+):
   ```bash
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   ```
2. **Adapt the framework to your domain.** Run the `/adapt` skill interactively in a Claude Code session at the repo root. It interviews you (domain, purpose, roles, phases, cadence) and generates the worker agent files, a tailored `PROMPT.md`, the domain skills, and a starter `projects/<name>/consensus.md` + `human_directives.md`. See `.dev-docs/example_cases.md` for ten worked adaptation cases.
3. **Configure** `config.yaml` - set `active_project`, the `squad` roster, cadence, and toggles (see below).
4. **Run the loop:**
   ```bash
   .venv/bin/python loop.py            # run until stopped
   .venv/bin/python loop.py --cycles 3 # stop after 3 successful cycles
   ```
   The loop detects an unadapted project (missing `consensus.md` or one still carrying the starter sentinel) and exits, directing you to run `/adapt` first.

## Repo Structure

```
AgentTeam/
├── README.md
├── CLAUDE.md                  # Directives for Claude Code sessions
├── loop.py                    # Main loop entrypoint
├── config.yaml                # Top-level config (active project, toggles)
├── requirements.txt
├── .claude/
│   ├── agents/                # Agent persona definitions (worker placeholders)
│   │   ├── orchestrator.md
│   │   └── worker.md
│   └── skills/                # Skill library
│       ├── adapt/             # Setup wizard: guides user to customize the framework
│       │   └── SKILL.md
│       └── example/           # Placeholder skill template
│           └── SKILL.md
├── src/                       # Python loop machinery + resources
│   ├── consensus.py           # Reads/writes/validates the consensus.md relay baton
│   ├── git_sync.py            # Pre/post loop git commit+push
│   └── resources/
│       └── PROMPT.md          # Cycle prompt template (orchestrator persona)
├── .dev-docs/                 # Dev docs and scratchpads
│   ├── example_cases.md       # Worked adaptation cases (end-to-end test recipes)
│   ├── todos.md
│   └── discussions.md
└── projects/                  # All project workspaces (one folder per project)
    └── <project-name>/
        ├── consensus.md        # Relay baton for this project's loop (agent-owned)
        ├── human_directives.md # Human steering file (human-owned, read-only to agents)
        ├── docs/               # Durable deliverables (agent-written, human-read)
        ├── logs/               # Operational audit trail (loop-written)
        └── memory/             # Agent long-term memory and consensus history
```

## Workflows

The recurring flows of operating the repo. Each links to the relevant detail under Core Concepts.

### 1. Adapt the framework to a domain (once per domain)
Run `/adapt` interactively at the repo root. The wizard interviews you and generates the worker agent files (`.claude/agents/`), domain skills (`.claude/skills/`), a tailored `src/resources/PROMPT.md`, and a starter `projects/<name>/` (with `consensus.md` + `human_directives.md`), then sets `active_project` and `squad` in `config.yaml`. Agent files, skills, and `PROMPT.md` are **repo-global** - adapting a new domain replaces the previous one's versions. Review the generated files before the first run. See [Adapt Skill](#adapt-skill-human-facing-pre-launch).

### 2. Run the loop
Two operating modes, selected by `single_cycle` in `config.yaml`:

- **Gated / supervised** (`single_cycle: true`) - runs one cycle and exits. Inspect the result, edit `human_directives.md`, re-run. Recommended for the first runs of a new domain and whenever you want tight control. `git_sync` is typically off here.
  ```bash
  .venv/bin/python loop.py
  ```
- **Continuous / autonomous** (`single_cycle: false`) - the loop self-drives, sleeping `loop_interval_seconds` between cycles, until you stop it (Ctrl-C / SIGTERM finishes the in-flight cycle, then exits cleanly) or it trips the circuit breaker. Use `--cycles N` to cap successful cycles. `git_sync: true` is the usual pairing so every cycle is committed.
  ```bash
  .venv/bin/python loop.py            # run until stopped
  .venv/bin/python loop.py --cycles 5 # stop after 5 successful cycles
  ```

### 3. Steer the team between cycles
Edit `projects/<active>/human_directives.md` - the human's only write channel (agents read it, never write it). Add a `## Cycle Overrides` entry for a one-off instruction that supersedes the consensus `## Next Action` (remove it once satisfied), a numbered `## Standing Directives` rule (D1, D2, ...) for a persistent constraint, or an entry under `## Answers` to resolve a question the agents raised in consensus `## Open Questions`. In continuous mode with `git_sync` on, the pre-cycle commit captures edits made between cycles. See [Human Directives File](#human-directives-file).

### 4. Review progress
- **`projects/<active>/consensus.md`** - current state at a glance: phase, what the last cycle did, the next action, and open questions.
- **`projects/<active>/docs/`** - the actual deliverables to judge the work by.
- **`projects/<active>/logs/cycle-NNNN-<timestamp>/`** - per-cycle audit trail (`prompt.md`, `output.json`, `metadata.json`, and `transcript.jsonl` when `verbosity` is on) for debugging what a cycle actually did.
- **History over time** - the per-cycle git history of `consensus.md` (with `git_sync`), or the `memory/consensus-step-NNNN.md` snapshots when it is off.

### 5. Switch or re-adapt a project
`projects/` can hold several project folders; each is self-contained. Point the loop at a different one by changing `active_project` in `config.yaml`. To repurpose the framework for a new domain, re-run `/adapt` - remember it overwrites the repo-global agent/skill/`PROMPT.md` files for the previous domain.

### 6. When the loop stops itself
- **Unadapted project** (missing `consensus.md` or carrying the starter sentinel) - the loop exits immediately; run `/adapt`.
- **Validation failure or no-op cycle** - consensus is restored from `memory/consensus.md.bak` and the consecutive-error counter increments; five in a row trips the circuit breaker and exits. Check `logs/loop.log` and the failing cycle's `metadata.json` / `output.json`. See [Consensus Validation & Recovery](#consensus-validation--recovery).
- **Rate limit / billing** - in continuous mode the loop waits before retrying; in gated mode it exits.
- **Cycle timeout** - if consensus was updated and still valid, progress is kept; otherwise the cycle counts as a failure.

### Developing the framework itself
`main` is the pristine, domain-agnostic template - adapt a domain on a **branch** so `main` stays generic and reusable. Framework dev notes live under `.dev-docs/` (`todos.md`, `discussions.md`, `example_cases.md`); they are tracked but are not part of an operator's runtime.

## Core Concepts

### Active Project
- `projects/` may contain multiple project folders.
- Exactly one project is active at a time, identified by `active_project` in `config.yaml`.
- The loop always operates on the active project. All outputs, logs, docs, and memory artifacts write into the active project folder.

### Project Workspace Layout
Each `projects/<name>/` folder is self-contained - everything the loop produces for that project lives inside it. At the root sit the two steering files (`consensus.md`, `human_directives.md`); the three subfolders divide the rest by purpose:

**`docs/` - durable work products (agent-written, human-read).** The actual deliverables of the loop: research summaries, design docs, decision records, drafts, reports - whatever the domain produces. Organized by agent role or topic (the adapt skill sets the convention for the domain). This is the folder a human reviews to judge progress. Anything meant to outlive a cycle and be read later belongs here, not in consensus.md (which stays small).

**`logs/` - operational audit trail (loop-written, agents never write here).**
- `loop.log` - loop-level event log: cycle start/end, validation pass/fail, restores, circuit-breaker trips, rate-limit waits. Rotated when it grows large.
- `cycle-NNNN-<timestamp>/` - one folder per cycle, containing:
  - `prompt.md` - the full assembled prompt sent to the orchestrator (PROMPT.md + guardrails + injected consensus + injected human directives)
  - `output.json` - the CLI's final result message (cost, subtype, result text)
  - `transcript.jsonl` - full stream-json transcript when `verbosity` is on; includes every Task delegation, i.e. the per-worker prompts
  - `metadata.json` - exit code, duration, timed-out flag, consensus-validation outcome
- Retention: the loop prunes the oldest cycle folders beyond `max_cycle_logs`.

**`memory/` - agent long-term memory and consensus history.** consensus.md is *current state only*; memory/ is where history and accumulated knowledge live:
- `consensus-step-NNNN.md` - numbered snapshot of consensus after each successful cycle (the audit trail of how the project evolved when `git_sync` is off; redundant with consensus.md's git history when it is on)
- `consensus.md.bak` - the pre-cycle backup used for restore on validation failure
- free-form agent notes/learnings that should persist across cycles but don't belong in the relay baton (e.g. things tried and ruled out, domain facts discovered)

Rule of thumb: deliverables -> `docs/`, diagnostics -> `logs/`, agent recall -> `memory/`.

### Loop Behavior
`loop.py` runs iterations. Each iteration makes **one** headless Claude Code CLI call (the orchestrator session); worker agents are subagents the orchestrator delegates to *within* that session via the Task tool. The loop never invokes workers directly.

Each iteration:
1. Pre-iteration: `git add . && git commit && git push` (if git_sync enabled)
2. Back up consensus.md to `memory/consensus.md.bak`
3. Build the cycle prompt: PROMPT.md + runtime guardrails + pre-injected consensus content + pre-injected human_directives.md content + cycle number
4. Invoke `claude -p <prompt> --permission-mode bypassPermissions` with a watchdog timeout
5. Validate consensus.md; on failure (or if consensus is unchanged), restore from backup and count toward the circuit breaker
6. Save a numbered per-cycle snapshot (`memory/consensus-step-NNNN.md`) and write logs
7. Post-iteration: `git add . && git commit && git push` (if git_sync enabled)

### Consensus Validation & Recovery
- `src/consensus.py` validates that every required `## ` section heading exists in consensus.md (exact heading text, case-sensitive, any order) - a loop-level integrity check that catches an agent mangling or truncating the relay baton.
- Required sections: `## Last Updated`, `## Current Phase`, `## What We Did This Cycle`, `## Key Decisions`, `## Next Action`, `## Team State`, `## Open Questions`.
- human_directives.md is not validated by the loop (human-owned, free-form).
- On validation failure the loop restores `consensus.md.bak`, logs the rejected version, and increments the consecutive-error counter. The circuit breaker exits the loop after five consecutive failures.
- An unchanged consensus after a cycle is treated as a failed cycle (no-op detection).

### Logging & Visibility
- Every cycle writes to `projects/<active>/logs/cycle-NNNN-<timestamp>/`: the full prompt sent to the orchestrator, the CLI's final output, and cycle metadata (exit code, cost, duration). See "Project Workspace Layout" for the per-file breakdown.
- `verbosity` flag in config.yaml: when verbose, the loop uses `--output-format stream-json` and persists the full transcript - including the orchestrator's Task-tool delegations to workers, which captures the per-agent prompts. The direction is maximum visibility into the loop from logs alone.

### Runtime Guardrails (enforced via prompt + loop)
- The cycle prompt instructs agents: write only inside `projects/<active>/`, never modify framework files (`loop.py`, `config.yaml`, `src/`, `.claude/`), never run git push (the loop owns git sync), never write human_directives.md (human-owned, read-only to agents).
- The CLI runs from the repo root (required so the session discovers `.claude/agents/`), so these restrictions are prompt-level, backed by the loop's backup/restore of critical files.

### Consensus.md Relay Baton
- Single file per project that agents read before acting and update after acting.
- Carries: current objective, last completed step, next step, open questions, blockers.
- **Agent-owned**: only agents write it. Human steering lives in `human_directives.md` instead, so the two never collide and a corrupted consensus never loses human input.

### Human Directives File
- `projects/<name>/human_directives.md` is the human's steering channel. Agents read it every cycle but never write it.
- Sections: `## Standing Directives` (persistent rules, numbered D1, D2, ... for unambiguous reference), `## Cycle Overrides` (one-off instructions that supersede consensus `## Next Action`; the human removes them once satisfied), `## Answers` (responses to consensus.md's `## Open Questions`).
- Precedence: Cycle Overrides > Standing Directives > consensus `## Next Action`.
- The loop injects the file's content into the cycle prompt, marked read-only. Agents acknowledge directive IDs they acted on in consensus.md's `## What We Did This Cycle`.
- In gated mode (`single_cycle: true`): run a cycle, edit human_directives.md, re-run.

### Dynamic Squad Assembly
- **Orchestrator-driven.** Not all agents run every iteration. The loop does not select the subset; it injects the full configured `squad` roster (config.yaml) into the cycle prompt, and the orchestrator chooses the relevant subset to delegate to via the Task tool (PROMPT.md). The loop stays domain-agnostic - the LLM judges task/phase relevance, not hardcoded phase->agent rules in core code.
- `config.yaml > squad` is the ceiling (which agents are available); the orchestrator picks from within it each cycle.
- A loop-driven `src/squad.py` was considered and rejected: it would couple the generic loop to domain-specific phase->agent mappings. Revisit only if deterministic, code-level subset control becomes a real need.

### Skill Library
- Reusable capabilities agents can invoke (e.g. web search, file write, code review).
- Defined as callable units, not baked into agent prompts.

### Adapt Skill (human-facing, pre-launch)
- `.claude/skills/adapt/` is a setup wizard run **by the human** in an interactive Claude Code session, *before* launching the loop on a new domain. It is not invoked by the loop or by agents.
- It interviews the user (domain, purpose, roles, phases, cadence) and generates customized agent files, a tailored PROMPT.md, a starter consensus.md, and a starter human_directives.md.
- The loop detects an unadapted project (missing consensus.md or one still carrying the starter sentinel marker) and exits with instructions to run /adapt interactively.

### Git Sync
- **Single-repo model:** the framework and all project folders live in one repo - the deployment clone of this template. The loop commits and pushes this repo as a whole; there is no separate per-project repo and no external artifact sync.
- On by default. Toggle: `config.yaml > git_sync: false`.
- Enforced in the loop, not in prompts (agents are additionally prompt-forbidden from running `git push`).
- Two commits per cycle: pre-cycle captures human edits made between cycles (e.g. `human_directives.md`), post-cycle captures agent artifacts.
- The sync set is governed by `.gitignore` - the ignore rules ARE the sync policy:
  - **Tracked (synced):** project `docs/` deliverables, `consensus.md`, `human_directives.md`. consensus.md's per-cycle commit history is the project's decision log.
  - **Ignored (local-only):** `projects/*/logs/` and `projects/*/memory/` - regenerable runtime artifacts. The `consensus-step-NNNN.md` snapshots duplicate what git history provides; they are the fallback audit trail for `git_sync: false` operation.

## Configuration

`config.yaml` keys:

| Key | Meaning |
|---|---|
| `active_project` | Which `projects/<name>/` the loop operates on |
| `squad` | The roster of worker agents available to the orchestrator |
| `model` | Claude model id passed to the CLI |
| `single_cycle` | Run one cycle and exit (gated mode) vs. loop continuously |
| `git_sync` | Enable pre/post-cycle commit+push |
| `loop_interval_seconds` | Sleep between cycles in continuous mode |
| `cycle_timeout_seconds` | Watchdog timeout for a single cycle |
| `verbosity` | Persist the full stream-json transcript per cycle |
| `max_cycle_logs` | Retention cap for per-cycle log folders |

## Non-Goals

| Feature | Decision |
|---|---|
| Multi-provider LLM abstraction | Excluded - Claude only |
| Linux/Windows/WSL support | Excluded - macOS only |
| Artifact sync to external project tracking folder | Excluded - everything stays in the repo |
| Loop-driven (code-level) squad selection | Excluded - orchestrator-driven instead |
