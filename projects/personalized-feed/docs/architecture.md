# Architecture - personalized-feed

Status: draft (cycle 2). Owner: tech-lead. Majestic monolith: one small Python package, stdlib only, files on disk, one entry point.

## Shape

```
projects/personalized-feed/
  pfeed/                  # the package (stdlib only; no deps beyond pytest)
    adapters/             # one module per source family: github.py hn.py lobsters.py arxiv.py rss.py hfpapers.py
    http.py               # fetch(url): UA "personalized-feed/0.1", 15s timeout, 1 retry w/ backoff, ETag cache, injectable opener
    models.py             # Candidate dataclass
    profile.py            # parse profile/<user>.md -> Profile
    ledger.py             # dedup ledger (profile/<user>-delivered.md)
    rank.py               # scoring + selection (see ranking-design.md)
    feedback.py           # D6 capture -> weights + profile engagement log
    render.py             # Selection -> feeds/<YYYY-MM-DD>-NN.md
    pipeline.py           # run_daily(user_id, today) ; CLI: python -m pfeed daily --user alex
  sources/                # catalog + sources.yaml-free config: SOURCES list lives in adapters/__init__.py
  profile/                # <user>.md, <user>-delivered.md, <user>-weights.json
  feeds/                  # output editions
  tests/                  # pytest, offline, fixtures in tests/fixtures/
  requirements.txt        # pytest only
```

Why this shape: no DB (ledger and profile are markdown the human can read and git can diff), no queue, no framework, no config language. Adding a source = adding one function.

## Candidate (the only shared type)

`Candidate(title, url, canonical_url, source, source_type, item_type, summary, published, extras)`
- `source_type` in {GitHub, HN, Lobsters, arXiv, blog, Medium, Substack} - what D2 counts. Collapse for D2: HF Papers counts as `arXiv/papers`; all personal/company/Substack blogs count as `blog` unless Medium (kept separate).
- `item_type` in {repo, article, discussion, paper, tool} - matches feed-item-format.
- `extras`: stars, points, comment count, repo links found in text, etc. Used by ranking heuristics.

## Ingestion adapters

- Contract: `fetch(http) -> list[Candidate]`. Pure function of an injected `http` object, so tests pass a fake returning fixture bytes. No adapter touches disk or the ledger.
- Parsing: `urllib.request`, `json`, `xml.etree.ElementTree` (RSS 2.0 and Atom both handled by one `rss.py` with a feed-URL list from the catalog).
- Official APIs/RSS only (D8/reader-source 2): GitHub search API (S1), HN Algolia (S3), lobste.rs RSS (S5), arXiv API with `abs:github` filter (S7), HF daily_papers (S7c, fragile, optional), blog/Substack/Medium RSS (S8-S17). Do NOT implement: GitHub trending HTML (S2), Reddit (S6 blocked), Papers with Code (blocked).
- Fail-soft: each adapter is called in try/except by the pipeline; failure -> logged in the run report, zero items from that source, never fabricated. arXiv: 1 req / 3 s. GitHub search: at most 10-15 queries per run.
- Pre-rank filters live in adapters only when source-specific (reject awesome-lists, arXiv without a repo link, HN story with < N points). Interest/exclude logic is NOT in adapters; it is in rank.py.

## Profile (D5)

- `profile.py` parses the markdown tables of `profile/<user_id>.md` per `loop-plugin:profile-schema`. Everything is keyed by `user_id`; nothing in code names Alex. A second user = a second profile file + ledger, and `--user` flag.
- Output `Profile(interests[(name, weight, status)], excludes, preferred_sources, form_pref)`. Parser is strict: unknown table shape raises, pipeline aborts with a clear message rather than ranking blind.
- Per-user mutable numeric state (rubric signal weights) lives in `profile/<user_id>-weights.json` (defaults from the rubric if absent). Markdown stays the human-facing truth; JSON holds only the 5 floats and the adjustment log.

## Dedup ledger (D7)

