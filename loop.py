#!/usr/bin/env python3
"""AgentTeam loop - drives headless Claude Code cycles against a project."""

import json
import logging
import os
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

from core import consensus as con

REPO_ROOT = Path(__file__).parent.resolve()
RATE_LIMIT_WAIT_SECONDS = 3600
MAX_CONSECUTIVE_ERRORS = 5
LOG_ROTATE_BYTES = 10 * 1024 * 1024  # 10 MB

RATE_LIMIT_PATTERNS = [
    "rate limit", "ratelimit", "429", "too many requests",
    "usage limit", "billing", "insufficient credits",
    "overloaded", "resource_exhausted", "quota",
]


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
# Prompt assembly
# ---------------------------------------------------------------------------

def build_prompt(cycle_num: int, config: dict, consensus_content: str, directives_content: str) -> str:
    base = (REPO_ROOT / "PROMPT.md").read_text(encoding="utf-8")
    active = config["active_project"]
    squad = config.get("squad", [])
    roster = "\n".join(f"- {s}" for s in squad) if squad else "(none configured)"

    guardrails = f"""
---

## Runtime Guardrails (required)

- Write only inside `projects/{active}/`. Never modify framework files (`loop.py`, `core/`, `.claude/`, `config.yaml`).
- Never run `git push` — the loop owns git sync.
- Never write `human_directives.md` — it is human-owned and read-only to agents.

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

Active project: `{active}`. This is Cycle #{cycle_num}. Act decisively.
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
    cmd += ["--output-format", "stream-json" if verbose else "json"]
    if model:
        cmd += ["--model", model]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=str(REPO_ROOT),
        text=True,
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
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    config = load_config()
    active = config["active_project"]
    project_dir = REPO_ROOT / "projects" / active
    logs_dir = project_dir / "logs"
    memory_dir = project_dir / "memory"
    consensus_path = project_dir / "consensus.md"
    directives_path = project_dir / "human_directives.md"
    state_file = logs_dir / "loop_state.json"

    logs_dir.mkdir(parents=True, exist_ok=True)
    memory_dir.mkdir(parents=True, exist_ok=True)

    log = setup_logging(logs_dir / "loop.log")

    # Unadapted project guard
    if con.is_unadapted(consensus_path):
        log.error(f"Project '{active}' is unadapted or missing consensus.md.")
        log.error("Run the /adapt skill interactively to set up this project, then rerun the loop.")
        sys.exit(1)

    claude_bin = find_claude_bin()
    log.info("=== AgentTeam Loop Starting ===")
    log.info(f"Active project: {active}")
    log.info(f"Claude bin: {claude_bin}")
    log.info(f"Single cycle: {config.get('single_cycle', False)}")
    log.info(f"Verbosity: {config.get('verbosity', False)}")

    cycle_count = load_cycle_count(state_file)
    error_count = 0

    while True:
        cycle_count += 1
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        cycle_dir = logs_dir / f"cycle-{cycle_count:04d}-{ts}"
        cycle_dir.mkdir(parents=True, exist_ok=True)

        log.info(f"=== Cycle #{cycle_count} START ===")
        save_state(state_file, cycle_count, "running")

        # Back up consensus
        con.backup(project_dir)

        # Read steering files
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
            if con.changed_since_backup(project_dir):
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
                if not con.changed_since_backup(project_dir):
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
            restored = con.restore(project_dir)
            if restored:
                log.info(f"Cycle #{cycle_count}: consensus restored from backup")
            error_count += 1
            log.warning(
                f"Cycle #{cycle_count}: FAIL [{validation_outcome}] "
                f"(errors: {error_count}/{MAX_CONSECUTIVE_ERRORS})"
            )

            if is_rate_limited(raw_output, exit_code):
                log.warning(f"Cycle #{cycle_count}: rate limit detected.")
                save_state(state_file, cycle_count, "rate_limited")
                if config.get("single_cycle", False):
                    log.warning("Single-cycle mode - exiting instead of sleeping.")
                    sys.exit(1)
                log.warning(
                    f"Waiting {RATE_LIMIT_WAIT_SECONDS}s ({RATE_LIMIT_WAIT_SECONDS // 3600}h)..."
                )
                time.sleep(RATE_LIMIT_WAIT_SECONDS)
                error_count = 0
            elif error_count >= MAX_CONSECUTIVE_ERRORS:
                log.error(
                    f"Circuit breaker tripped: {MAX_CONSECUTIVE_ERRORS} consecutive failures. Exiting."
                )
                save_state(state_file, cycle_count, "circuit_broken")
                sys.exit(1)
        else:
            error_count = 0
            con.snapshot(project_dir, cycle_count)
            log.info(
                f"Cycle #{cycle_count}: OK [{validation_outcome}] "
                f"(cost: {cost}, duration: {duration:.1f}s)"
            )

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
        time.sleep(interval)


if __name__ == "__main__":
    main()
