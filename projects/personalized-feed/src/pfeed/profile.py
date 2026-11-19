"""Parse profile/<user_id>.md (loop-plugin:profile-schema) into a Profile. Strict: a malformed table raises."""
import re
from dataclasses import dataclass, field
from pathlib import Path

INFERRED_WEIGHT_CAP = 2  # ranking-design: inferred interests are capped until confirmed by engagement


class ProfileError(Exception):
    pass


@dataclass
class Interest:
    name: str
    weight: int      # as written in the profile
    status: str      # confirmed | inferred
    notes: str = ""

    @property
    def effective_weight(self):
        return min(self.weight, INFERRED_WEIGHT_CAP) if self.status == "inferred" else self.weight


@dataclass
class Profile:
    user_id: str
    interests: list = field(default_factory=list)
    excludes: list = field(default_factory=list)
    preferred_sources: list = field(default_factory=list)


def profile_path(root, user_id):
    return Path(root) / "profile" / f"{user_id}.md"


def _section(text, heading):
    m = re.search(rf"^##\s+{re.escape(heading)}.*?\n(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def _bullets(block):
    return [re.sub(r"\s*\(.*?\)\s*$", "", b).strip() for b in re.findall(r"^-\s+(.+)$", block, re.M)]


def parse_profile(text, user_id):
    block = _section(text, "Interests")
    rows = [[c.strip() for c in line.strip().strip("|").split("|")] for line in block.splitlines() if line.startswith("|")]
    rows = [r for r in rows if r and not set(r[0]) <= {"-", ":", " "}][1:]  # drop header and separator
    if not rows:
        raise ProfileError(f"{user_id}: no interests table found")
    interests = []
    for r in rows:
        if len(r) != 4 or not r[1].isdigit() or r[2] not in ("confirmed", "inferred"):
            raise ProfileError(f"{user_id}: malformed interest row {r!r}")
        interests.append(Interest(r[0], int(r[1]), r[2], r[3]))
    return Profile(user_id, interests, _bullets(_section(text, "Anti-interests")),
                   _bullets(_section(text, "Preferred sources")))


def load_profile(root, user_id):
    path = profile_path(root, user_id)
    if not path.exists():
        raise ProfileError(f"no profile for user {user_id!r} at {path}")
    return parse_profile(path.read_text(encoding="utf-8"), user_id)
