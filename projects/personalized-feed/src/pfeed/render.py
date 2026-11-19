"""Selection -> markdown edition exactly per loop-plugin:feed-item-format, plus the JSON sidecar (D6).

Why-lines are template-composed from real fields only; a number appears only if the source supplied it.
"""
import json
import re
from pathlib import Path

from .ledger import cluster_key

FOOTER = '---\n_Feedback: reply 👍/👎 per item, or "more like #2 / less like #4" to tune future feeds._\n'
HOOKS = {"repo": "clone it and run the quickstart", "paper": "skim the abstract, then run the linked repo",
         "discussion": "read the thread for practitioners' notes", "article": "follow the write-up and try the steps",
         "tool": "install it and try it on one of your own cases"}


def next_edition(out_dir, date):
    taken = [int(m.group(1)) for p in Path(out_dir).glob(f"{date}-*.md")
             if (m := re.fullmatch(rf"{re.escape(str(date))}-(\d\d)\.md", p.name))]
    return max(taken, default=0) + 1


def _facts(c):
    x, bits = c.extras, []
    if x.get("stars") is not None:
        bits.append(f"{x['stars']} stars")
    if x.get("pushed_at"):
        bits.append(f"pushed {x['pushed_at'][:10]}")
    if x.get("points") is not None:
        bits.append(f"{x['points']} points" + (f", {x['comments']} comments" if x.get("comments") is not None else ""))
    if x.get("upvotes") is not None:
        bits.append(f"{x['upvotes']} upvotes")
    return ", ".join(bits)


def why_line(s):
    c = s.candidate
    kind = {"repo": "Repo", "paper": "Paper with code", "discussion": "Discussion", "article": "Write-up",
            "tool": "Tool"}[c.item_type]
    facts = _facts(c)
    head = f"{kind} from {c.source}" + (f" ({facts})" if facts else "")
    if s.exploration:
        return (f"Broadening pick: {head}, outside your usual top interests"
                + (f" but touching {s.interest}" if s.interest else "") + f" - {HOOKS[c.item_type]}.")
    tie = f"ties to your {s.interest} interest"
    return f"{head}; {tie} - {HOOKS[c.item_type]}."


def render_edition(selection, user_id, date):
    items = selection.items
    assert 3 <= len(items) <= 5, f"edition must have 3-5 items, got {len(items)}"
    types = []
    for s in items:
        if s.candidate.source_type not in types:
            types.append(s.candidate.source_type)
    assert len(types) >= 3, f"edition must span >= 3 source types, got {types}"
    lines = [f"# Personalized Feed - {date}",
             f"**User:** {user_id} · **Items:** {len(items)} · **Source types:** {', '.join(types)}", ""]
    for n, s in enumerate(items, 1):
        c = s.candidate
        why = why_line(s)
        assert c.url.startswith("https://") and why, "item needs a real link and a why-line"
        sig = s.signals
        lines += [f"## {n}. {c.title}",
                  f"- **Source:** {c.source_type} · **Link:** {c.url}",
                  f"- **Type:** {c.item_type}",
                  f"- **Why it's worth investigating:** {why}",
                  "- **Relevance signals:** " + " · ".join(f"{k} {sig[k]}" for k in
                                                           ("interest-match", "novelty", "source-quality", "hands-on", "thought-leadership")),
                  ""]
    return "\n".join(lines) + "\n" + FOOTER


def sidecar(selection, user_id, date, edition, weights):
    return {"user": user_id, "date": str(date), "edition": edition, "weights": weights,
            "warnings": selection.warnings,
            "items": [{"n": n, "title": s.candidate.title, "url": s.candidate.url,
                       "canonical_url": s.candidate.canonical_url, "cluster_key": cluster_key(s.candidate),
                       "source_type": s.candidate.source_type, "item_type": s.candidate.item_type,
                       "signals": s.signals, "total": s.total, "interest": s.interest, "tier": s.tier,
                       "exploration": s.exploration} for n, s in enumerate(selection.items, 1)]}


def write_edition(selection, user_id, date, weights, out_dir):
    """Write NN.md and NN.json; returns (md_path, edition_number). Ledger append is the caller's job, after this."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    edition = next_edition(out_dir, date)
    stem = out_dir / f"{date}-{edition:02d}"
    md = render_edition(selection, user_id, date)  # asserts before anything is written
    stem.with_suffix(".json").write_text(json.dumps(sidecar(selection, user_id, date, edition, weights), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    stem.with_suffix(".md").write_text(md, encoding="utf-8")
    return stem.with_suffix(".md"), edition