- File `profile/<user_id>-delivered.md`: a markdown table `date | edition | canonical_url | cluster_key | title`. Append-only, written only after the edition file is successfully written (so a crash cannot burn items).
- `canonical_url(url)`: lowercase host, strip `www.`, drop fragment and tracking params (`utm_*`, `ref`, `source`), strip trailing slash, `http`->`https`. Resolve cross-source overlap: a HN/lobste.rs story whose target URL is a GitHub repo, arXiv paper, or blog post canonicalizes to the TARGET URL, so the same thing arriving via HN and via GitHub is one item.
- `cluster_key(c)`: `gh:<owner>/<repo>` for repo URLs (and links extracted from text), `arxiv:<id>` (version stripped), else the canonical URL. This gives "project/topic cluster" dedup required by the critic guardrail beyond exact URL. Same-day dedup uses the same function within the candidate set (keep best-scored per cluster).
- `Ledger.seen(candidate) -> bool` checks canonical_url OR cluster_key. Never repeats an item across editions (D7). Re-delivery of a repo only if a deliberate "new release" rule is added later (not now; you do not need it).

## Ranking (summary; detail in ranking-design.md)

rank.py takes candidates + Profile + weights + ledger, returns a `Selection` of 3-5 items with per-signal scores, weighted total, matched interest, and an `exploration` flag. Pure and deterministic.

## Feedback capture (D6)

- Input forms: `👍 #n`, `👎 #n`, `more #n`, `less #n` (also free text "more like #2 / less like #4" parsed by regex) against a given edition file.
- Each edition has a sidecar `feeds/<YYYY-MM-DD>-NN.json` (machine copy of the Selection: item #, url, signals, matched interest) so feedback needs no parsing of markdown.
- `feedback.apply(user, edition, events)`: (a) adjusts the five signal weights per the rubric (+/-0.05 on signals scoring >=4 on that item, renormalize to 1.0, clamp each to [0.05, 0.50]); (b) appends a line to the profile's Engagement history with the `real` or `simulated` tag; (c) for 👎/less, appends an interest-demotion flag to the engagement line for user-profiler (code never edits interest weights itself); (d) appends to the adjustment log in `<user>-weights.json`. Simulated events never promote inferred interests (guardrail, D9).
- CLI: `python -m pfeed feedback --user alex --edition feeds/2026-11-19-01.md --event "👍 1" --event "more 3" [--simulated]`.

## Markdown edition renderer

- `render.py` emits exactly the `loop-plugin:feed-item-format` template: header, 3-5 items with Source/Link/Type/Why/Relevance signals line, feedback footer. NN = next free edition number for that date. The exploration item's Why line starts with "Broadening pick:" (see ranking-design.md).
- "Why it's worth investigating" is template-composed from the matched interest + the item's hands-on hook (e.g. "Repo with N stars, pushed <date>; ties to your agent-frameworks interest - clone and try the quickstart."). The LLM-written polish pass is an optional later step by an agent, not part of the code path. Code must never emit an item without link or why-line; renderer asserts it.
- Slack push is out of scope (D4); the renderer is the single output seam, so adding Slack later = another function over the same Selection.

## Daily Feed pipeline entry point

`python -m pfeed daily --user alex [--date YYYY-MM-DD] [--offline FIXTURE_DIR]`

1. load profile + weights + ledger
2. run all adapters (fail-soft), collect candidates
3. drop excludes (observable tests), same-day dedup by cluster, drop ledger hits
4. rank, select 3-5 with caps/diversity/exploration
5. gate checks inside the pipeline (3-5 items, >= 3 source types, links present, no ledger repeats); if impossible, relax in documented order (see ranking-design) and print a WARNING in the run report instead of shipping a bad feed silently
6. render markdown + JSON sidecar, then append to ledger
7. print run report: sources ok/failed, candidate counts at each stage, selection with scores

Idempotence: running twice the same day makes edition 02, and the ledger prevents repeats.

## Testing

Per `loop-plugin:test-gate`: `.venv/bin/python -m pytest -q` from the project root. All unit tests offline (fake `http`, fixtures captured from the verified endpoints). Live checks are a separate explicit script `python -m pfeed check-live`, not in pytest.

## Roadmap (slices, one concern each)

1. Ingestion adapters + http + Candidate + dedup ledger (this cycle's pick; acceptance in ranking-design.md end section / by-product note)
2. Profile parser + ranking/selection to the rubric and guardrails
3. Renderer + pipeline entry point + first real edition (offline then live)
4. Feedback capture + weight adjustment + simulated reactions for edition 1
5. Hardening from QA/critic findings; optional HF Papers adapter, Medium publication feeds

## Rulings
- Markdown ledger over SQLite: human-readable, git-diffable, tiny volume. Revisit only past ~10k rows.
- No LLM calls in the code path: ranking is deterministic and testable; judgment lives in ranking-engineer's reviews that tune the spec.
- Skip GitHub trending HTML and Reddit: scraping/ToS (D8). You do not need them.
