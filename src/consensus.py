"""Consensus relay baton: read, validate, backup, restore, snapshot."""

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

SENTINEL = "<!-- AGENTTEAM_UNADAPTED -->"


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
    """Return True if consensus.md is missing or carries the unadapted sentinel."""
    if not consensus_path.exists():
        return True
    return SENTINEL in consensus_path.read_text(encoding="utf-8")


def backup(project_dir: Path) -> None:
    """Copy consensus.md to memory/consensus.md.bak."""
    src = project_dir / "consensus.md"
    dst = project_dir / "memory" / "consensus.md.bak"
    if src.exists():
        shutil.copy2(src, dst)


def restore(project_dir: Path) -> bool:
    """Restore consensus.md from memory/consensus.md.bak. Returns True if restored."""
    bak = project_dir / "memory" / "consensus.md.bak"
    dst = project_dir / "consensus.md"
    if bak.exists():
        shutil.copy2(bak, dst)
        return True
    return False


def changed_since_backup(project_dir: Path) -> bool:
    """Return True if consensus.md differs from the backup."""
    src = project_dir / "consensus.md"
    bak = project_dir / "memory" / "consensus.md.bak"
    if not src.exists():
        return False
    if not bak.exists():
        return True
    return src.read_bytes() != bak.read_bytes()


def snapshot(project_dir: Path, cycle_num: int) -> None:
    """Copy consensus.md to memory/consensus-step-NNNN.md after a successful cycle."""
    src = project_dir / "consensus.md"
    if not src.exists():
        return
    dst = project_dir / "memory" / f"consensus-step-{cycle_num:04d}.md"
    shutil.copy2(src, dst)
