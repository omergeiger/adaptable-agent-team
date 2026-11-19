---
name: test-gate
description: Test suite discipline - how to run the suite and what counts as green. Apply when the qa-engineer verifies a slice, when the tech-lead decides whether red tests block feature work, and when the developer changes dependencies.
---

# test-gate - Test Suite Discipline

**Audience: agent-applied (loop-plugin:test-gate).** Defines how the suite is run and what "green" means, so a slice is never declared done on unverified or broken tests.

## Protocol

1. All code and tests live under `projects/personalized-feed/`. Use the project venv:
   ```bash
   cd projects/personalized-feed
   python3 -m venv .venv            # first time only
   .venv/bin/pip install -r requirements.txt
   ```
2. Run the suite from the project root with the venv interpreter:
   ```bash
   .venv/bin/python -m pytest -q
   ```
3. **Green** = exit code 0, zero failures, zero errors. Anything else is **red**.
4. Record the exact command and the summary line (e.g. `28 passed in 4.1s`) in the QA report.
5. Network-dependent tests (live source fetch, Slack delivery) must be mockable and must also have an offline path; CI-style runs use mocks. Live-link validation is a separate, explicit check, not part of the unit suite.

## When to Apply

- qa-engineer runs this for every slice and reports green/red precisely.
- tech-lead treats a red suite as a blocker: new feature work is preempted until it is green again.
- developer ensures the suite stays runnable and adds/updates `requirements.txt` when dependencies change.
