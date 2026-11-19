"""Deterministic ranking + selection (docs/ranking-design.md, loop-plugin:relevance-rubric). No LLM, no I/O.

Pipeline: excludes -> score (5 signals, best single interest) -> constraint-aware greedy selection with
relaxation. Heuristic tables live in rank_data.py. Same inputs always give the same Selection.
"""
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

from . import rank_data as D
from .ledger import cluster_key


# ---------- data types ----------

@dataclass
class Scored:
    candidate: object
    signals: dict
    total: float
    interest: str = ""     # matched profile interest ("" = none)
    tier: str = ""         # high | mid | low | ""
    exploration: bool = False


@dataclass
class Selection:
    items: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    stats: dict = field(default_factory=dict)


# ---------- weights ----------

def weights_path(root, user_id):
    return Path(root) / "profile" / f"{user_id}-weights.json"


def load_weights(root, user_id):
    """Per-user signal weights (D5/D6); defaults if the file is absent."""
    path = weights_path(root, user_id)
    if path.exists():
        return dict(json.loads(path.read_text(encoding="utf-8"))["weights"])
    return dict(D.DEFAULT_WEIGHTS)


# ---------- excludes ----------

def active_exclude_rules(profile):
    """Map the profile's Anti-interests text to rule names; unknown text is warned about, never silent."""
    rules, warnings = set(), []
    for text in profile.excludes:
        low = text.lower()
        hit = {rule for key, rule in D.EXCLUDE_RULE_FOR_TEXT.items() if key in low}
        if hit:
            rules |= hit
        else:
            warnings.append(f"exclude not mapped to an observable rule (ignored): {text!r}")
    return rules, warnings


def _text(c):
    return f"{c.title} {c.summary} {' '.join(c.extras.get('topics') or [])}".lower()


def _has(text, words):
    return any(w in text for w in words)


def _tryable(c):
    return bool(c.extras.get("repo_links")) or _has(_text(c), D.TRYABLE_WORDS)


def exclude_reason(c, rules):
    """Reason string if the candidate is hard-dropped, else None. Observable tests only."""
    text = _text(c)
    if c.item_type == "repo" and re.match(r"^awesome([-_]|$)", c.title.split("/")[-1], re.I):
        return "awesome-list"
    if c.item_type == "paper" and not (c.extras.get("repo_links") or "github.com/" in text):
        return "paper without code"
    for rule, words in D.EXCLUDE_KEYWORDS.items():
        if rule in rules and any(re.search(r"\b" + re.escape(w), text) for w in words):
            return rule
    if "listicle" in rules and re.match(D.LISTICLE_RE, c.title.strip(), re.I):
        return "listicle"
    if "announcement" in rules and c.item_type == "article" and not _tryable(c) \
            and _has(text, D.ANNOUNCEMENT_WORDS):
        return "announcement with nothing to try"
    if "vendor-cta" in rules and c.source in D.VENDOR_SOURCES and _has(text, D.CTA_WORDS):
        return "vendor post with product CTA"
    return None


# ---------- signals ----------

def match_interest(c, profile):
    """Best single matching interest -> (name, tier, signal 0-5). Never sums rows; weight 0 is ineligible."""
    text, title = _text(c), c.title.lower()
    best = None
    for it in profile.interests:
        w = it.effective_weight
        if w <= 0:
            continue
        key = next((k for k in D.INTEREST_KEYWORDS if it.name.lower().startswith(k)), None)
        hits = [k for k in D.INTEREST_KEYWORDS.get(key, []) if re.search(r"\b" + re.escape(k), text)]
        if not hits:
            continue
        tier, base = ("high", 5) if w >= 4 else ("mid", 3) if w == 3 else ("low", 1)
        strong = len(hits) >= D.STRONG_HITS or any(re.search(r"\b" + re.escape(k), title) for k in hits)
        rank_key = (base, len(hits), w)
        if best is None or rank_key > best[0]:
            best = (rank_key, it.name, tier, base if strong else max(base - 1, 1))
    return (best[1], best[2], best[3]) if best else ("", "", 0)


def hands_on(c):
    text = _text(c)
    if c.item_type == "paper":
        return D.HANDS_ON_PAPER_WITH_REPO if c.extras.get("repo_links") or "github.com/" in text else 1
    if c.item_type == "article" and _tryable(c):
        return D.HANDS_ON_TRYABLE_ARTICLE
    if c.item_type == "discussion":
        need, score = D.HANDS_ON_DISCUSSION_MANY_COMMENTS
        return score if (c.extras.get("comments") or 0) >= need else D.HANDS_ON_BY_ITEM_TYPE["discussion"]
    return D.HANDS_ON_BY_ITEM_TYPE.get(c.item_type, 2)


def domain_key(c):
    """Author/domain identity for the one-per-author cap: GitHub owner or host; None for aggregator discussions."""
    parts = urlsplit(c.canonical_url)
    host = parts.hostname or ""
    if host in D.AGGREGATOR_HOSTS:
        return None
    if host == "github.com":
        segs = [s for s in parts.path.split("/") if s]
        return f"github.com/{segs[0]}" if segs else host
    return host


def recent_domains(ledger, n_editions=D.NOVELTY_RECENT_EDITIONS):
    editions = []
    for row in ledger.rows:
        key = (row[0], row[1])
        if key not in editions:
            editions.append(key)
    recent = set(editions[-n_editions:])
    out = set()
    for date, edition, url, _cluster, _title in ledger.rows:
        if (date, edition) in recent:
            host = urlsplit(url).hostname or ""
            if host in D.AGGREGATOR_HOSTS:
                continue
            segs = [s for s in urlsplit(url).path.split("/") if s]
            out.add(f"github.com/{segs[0]}" if host == "github.com" and segs else host)
    return out


