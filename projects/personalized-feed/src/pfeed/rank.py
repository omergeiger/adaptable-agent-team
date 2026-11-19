"""Deterministic ranking + selection (docs/ranking-design.md, loop-plugin:relevance-rubric). No LLM, no I/O.

Pipeline: excludes -> score (5 signals, best single interest) -> constraint-aware greedy selection with
relaxation. Heuristic tables live in rank_data.py. Same inputs always give the same Selection.
"""
import json
import re
from datetime import date, datetime
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

from . import rank_data as D
from .ledger import cluster_key, name_key, repo_slug
from .models import Candidate


# ---------- data types ----------

@dataclass
class Scored:
    candidate: object
    signals: dict
    total: float
    interest: str = ""     # matched profile interest ("" = none)
    tier: str = ""         # high | mid | low | ""
    exploration: bool = False
    strong: bool = False   # strong interest match (see match_interest)
    matches: list = field(default_factory=list)  # [{"keyword", "origin": title|summary}] for audit


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
    """Whole-word match (an optional plural s is allowed): 'repo' must not fire on 'report'."""
    return any(re.search(r"\b" + re.escape(w) + r"s?\b", text) for w in words)


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
        if rule not in rules:
            continue
        if rule in D.EXCLUDE_WHOLE_WORD:
            hit = _has(text, words)
        else:
            hit = any(re.search(r"\b" + re.escape(w), text) for w in words)
        if hit:
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

def _kw_hit(keyword, text):
    """Stems match as prefixes; every other keyword is a whole word (optional plural s)."""
    tail = "" if keyword in D.STEM_KEYWORDS else r"s?\b"
    return re.search(r"\b" + re.escape(keyword) + tail, text) is not None


def _interest_hits(it_name, key, c, text):
    """Distinct keyword hits for one interest; ambiguous interests need context (e.g. rust needs an LLM/ML term)."""
    context = D.CONTEXT_REQUIRED.get(key)
    if context and c.item_type not in D.CONTEXT_EXEMPT_TYPES and not _has(text, context):
        return []
    return [k for k in D.INTEREST_KEYWORDS.get(key, []) if _kw_hit(k, text)]


def _match(c, profile):
    """Best single interest -> (name, tier, signal 0-5, strong, matches). Never sums rows; weight 0 is ineligible.

    Strong = a non-weak keyword in the title, or >= STRONG_HITS distinct hits with at least one non-weak. A weak-only
    or lone weak match is one tier lower. Confirmed low-weight interests have base 2 (rare, not never); inferred 1.
    HN/Lobsters items whose hits all come from the summary/body are capped at SUMMARY_ONLY_CAP (promotional text).
    """
    text, title = _text(c), c.title.lower()
    best = None
    for it in profile.interests:
        w = it.effective_weight
        if w <= 0:
            continue
        key = next((k for k in D.INTEREST_KEYWORDS if it.name.lower().startswith(k)), None)
        hits = _interest_hits(it.name, key, c, text)
        if not hits:
            continue
        low_base = 2 if it.status == "confirmed" else 1
        tier, base = ("high", 5) if w >= 4 else ("mid", 3) if w == 3 else ("low", low_base)
        strong_hits = [k for k in hits if k not in D.WEAK_KEYWORDS]
        strong = any(_kw_hit(k, title) for k in strong_hits) or (len(hits) >= D.STRONG_HITS and bool(strong_hits))
        signal = base if strong else max(base - 1, 1)
        matches = [{"keyword": k, "origin": "title" if _kw_hit(k, title) else "summary"} for k in hits]
        if c.source_type in D.SUMMARY_CAP_SOURCE_TYPES and all(m["origin"] == "summary" for m in matches):
            if not strong_hits:
                continue  # weak words in a promotional body prove nothing: no match, no credit
            signal = min(signal, D.SUMMARY_ONLY_CAP)
        rank_key = (base, len(hits), w)
        if best is None or rank_key > best[0]:
            best = (rank_key, it.name, tier, signal, strong, matches)
    return best[1:] if best else ("", "", 0, False, [])


def match_interest(c, profile):
    """(interest name, tier, signal 0-5); see _match for the rules."""
    return _match(c, profile)[:3]


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


def _traction_count(c):
    """Stars for repos; HN points for an HN-delivered repo; None when unknown."""
    stars = c.extras.get("stars")
    return stars if stars is not None else (c.extras.get("points") if c.item_type in ("repo", "tool") else None)


def _age_days(c, today):
    try:
        return (today - datetime.fromisoformat(c.extras["created_at"].replace("Z", "+00:00")).date()).days
    except (KeyError, TypeError, ValueError, AttributeError):
        return None


def source_quality(c, today=None):
    """Repos are rated on traction (stars / HN points), everything else on its source."""
    count = _traction_count(c) if c.item_type in ("repo", "tool") else None
    if count is not None:
        quality = next(q for floor, q in D.TRACTION_LADDER if count >= floor)
        age = _age_days(c, today or date.today())
        if age is not None and age <= D.VELOCITY_MAX_AGE_DAYS and count >= D.VELOCITY_MIN_STARS:
            quality = max(quality, D.VELOCITY_QUALITY)
        return quality
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


