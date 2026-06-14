"""Git sync helpers: pre/post cycle commits and push."""

import logging
import subprocess
from pathlib import Path


def _run(args: list[str], cwd: Path, logger: logging.Logger) -> tuple[int, str]:
    result = subprocess.run(args, capture_output=True, text=True, cwd=str(cwd))
    if result.returncode != 0 and result.stderr.strip():
        logger.warning(f"git {args[1]}: {result.stderr.strip()}")
    return result.returncode, result.stdout.strip()


def _commit_and_push(message: str, repo_root: Path, logger: logging.Logger) -> bool:
    """Stage all changes, commit, and push. Returns True if a commit was made."""
    _run(["git", "add", "-A"], repo_root, logger)

    # exit 0 = no staged differences; exit 1 = staged changes present
    rc, _ = _run(["git", "diff", "--staged", "--quiet"], repo_root, logger)
    if rc == 0:
        return False

    rc, _ = _run(["git", "commit", "-m", message], repo_root, logger)
    if rc != 0:
        logger.warning("git commit failed - skipping push")
        return False

    rc, _ = _run(["git", "push"], repo_root, logger)
    if rc != 0:
        logger.warning("git push failed - commit is local only")

    return True


def pre_cycle(cycle_num: int, repo_root: Path, logger: logging.Logger) -> None:
    """Commit any human edits made between cycles before the cycle runs."""
    msg = f"pre-cycle {cycle_num}: capture human edits"
    if _commit_and_push(msg, repo_root, logger):
        logger.info(f"git sync: pre-cycle {cycle_num} committed and pushed")


def post_cycle(cycle_num: int, repo_root: Path, logger: logging.Logger) -> None:
    """Commit agent artifacts produced during the cycle."""
    msg = f"cycle {cycle_num}: agent artifacts"
    if _commit_and_push(msg, repo_root, logger):
        logger.info(f"git sync: cycle {cycle_num} committed and pushed")