def source_quality(c):
    for name, score in D.SOURCE_QUALITY_BY_SOURCE.items():
        if c.source.startswith(name):
            return score
    return D.SOURCE_QUALITY_BY_TYPE.get(c.source_type, 1)


def thought_leadership(c):
    who = f"{c.source} {c.extras.get('author') or ''}".lower()
    if any(n.lower() in who for n in D.NOTABLE_AUTHORS):
        return 5
    if (c.extras.get("stars") or 0) >= D.NOTABLE_REPO_STARS:
        return 3
    return 1


def score(c, profile, weights, recent):
    interest, tier, match = match_interest(c, profile)
    dom = domain_key(c)
    signals = {"interest-match": match, "novelty": 3 if dom and dom in recent else 5,
               "hands-on": hands_on(c), "thought-leadership": thought_leadership(c),
               "source-quality": source_quality(c)}
    total = round(sum(weights[k] * signals[k] for k in signals), 4)
    return Scored(c, signals, total, interest, tier)


# ---------- selection ----------

def _order(pool):
    return sorted(pool, key=lambda s: (-s.total, s.candidate.title.lower(), s.candidate.canonical_url))


def _fits(chosen, s, n, extra_cap):
    """Interest cap, one per cluster, one per author/domain."""
    cap = max(1, int(D.INTEREST_CAP_FRACTION * n)) + extra_cap
    if s.interest and sum(x.interest == s.interest for x in chosen) >= cap:
        return False
    if any(cluster_key(x.candidate) == cluster_key(s.candidate) for x in chosen):
        return False
    dom = domain_key(s.candidate)
    return not (dom and any(domain_key(x.candidate) == dom for x in chosen))


def _types(chosen):
    return {x.candidate.source_type for x in chosen}


def _exploration_pick(scored, profile, floor):
    top = {i.name for i in sorted(profile.interests, key=lambda i: -i.effective_weight)[:D.TOP_INTERESTS_FOR_EXPLORATION]}
    inferred = {i.name for i in profile.interests if i.status == "inferred"}
    pool = [s for s in scored if s.signals["hands-on"] >= max(D.EXPLORATION_MIN_HANDS_ON, floor)
            and s.interest not in top and s.interest not in inferred]
    return _order(pool)[0] if pool else None


def _attempt(scored, profile, n, floor, extra_cap):
    """One greedy pass at fixed constraints -> list of Scored, or None if n items with >=3 types are not reachable."""
    eligible = [s for s in scored if s.signals["hands-on"] >= floor]
    chosen = []
    pick = _exploration_pick(eligible, profile, floor)
    for s in scored:
        s.exploration = False
    if pick:
        pick.exploration = True
        chosen.append(pick)
    for s in _order(eligible):
        if len(chosen) >= n:
            break
        if s.interest and s not in chosen and _fits(chosen, s, n, extra_cap):
            chosen.append(s)
    # D2 diversity: swap the lowest-scored duplicated-type, non-exploration item for the best missing-type candidate
    while len(_types(chosen)) < D.MIN_SOURCE_TYPES:
        swapped = False
        for cand in _order(s for s in eligible if s.interest and s not in chosen and s.candidate.source_type not in _types(chosen)):
            counts = {t: sum(x.candidate.source_type == t for x in chosen) for t in _types(chosen)}
            for out in reversed(_order(x for x in chosen if not x.exploration and counts[x.candidate.source_type] > 1)):
                rest = [x for x in chosen if x is not out]
                if _fits(rest, cand, n, extra_cap):
                    chosen = rest + [cand]
                    swapped = True
                    break
            if swapped:
                break
        if not swapped:
            break
    ok = len(chosen) >= n and len(_types(chosen)) >= D.MIN_SOURCE_TYPES
    return _order(chosen) if ok else None


RELAXATIONS = [  # (hands-on floor, n, extra per-interest cap, warning)
    (D.DEFAULT_HANDS_ON_FLOOR, D.TARGET_N, 0, ""),
    (1, D.TARGET_N, 0, "relaxed: hands-on floor lowered to 1"),
    (1, 4, 0, "relaxed: edition size lowered to 4"),
    (1, 3, 0, "relaxed: edition size lowered to 3"),
    (1, 3, 1, "relaxed: allowed a 2nd item for a capped interest"),
]


def select(candidates, profile, weights, ledger):
    """Candidates -> Selection. Drops excludes, ledger repeats and same-day cluster duplicates, then ranks."""
    rules, warnings = active_exclude_rules(profile)
    stats = {"candidates": len(candidates), "excluded": {}, "ledger_seen": 0, "same_day_dupes": 0}
    kept = []
    for c in candidates:
        reason = exclude_reason(c, rules)
        if reason:
            stats["excluded"][reason] = stats["excluded"].get(reason, 0) + 1
        elif ledger.seen(c):
            stats["ledger_seen"] += 1
        else:
            kept.append(c)
    recent = recent_domains(ledger)
    scored, best = [], {}
    for s in _order(score(c, profile, weights, recent) for c in kept):
        key = cluster_key(s.candidate)
        if key in best:
            stats["same_day_dupes"] += 1
        else:
            best[key] = s
            scored.append(s)
    stats["scored"] = len(scored)
    for floor, n, extra, note in RELAXATIONS:
        chosen = _attempt(scored, profile, n, floor, extra)
        if chosen:
            if note:
                warnings.append(note)
            if not any(s.exploration for s in chosen):
                warnings.append("no exploration (Broadening pick) candidate met the bar; shipped without one")
            return Selection(chosen, warnings, stats)
        if note:
            warnings.append(note + " - still unsatisfiable")
    warnings.append("ALARM: cannot assemble >= 3 items across >= 3 source types; shipping nothing")
    return Selection([], warnings, stats)