def fatigued_interests(ledger, profile):
    """Interests delivered in >= FATIGUE_MIN_HITS of the last FATIGUE_EDITIONS editions.

    The ledger stores titles only, so interests are re-derived from titles (an undercount, never an overcount).
    """
    editions = {}
    for date_, edition, url, _cluster, title in ledger.rows:
        c = Candidate(title, url, url, "", "", "article")
        interest = match_interest(c, profile)[0]
        editions.setdefault((date_, edition), set())
        if interest:
            editions[(date_, edition)].add(interest)
    recent = list(editions.values())[-D.FATIGUE_EDITIONS:]
    names = {i for hits in recent for i in hits}
    return {i for i in names if sum(i in hits for hits in recent) >= D.FATIGUE_MIN_HITS}


def score(c, profile, weights, recent, today=None, fatigued=frozenset()):
    interest, tier, match, strong, matches = _match(c, profile)
    dom = domain_key(c)
    novelty = 3 if dom and dom in recent else 5
    if interest in fatigued:
        novelty = min(novelty, D.FATIGUE_NOVELTY)
    signals = {"interest-match": match, "novelty": novelty,
               "hands-on": hands_on(c), "thought-leadership": thought_leadership(c),
               "source-quality": source_quality(c, today)}
    total = round(sum(weights[k] * signals[k] for k in signals), 4)
    return Scored(c, signals, total, interest, tier, strong=strong, matches=matches)


# ---------- selection ----------

def _order(pool):
    return sorted(pool, key=lambda s: (-s.total, s.candidate.title.lower(), s.candidate.canonical_url))


def top_interests(profile):
    ranked = sorted(profile.interests, key=lambda i: -i.effective_weight)
    return {i.name for i in ranked[:D.TOP_INTERESTS_FOR_EXPLORATION]}


def _is_tail_repo(s):
    c = s.candidate
    stars = c.extras.get("stars")
    return c.item_type == "repo" and stars is not None and stars < D.TAIL_REPO_STARS


def _fits(chosen, s, n, extra_cap, top=frozenset()):
    """Interest cap, top-3-combined cap, tail-repo cap, one per cluster, one per author/domain."""
    cap = max(1, int(D.INTEREST_CAP_FRACTION * n)) + extra_cap
    if s.interest and sum(x.interest == s.interest for x in chosen) >= cap:
        return False
    top_cap = max(1, int(D.TOP_INTEREST_CAP_FRACTION * n + 0.5)) + extra_cap
    if s.interest in top and sum(x.interest in top for x in chosen) >= top_cap:
        return False
    if _is_tail_repo(s) and sum(_is_tail_repo(x) for x in chosen) >= D.MAX_TAIL_REPOS:
        return False
    if any(cluster_key(x.candidate) == cluster_key(s.candidate) for x in chosen):
        return False
    dom = domain_key(s.candidate)
    return not (dom and any(domain_key(x.candidate) == dom for x in chosen))


def _types(chosen):
    return {x.candidate.source_type for x in chosen}


def _exploration_eligible(s):
    """Tryable things only: repo/tool, paper with linked code, or a tryable article not from a newsletter headline."""
    c = s.candidate
    if not s.strong or s.signals["interest-match"] < D.EXPLORATION_MIN_INTEREST_MATCH:
        return False
    if c.item_type in ("repo", "tool"):
        return True
    if c.item_type == "paper":
        return bool(c.extras.get("repo_links"))
    return (c.item_type == "article" and _tryable(c)
            and c.source_type not in D.EXPLORATION_EXCLUDED_SOURCE_TYPES)


def _exploration_pick(scored, profile, floor, n, extra_cap):
    top = top_interests(profile)
    inferred = {i.name for i in profile.interests if i.status == "inferred"}
    pool = [s for s in scored if s.interest and _exploration_eligible(s)
            and s.signals["hands-on"] >= max(D.EXPLORATION_MIN_HANDS_ON, floor)
            and s.interest not in top and s.interest not in inferred and _fits([], s, n, extra_cap, top)]
    return _order(pool)[0] if pool else None


