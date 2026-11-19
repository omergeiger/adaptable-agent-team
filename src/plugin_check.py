"""Preflight check for the loop plugin's agent and skill files.

Claude Code registers a plugin agent or skill only when its file starts with a
YAML frontmatter block carrying `name` and `description`. A file without one is
silently skipped: the headless session never sees it, and nothing errors. This
check makes that failure loud before the first cycle runs.
"""

from pathlib import Path

import yaml


class FrontmatterError(ValueError):
    """Raised when a leading `---` block exists but is not a valid YAML mapping."""


def _frontmatter(text: str) -> dict | None:
    """Return the leading `---` YAML block as a dict, or None if there is none.

    Raises FrontmatterError if the block is present but unparseable or not a mapping.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            try:
                data = yaml.safe_load("\n".join(lines[1:i]))
            except yaml.YAMLError as exc:
                detail = " ".join(str(getattr(exc, "problem", None) or exc).split())
                mark = getattr(exc, "problem_mark", None)
                where = f" (line {mark.line + 2})" if mark is not None else ""
                raise FrontmatterError(f"invalid YAML{where}: {detail}") from exc
            if not isinstance(data, dict):
                raise FrontmatterError("frontmatter is not a key/value mapping")
            return data
    return None


def check_file(path: Path, expected_name: str) -> list[str]:
    """Return the problems found in one agent or skill file (empty = valid)."""
    try:
        meta = _frontmatter(path.read_text(encoding="utf-8"))
    except FrontmatterError as exc:
        return [f"{path}: frontmatter {exc} - quote values that contain ': '"]
    if meta is None:
        return [f"{path}: missing YAML frontmatter (--- name/description ---)"]
    problems = []
    for field in ("name", "description"):
        value = meta.get(field)
        if not isinstance(value, str) or not value.strip():
            problems.append(f"{path}: frontmatter lacks a non-empty '{field}'")
    name = meta.get("name")
    if isinstance(name, str) and name.strip() and name.strip() != expected_name:
        problems.append(f"{path}: name '{name.strip()}' does not match '{expected_name}'")
    return problems


def check_plugin(plugin_dir: Path) -> list[str]:
    """Check every agents/*.md and skills/*/SKILL.md under the loop plugin."""
    problems = []
    for agent in sorted((plugin_dir / "agents").glob("*.md")):
        problems += check_file(agent, agent.stem)
    for skill_dir in sorted(p for p in (plugin_dir / "skills").glob("*") if p.is_dir()):
        skill = skill_dir / "SKILL.md"
        if not skill.is_file():
            problems.append(f"{skill_dir}: missing SKILL.md")
            continue
        problems += check_file(skill, skill_dir.name)
    return problems
