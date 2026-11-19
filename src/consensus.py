"""Consensus relay baton: read, validate, restore, snapshot."""

import shutil
from pathlib import Path

REQUIRED_SECTIONS = [
    "## Last Updated",
    "## Current Phase",
    "## What We Did This Cycle",
    "## Key Decisions",
    "## Next Action",
    "## Team State",
    "## Open Questions",
]


class ConsensusError(Exception):
    pass


def validate(content: str) -> None:
    """Raise ConsensusError if any required section heading is missing."""
    missing = [s for s in REQUIRED_SECTIONS if s not in content]
    if missing:
        raise ConsensusError(f"Missing required sections: {missing}")


def read(consensus_path: Path) -> str:
    return consensus_path.read_text(encoding="utf-8")


def write(consensus_path: Path, content: str) -> None:
    consensus_path.write_text(content, encoding="utf-8")


def is_unadapted(consensus_path: Path) -> bool:
    """Return True if the project has no consensus.md - /adapt has not set it up."""
    return not consensus_path.exists()


def restore(consensus_path: Path, pre_content: str) -> bool:
    """Restore consensus.md from the pre-cycle in-memory snapshot. Returns True if restored."""
    if not pre_content:
        return False
    consensus_path.write_text(pre_content, encoding="utf-8")
    return True


def changed_since(consensus_path: Path, pre_content: str) -> bool:
    """Return True if consensus.md differs from the pre-cycle snapshot."""
    if not consensus_path.exists():
        return False
    return consensus_path.read_text(encoding="utf-8") != pre_content


def read_signal(content: str) -> str | None:
    """Return the text after '## Loop Signal:' if present, else None."""
    for line in content.splitlines():
        if line.startswith("## Loop Signal:"):
            return line[len("## Loop Signal:"):].strip()
    return None


def snapshot(steering_dir: Path, memory_dir: Path, cycle_num: int) -> None:
    """Copy consensus.md to memory/consensus-step-NNNN.md and make it read-only."""
    src = steering_dir / "consensus.md"
    if not src.exists():
        return
    dst = memory_dir / f"consensus-step-{cycle_num:04d}.md"
    shutil.copy2(src, dst)
    dst.chmod(0o444)
