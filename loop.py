#!/usr/bin/env python3
"""AgentTeam loop - drives headless Claude Code cycles against a project."""

import argparse
import fcntl
import json
import logging
import os
import shutil
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

from src import consensus as con
from src import git_sync
from src import plugin_check

REPO_ROOT = Path(__file__).parent.resolve()
PLUGIN_DIR = REPO_ROOT / "src" / "resources" / "loop-plugin"
RATE_LIMIT_WAIT_SECONDS = 3600
MAX_CONSECUTIVE_ERRORS = 5
LOG_ROTATE_BYTES = 10 * 1024 * 1024  # 10 MB

_stop_event = threading.Event()


def _signal_handler(sig, frame):
    _stop_event.set()


RATE_LIMIT_PATTERNS = [
    "rate limit", "ratelimit", "429", "too many requests",
    "usage limit", "billing", "insufficient credits",
    "overloaded", "resource_exhausted", "quota",
]


# ---------------------------------------------------------------------------
# CLI args
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="AgentTeam loop runner")
    p.add_argument(
        "--cycles", type=int, default=None, metavar="N",
        help="Stop after N successful cycles (default: run indefinitely).",
    )
    args = p.parse_args()
    if args.cycles is not None and args.cycles < 1:
        p.error("--cycles must be a positive integer")
    return args


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_config() -> dict:
    with open(REPO_ROOT / "config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def setup_logging(log_path: Path) -> logging.Logger:
    if log_path.exists() and log_path.stat().st_size > LOG_ROTATE_BYTES:
        log_path.rename(log_path.with_suffix(".log.old"))

    logger = logging.getLogger("agentteam")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        fmt = logging.Formatter("[%(asctime)s] %(message)s", "%Y-%m-%d %H:%M:%S")
        fh = logging.FileHandler(log_path, encoding="utf-8")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(fmt)
        logger.addHandler(sh)
    return logger


# ---------------------------------------------------------------------------
# Claude binary resolution
# ---------------------------------------------------------------------------

def find_claude_bin() -> str:
    # Try loading user profile so nvm/brew installs are visible
    try:
        result = subprocess.run(
            ["bash", "-ic", "command -v claude"],
            capture_output=True, text=True, timeout=5,
        )
        candidate = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else ""
        if candidate and Path(candidate).is_file() and os.access(candidate, os.X_OK):
            return candidate
    except Exception:
        pass

    found = shutil.which("claude")
    if found:
        return found

    raise RuntimeError(
        "Claude CLI not found. Install Claude Code and verify with 'claude --version'."
    )


# ---------------------------------------------------------------------------
# Single-instance lock
# ---------------------------------------------------------------------------

def acquire_singleton_lock(lock_path: Path):
    """Ensure only one loop runs per repo. Two concurrent loops race on git
    sync (both commit/push the same branch) and double-run cycles.

    Uses an advisory flock held for the process lifetime. The OS releases it
    automatically when the process dies - including SIGKILL and crashes - so
    there is no stale-lock problem. Returns the open handle, which the caller
    MUST keep referenced (garbage-collecting it closes the fd and releases the
    lock).
    """
    fd = open(lock_path, "a+")  # a+ does not truncate, so an existing PID survives the failed-acquire read
    try:
        fcntl.flock(fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        fd.seek(0)
        existing = fd.read().strip() or "unknown"
        fd.close()
        print(
            f"[agentteam] ERROR: another loop.py is already running (PID {existing}).",
            file=sys.stderr,
        )
        print(
            f"[agentteam] Refusing to start a second loop on this repo - it would race on git sync. Lock: {lock_path}",
            file=sys.stderr,
        )
        sys.exit(1)
    fd.seek(0)
    fd.truncate()
    fd.write(str(os.getpid()))
    fd.flush()
    return fd


# ---------------------------------------------------------------------------
# Prompt assembly
# ---------------------------------------------------------------------------

def build_prompt(cycle_num: int, config: dict, consensus_content: str, directives_content: str) -> str:
    base = (REPO_ROOT / "src" / "resources" / "PROMPT.md").read_text(encoding="utf-8")
    active = config["active_project"]
    squad = config.get("squad", [])
    # Agents ship in the loop plugin, so their subagent_type is plugin-namespaced.
    roster = "\n".join(f"- {s} (subagent_type: `loop-plugin:{s}`)" for s in squad) if squad else "(none configured)"
    cycle_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    # File-safe timestamp for by-product doc naming (colons replaced with hyphens, no Z)
    cycle_time_file = cycle_time[:-1].replace(":", "-")

    guardrails = f"""
---

## Runtime Guardrails (required)

- **Deliverables** (the domain product the project is chartered to produce): write to `projects/{active}/`. Use domain-native filenames with no cycle or persona stamps; no framework references.
- **By-products** (the synthesized account of this cycle's work): you, the orchestrator, write one file per persona turn to `auto-outputs/{active}/docs/` - one for each sub-agent you delegated to (synthesized from its report) and one for your own turn if you did hands-on work. Sub-agents write only deliverables. Name each file `cycle-{cycle_num:04d}-{cycle_time_file}-<persona>-<slug>.md`.
- **Consensus**: `steering/{active}/consensus.md` is the only steering file you may write, and only you (the orchestrator) write it - never a sub-agent.
- Never modify framework files (`loop.py`, `config.yaml`, `src/`, `.claude/`) or any other file in `steering/`.
- Never run `git push` - the loop owns git sync.
- Never write `human_directives.md` - it is human-owned and read-only to agents.
- Never invoke the human-run skills in `.claude/skills/` (`/adapt`, `/retrospect`).

---

## Available Agent Roster

{roster}

---

## Human Directives (read-only — never modify this file)

{directives_content}

---

## Current Consensus (pre-loaded — do not re-read from disk)

{consensus_content}

---

Active project: `{active}`. This is Cycle #{cycle_num}. Cycle time: `{cycle_time}` (use this exact value for `## Last Updated` in consensus.md). Act decisively.
"""
    return base + guardrails


# ---------------------------------------------------------------------------
# Cycle execution
# ---------------------------------------------------------------------------

def run_cycle(
    prompt: str, claude_bin: str, timeout_seconds: int, verbose: bool, model: str | None = None
) -> tuple[int, str, list[str], bool]:
    """
    Run one `claude -p` invocation.
    Returns (exit_code, raw_output, transcript_lines, timed_out).
    transcript_lines is populated only when verbose=True.
    """
    cmd = [claude_bin, "-p", prompt, "--permission-mode", "bypassPermissions"]
    # Load loop-only skills as a plugin, scoped to this invocation. Interactive
    # Claude Code sessions never pass --plugin-dir, so these skills stay invisible
    # to them and are addressed namespaced as `loop-plugin:<skill-name>`.
    cmd += ["--plugin-dir", str(PLUGIN_DIR)]
    if verbose:
        # The CLI requires --verbose for stream-json in print mode
        cmd += ["--output-format", "stream-json", "--verbose"]
    else:
        cmd += ["--output-format", "json"]
    if model:
        cmd += ["--model", model]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=str(REPO_ROOT),
        text=True,
        # Own session so a terminal Ctrl-C (SIGINT to the loop's process group)
        # does not reach the child; the cycle finishes and the loop exits
        # gracefully at the next stop-event check.
        start_new_session=True,
    )

    timed_out = False

    def _kill():
        nonlocal timed_out
        if proc.poll() is None:
            timed_out = True
            proc.terminate()
            time.sleep(5)
            if proc.poll() is None:
                proc.kill()

    timer = threading.Timer(timeout_seconds, _kill)
    timer.start()
    try:
        stdout, _ = proc.communicate()
    finally:
        timer.cancel()

    lines = [ln for ln in stdout.splitlines() if ln.strip()] if verbose else []
    return proc.returncode, stdout, lines, timed_out


def extract_output_json(raw: str, verbose: bool) -> dict:
    """Parse the CLI output into a result dict."""
    if not raw.strip():
        return {}
    if verbose:
        for line in reversed(raw.splitlines()):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if obj.get("type") == "result":
                    return obj
            except json.JSONDecodeError:
                continue
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def is_rate_limited(raw: str, exit_code: int) -> bool:
    lower = raw.lower()
    return any(p in lower for p in RATE_LIMIT_PATTERNS)


# ---------------------------------------------------------------------------
# Log pruning
# ---------------------------------------------------------------------------

def prune_cycle_logs(logs_dir: Path, max_logs: int) -> None:
    folders = sorted(logs_dir.glob("cycle-*"), key=lambda p: p.name)
    for folder in folders[: max(0, len(folders) - max_logs)]:
        shutil.rmtree(folder, ignore_errors=True)


# ---------------------------------------------------------------------------
# Cycle state persistence
# ---------------------------------------------------------------------------

def load_cycle_count(state_file: Path) -> int:
    if state_file.exists():
        try:
            return int(json.loads(state_file.read_text()).get("cycle_count", 0))
        except Exception:
            pass
    return 0


def save_state(state_file: Path, cycle_count: int, status: str) -> None:
    state_file.write_text(
        json.dumps(
            {
                "cycle_count": cycle_count,
                "status": status,
                "last_run": datetime.now(timezone.utc).isoformat(),
            },
            indent=2,
        )
    )


# ---------------------------------------------------------------------------
# Read-only finalization
# ---------------------------------------------------------------------------

def finalize_auto_outputs(docs_dir: Path, memory_dir: Path) -> None:
    """Make all files in auto-outputs docs/ and memory/ read-only after a successful cycle."""
    for directory in [docs_dir, memory_dir]:
        if directory.exists():
            for f in directory.rglob("*"):
                if f.is_file():
                    try:
                        f.chmod(0o444)
                    except OSError:
                        pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    args = parse_args()
    signal.signal(signal.SIGTERM, _signal_handler)
    signal.signal(signal.SIGINT, _signal_handler)

    config = load_config()
    active = config["active_project"]

    # Three top-level spaces per project
    steering_dir = REPO_ROOT / "steering" / active
    auto_outputs_dir = REPO_ROOT / "auto-outputs" / active
    project_dir = REPO_ROOT / "projects" / active  # deliverables only

    logs_dir = auto_outputs_dir / "logs"
    memory_dir = auto_outputs_dir / "memory"
    docs_dir = auto_outputs_dir / "docs"

    consensus_path = steering_dir / "consensus.md"
    directives_path = steering_dir / "human_directives.md"
    state_file = logs_dir / "loop_state.json"

    # Unadapted project guard — runs before any mkdir so no stray directories are created
    if con.is_unadapted(consensus_path):
        print(f"[agentteam] ERROR: Project '{active}' is unadapted or missing consensus.md.", file=sys.stderr)
        print("[agentteam] Run the /adapt skill interactively to set up this project, then rerun the loop.", file=sys.stderr)
        sys.exit(1)

    # Plugin preflight - Claude Code silently skips agent/skill files without
    # name/description frontmatter, so fail loudly here instead.
    plugin_problems = plugin_check.check_plugin(PLUGIN_DIR)
    if plugin_problems:
        print("[agentteam] ERROR: loop-plugin files would not be registered by Claude Code:", file=sys.stderr)
        for problem in plugin_problems:
            print(f"[agentteam]   {problem}", file=sys.stderr)
        print("[agentteam] Add a leading '---' block with 'name' (matching the file/dir) and 'description'.", file=sys.stderr)
        sys.exit(1)

    steering_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    memory_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)
    project_dir.mkdir(parents=True, exist_ok=True)

    log = setup_logging(logs_dir / "loop.log")

    # Single-instance guard - held for the whole process lifetime (do not let
    # _lock fall out of scope, or the fd closes and the lock releases).
    _lock = acquire_singleton_lock(REPO_ROOT / ".loop.lock")

    claude_bin = find_claude_bin()
    log.info("=== AgentTeam Loop Starting ===")
    log.info(f"Active project: {active}")
    log.info(f"Claude bin: {claude_bin}")
    log.info(f"Single cycle: {config.get('single_cycle', False)}")
    log.info(f"Verbosity: {config.get('verbosity', False)}")

    cycle_count = load_cycle_count(state_file)
    error_count = 0
    remaining_cycles = args.cycles  # None = run indefinitely

    while True:
        cycle_count += 1
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        cycle_dir = logs_dir / f"cycle-{cycle_count:04d}-{ts}"
        cycle_dir.mkdir(parents=True, exist_ok=True)

        log.info(f"=== Cycle #{cycle_count} START ===")
        save_state(state_file, cycle_count, "running")

        if config.get("git_sync", True):
            git_sync.pre_cycle(cycle_count, REPO_ROOT, log)

        # Read steering files (pre-cycle snapshot held in memory for restore)
        consensus_content = con.read(consensus_path)
        directives_content = (
            directives_path.read_text(encoding="utf-8")
            if directives_path.exists()
            else "(no directives file)"
        )

        # Assemble and save prompt
        prompt = build_prompt(cycle_count, config, consensus_content, directives_content)
        (cycle_dir / "prompt.md").write_text(prompt, encoding="utf-8")

        # Run the cycle
        timeout = config.get("cycle_timeout_seconds", 1800)
        verbose = config.get("verbosity", False)
        model = config.get("model") or None
        start_time = time.time()

        exit_code, raw_output, transcript_lines, timed_out = run_cycle(
            prompt, claude_bin, timeout, verbose, model
        )
        duration = time.time() - start_time

        # Persist outputs
        output_obj = extract_output_json(raw_output, verbose)
        (cycle_dir / "output.json").write_text(
            json.dumps(output_obj, indent=2) if output_obj else raw_output,
            encoding="utf-8",
        )
        if verbose and transcript_lines:
            (cycle_dir / "transcript.jsonl").write_text(
                "\n".join(transcript_lines), encoding="utf-8"
            )

        # ------------------------------------------------------------------
        # Validate consensus
        # ------------------------------------------------------------------
        cycle_failed = False
        validation_outcome = "unknown"

        if timed_out:
            # Soft timeout: keep progress if consensus was updated and valid
            if con.changed_since(consensus_path, consensus_content):
                try:
                    con.validate(con.read(consensus_path))
                    validation_outcome = "ok:timeout_with_update"
                    log.info(f"Cycle #{cycle_count}: timed out but consensus updated; keeping progress")
                except con.ConsensusError as exc:
                    cycle_failed = True
                    validation_outcome = f"fail:timeout_invalid:{exc}"
            else:
                cycle_failed = True
                validation_outcome = "fail:timeout_no_update"
        elif exit_code != 0:
            cycle_failed = True
            validation_outcome = f"fail:exit_{exit_code}"
        else:
            try:
                new_content = con.read(consensus_path)
                con.validate(new_content)
                if not con.changed_since(consensus_path, consensus_content):
                    log.warning(f"Cycle #{cycle_count}: consensus unchanged (no-op)")
                    cycle_failed = True
                    validation_outcome = "fail:unchanged"
                else:
                    validation_outcome = "ok"
            except con.ConsensusError as exc:
                log.warning(f"Cycle #{cycle_count}: validation failed: {exc}")
                cycle_failed = True
                validation_outcome = f"fail:invalid:{exc}"

        cost = output_obj.get("total_cost_usd") or output_obj.get("cost_usd") or "N/A"

        # Write metadata
        metadata = {
            "cycle": cycle_count,
            "exit_code": exit_code,
            "duration_seconds": round(duration, 2),
            "timed_out": timed_out,
            "validation_outcome": validation_outcome,
            "cost_usd": cost,
            "subtype": output_obj.get("subtype", "unknown"),
            "timestamp": ts,
        }
        (cycle_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        # ------------------------------------------------------------------
        # Handle failure vs success
        # ------------------------------------------------------------------
        if cycle_failed:
            restored = con.restore(consensus_path, consensus_content)
            if restored:
                log.info(f"Cycle #{cycle_count}: consensus restored from pre-cycle snapshot")
            error_count += 1
            log.warning(
                f"Cycle #{cycle_count}: FAIL [{validation_outcome}] "
                f"(errors: {error_count}/{MAX_CONSECUTIVE_ERRORS})"
            )

            # Circuit breaker applies to every failure cause, including a
            # persistent rate-limit/billing condition (checked before the wait
            # so it can't be masked by the rate-limit branch resetting state).
            if error_count >= MAX_CONSECUTIVE_ERRORS:
                log.error(
                    f"Circuit breaker tripped: {MAX_CONSECUTIVE_ERRORS} consecutive failures. Exiting."
                )
                save_state(state_file, cycle_count, "circuit_broken")
                sys.exit(1)

            if is_rate_limited(raw_output, exit_code):
                log.warning(f"Cycle #{cycle_count}: rate limit detected.")
                save_state(state_file, cycle_count, "rate_limited")
                if config.get("single_cycle", False):
                    log.warning("Single-cycle mode - exiting instead of sleeping.")
                    sys.exit(1)
                log.warning(
                    f"Waiting {RATE_LIMIT_WAIT_SECONDS}s ({RATE_LIMIT_WAIT_SECONDS // 3600}h)..."
                )
                if _stop_event.wait(timeout=RATE_LIMIT_WAIT_SECONDS):
                    log.info("Stop signal received during rate-limit wait - exiting cleanly.")
                    save_state(state_file, cycle_count, "stopped")
                    break
                # Backoff already served; start the next cycle now rather than
                # also sleeping the normal inter-cycle interval. error_count is
                # left intact so consecutive rate-limits still trip the breaker.
                continue
        else:
            error_count = 0
            con.snapshot(steering_dir, memory_dir, cycle_count)
            finalize_auto_outputs(docs_dir, memory_dir)
            log.info(
                f"Cycle #{cycle_count}: OK [{validation_outcome}] "
                f"(cost: {cost}, duration: {duration:.1f}s)"
            )
            if config.get("git_sync", True):
                git_sync.post_cycle(cycle_count, REPO_ROOT, log)

            signal_text = con.read_signal(con.read(consensus_path))
            if signal_text:  # truthy: skip None and empty/whitespace-only signals
                token = signal_text.split()[0].lower()
                if token == "done":
                    log.info(f"Cycle #{cycle_count}: Loop Signal 'done' - final deliverable written. Exiting.")
                    save_state(state_file, cycle_count, "done")
                    sys.exit(0)
                elif token == "stop":
                    log.info(f"Cycle #{cycle_count}: Loop Signal 'stop' - stop acknowledged. Exiting.")
                    save_state(state_file, cycle_count, "stopped")
                    sys.exit(0)
                elif token == "block":
                    reason = signal_text[len("block"):].lstrip(" -").strip()
                    log.warning(
                        f"Cycle #{cycle_count}: Loop Signal 'block' - {reason}. "
                        "Update human_directives.md and restart the loop."
                    )
                    save_state(state_file, cycle_count, "blocked")
                    sys.exit(1)
                else:
                    log.warning(f"Cycle #{cycle_count}: Loop Signal '{token}' unrecognized - ignoring.")

            if remaining_cycles is not None:
                remaining_cycles -= 1
                if remaining_cycles <= 0:
                    log.info(f"Cycle #{cycle_count}: --cycles limit reached - exiting.")
                    save_state(state_file, cycle_count, "idle")
                    break

        # Prune old cycle log folders
        prune_cycle_logs(logs_dir, config.get("max_cycle_logs", 50))

        save_state(state_file, cycle_count, "idle")

        if config.get("single_cycle", False):
            log.info(f"Cycle #{cycle_count}: DONE. Single-cycle mode — exiting.")
            if cycle_failed:
                sys.exit(1)
            break

        interval = config.get("loop_interval_seconds", 30)
        log.info(f"Sleeping {interval}s before next cycle...")
        if _stop_event.wait(timeout=interval):
            log.info("Stop signal received - exiting cleanly.")
            save_state(state_file, cycle_count, "stopped")
            break


if __name__ == "__main__":
    main()