def _attempt(scored, profile, n, floor, extra_cap, min_match=D.MIN_INTEREST_MATCH_MAIN):
    """One greedy pass at fixed constraints -> list of Scored, or None if n items with >=3 types are not reachable."""
    eligible = [s for s in scored if s.signals["hands-on"] >= floor and s.signals["interest-match"] >= min_match]
    chosen = []
    top = top_interests(profile)
    pick = _exploration_pick(eligible, profile, floor, n, extra_cap)
    for s in scored:
        s.exploration = False
    if pick:
        pick.exploration = True
        chosen.append(pick)
    for s in _order(eligible):
        if len(chosen) >= n:
            break
        if s.interest and s not in chosen and _fits(chosen, s, n, extra_cap, top):
            chosen.append(s)
    # D2 diversity: swap the lowest-scored duplicated-type, non-exploration item for the best missing-type candidate
    while len(_types(chosen)) < D.MIN_SOURCE_TYPES:
        swapped = False
        for cand in _order(s for s in eligible if s.interest and s not in chosen and s.candidate.source_type not in _types(chosen)):
            counts = {t: sum(x.candidate.source_type == t for x in chosen) for t in _types(chosen)}
            for out in reversed(_order(x for x in chosen if not x.exploration and counts[x.candidate.source_type] > 1)):
                rest = [x for x in chosen if x is not out]
                if _fits(rest, cand, n, extra_cap, top):
                    chosen = rest + [cand]
                    swapped = True
                    break
            if swapped:
                break
        if not swapped:
            break
    ok = len(chosen) >= n and len(_types(chosen)) >= D.MIN_SOURCE_TYPES
    return _order(chosen) if ok else None


M = D.MIN_INTEREST_MATCH_MAIN
RELAXATIONS = [  # (hands-on floor, n, extra per-interest cap, min interest-match, warning)
    (D.DEFAULT_HANDS_ON_FLOOR, D.TARGET_N, 0, M, ""),
    (1, D.TARGET_N, 0, M, "relaxed: hands-on floor lowered to 1"),
    (1, 4, 0, M, "relaxed: edition size lowered to 4"),
    (1, 3, 0, M, "relaxed: edition size lowered to 3"),
    (1, 3, 1, M, "relaxed: allowed a 2nd item for a capped interest"),
    (1, 3, 1, 1, "relaxed: interest-match floor lowered to 1 (weak matches allowed in main slots)"),
]


def zero_traction(c, backed):
    """A GitHub repo under MIN_REPO_STARS that no other candidate (paper, HN post...) points at."""
    return (c.source_type == "GitHub" and c.item_type == "repo" and c.extras.get("stars") is not None
            and c.extras["stars"] < D.MIN_REPO_STARS and cluster_key(c) not in backed)


def _traction_rank(c):
    """Clone-cluster winner order: most stars, then earliest created_at, then owner name (deterministic)."""
    return (-(_traction_count(c) or 0), c.extras.get("created_at") or "9999", repo_slug(c.canonical_url))


def drop_name_clones(kept, stats):
    """Same distinctive repo name under different owners is one cluster; only the best-ranked owner survives."""
    groups = {}
    for c in kept:
        nk = name_key(c)
        if nk:
            groups.setdefault(nk, []).append(c)
    losers = set()
    for group in groups.values():
        if len({cluster_key(c) for c in group}) > 1:
            win = cluster_key(min(group, key=_traction_rank))
            losers |= {id(c) for c in group if cluster_key(c) != win}
    stats["name_clone_dupes"] = len(losers)
    return [c for c in kept if id(c) not in losers]


def select(candidates, profile, weights, ledger, today=None):
    """Candidates -> Selection. Drops excludes, ledger repeats and same-day cluster duplicates, then ranks."""
    today = today or date.today()
    rules, warnings = active_exclude_rules(profile)
    counts = {}
    for c in candidates:
        counts[cluster_key(c)] = counts.get(cluster_key(c), 0) + 1
    backed = {k for k, n in counts.items() if n > 1}
    stats = {"candidates": len(candidates), "excluded": {}, "ledger_seen": 0, "same_day_dupes": 0,
             "name_clone_dupes": 0}
    kept = []
    for c in candidates:
        reason = exclude_reason(c, rules) or ("zero-traction repo" if zero_traction(c, backed) else None)
        if reason:
            stats["excluded"][reason] = stats["excluded"].get(reason, 0) + 1
        elif ledger.seen(c):
            stats["ledger_seen"] += 1
        else:
            kept.append(c)
    kept = drop_name_clones(kept, stats)
    recent, fatigued = recent_domains(ledger), fatigued_interests(ledger, profile)
    stats["fatigued"] = sorted(fatigued)
    scored, best = [], {}
    for s in _order(score(c, profile, weights, recent, today, fatigued) for c in kept):
        key = cluster_key(s.candidate)
        if key in best:
            stats["same_day_dupes"] += 1
        else:
            best[key] = s
            scored.append(s)
    stats["scored"] = len(scored)
    for rung, (floor, n, extra, min_match, note) in enumerate(RELAXATIONS):
        chosen = _attempt(scored, profile, n, floor, extra, min_match)
        if chosen:
            stats["rung"] = rung
            if note:
                warnings.append(note)
            if not any(s.exploration for s in chosen):
                warnings.append("no exploration (Broadening pick) candidate met the bar; shipped without one")
            return Selection(chosen, warnings, stats)
        if note:
            warnings.append(note + " - still unsatisfiable")
    stats["rung"] = None
    warnings.append("ALARM: cannot assemble >= 3 items across >= 3 source types; shipping nothing")
    return Selection([], warnings, stats)
