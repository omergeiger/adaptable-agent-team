# personalized-feed

Daily, programmatically ranked feed of things to try (repos, papers with code, practitioner write-ups), one user profile per reader.

## Setup
```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

## Daily run
```
PYTHONPATH=src .venv/bin/python -m pfeed daily --user alex
```
Fetches live sources, ranks, writes `feeds/<YYYY-MM-DD>-NN.md` (+ `.json` sidecar) and appends to `profile/alex-delivered.md`
(the dedup ledger). The run report prints each chosen item's signals, total, matched interest and the relaxation rung used.

Trial runs that must not touch real state:
```
PYTHONPATH=src .venv/bin/python -m pfeed daily --user alex --out /tmp/trial --date 2026-11-19
```
`--out` redirects editions and (by default) the ledger to `/tmp/trial/ledger.md`.

## Other commands
- `python -m pfeed check-live` - ping every source once, print status (not part of pytest).
- `python -m pfeed feedback --user alex --edition feeds/2026-11-19-01.json --event "👍 1"` - adjust the user's signal weights.
  Trial-safe: add `--weights /tmp/trial/w.json` or `--root /tmp/trial`.

## Tests
```
PYTHONPATH=src .venv/bin/python -m pytest -q
```
All offline (fixtures in `tests/fixtures/`).

## Delivery
Slack delivery is not wired yet; the markdown file in `feeds/` is the canonical output. Design: `docs/ranking-design.md`, `docs/architecture.md`.
