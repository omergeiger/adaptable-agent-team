# Slice 1 build - ingestion adapters + dedup ledger (developer, cycle 2)

Result: `cd projects/personalized-feed && .venv/bin/python -m pytest -q` -> 63 passed in 0.05s (offline).
Live: `PYTHONPATH=src .venv/bin/python -m pfeed check-live` -> 33/33 sources OK, 1946 candidates (GitHub 248, HN 179, Lobsters 75, arXiv 25, blog 1339, Substack 60, Medium 20); exit 0, ~70 s (GitHub/arXiv politeness delays).

## Files (all under projects/personalized-feed/)
- src/pfeed/{__init__,__main__,models,http,ledger}.py, src/pfeed/adapters/{__init__,github,hn,lobsters,arxiv,hfpapers,rss}.py
- tests/{conftest,adapters_helpers,test_http,test_ledger,test_adapters,test_runner}.py, tests/fixtures/* (trimmed real captures from the catalog endpoints, 2026-11-19)
- pytest.ini (pythonpath=src, testpaths=tests), requirements.txt (pytest), .venv created

## Deviations / decisions
1. Package at src/pfeed/ (per cycle instruction), not pfeed/ as drawn in architecture.md. Run CLI with PYTHONPATH=src.
2. .venv did not exist in the project and the repo-root venv has no pytest; created projects/personalized-feed/.venv and installed pytest only (per test-gate).
3. Candidates with a non-https URL are skipped (criterion 3 says https url; we never rewrite links). Some legacy http-only HN/blog links are therefore lost.
4. Adapters raise FetchError; fail-soft lives in `run_sources` (records per-source SourceReport, others continue).
5. Per-host politeness built into Http (arXiv 3 s, api.github.com 6 s) via injectable clock/sleep.
6. cluster_key: only papers (arXiv/HF) cluster with a repo they link; blog posts that mention repos do not (avoids merging link round-ups with repos). Version-stripped arXiv URLs canonicalize to /abs/<id>.
7. HF Daily Papers (optional) implemented; keeps only papers with githubRepo; source_type arXiv.
8. HN: Ask HN/no-target posts become item_type discussion with the HN URL; others take the target's type (repo/paper/article). MIN_POINTS=10 filter in adapter. No recency window yet (search_by_date order only).
9. ETag cache is in-memory per Http instance (no disk persistence yet).

## For slice 2 (ranking)
- Full-archive feeds return many old items (Hugging Face blog 913, Eugene Yan 214, LangChain 99): rank/pipeline needs a recency filter on `Candidate.published` (ISO string, may be empty).
- GitHub search results are stars-sorted over created-in-7-days; stars can be hype - already noted in catalog.
- Tests were written together with the code in one pass, not strictly red-first; three tests failed on first run and drove fixes (pipe-escaping in ledger, HTML root check in arXiv adapter, truncated-tag cleanup).
