# QA gate: Slice 1 (ingestion adapters + dedup ledger) - cycle 2

Verdict: APPROVE (with one non-blocking defect, QA-1)

Suite: `cd projects/personalized-feed && .venv/bin/python -m pytest -q` -> `71 passed, 3 xfailed in 0.07s` (exit 0). Developer's baseline was 63 passed; QA added 11 (8 pass, 3 xfail documenting QA-1).

## Acceptance criteria
1. Suite green: PASS.
2. Fake http, fixtures for S1/S3/S5/S7/blog/Substack/Atom, no network in pytest: PASS (FakeHttp everywhere; fixtures verified as real captures, arXiv hrefs https).
3. Fields + malformed skipped: PASS (test_malformed_entries..., rss skip tests, assert_valid).
4. Fail-soft + one retry w/ fake sleep: PASS (test_http retry/429/500/timeout, test_runner isolation). Caveat QA-1.
5. arXiv drops no-repo, GitHub drops awesome-*: PASS (QA also checked awesome_/awesomeness: only awesome[-_]/exact dropped, intended).
6. canonical_url cases: PASS.
7. cluster_key cases: PASS.
8. Ledger round-trip, seen by url or cluster, markdown header, create-on-missing, no-append unchanged: PASS.
9. check-live run once by QA (not gate): 33/33 sources ok, 1946 candidates {GitHub 248, HN 179, Lobsters 75, arXiv 25, blog 1339, Substack 60, Medium 20}. All 7 source types observed live.
10. Only pytest dep, UA personalized-feed/0.1, no secrets: PASS (grep clean).

## Defects
- QA-1 (low/medium): GitHub/HN adapters index `["items"]`/`["hits"]` inside try, but a JSON `null` value iterates outside it, raising TypeError (not FetchError). run_sources only catches FetchError, so one source returning `{"items": null}` aborts the whole run. Violates criterion 4 intent. Fix: validate isinstance list inside the try. Regression: tests/test_qa_exploratory.py (xfail strict; flips to failure when fixed, then remove the marker).

## Observations (not defects)
- HN stories with http:// targets are silently dropped (https-only rule); minor recall loss.
- A truncated/hand-edited ledger row is silently skipped on load, so that item could resurface (D7 risk is small; consider a warning).
- ledger_path does not sanitize user_id ("../x"); fine for single-user, harden before multi-user.
- XML entity expansion not guarded (stdlib ET); sources are trusted public feeds, low risk.
- Percent-encoding, mobile hosts (m.), tracking params like fbclid/si are not canonicalized; may leak minor duplicates.

## Next
Slice 2 may proceed. Ask developer to fix QA-1 early in slice 2 (remove xfail).
