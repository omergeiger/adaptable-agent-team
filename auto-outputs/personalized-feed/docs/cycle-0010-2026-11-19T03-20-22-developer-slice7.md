# Cycle 10 - developer - Slice 7

Changes (projects/personalized-feed/src/pfeed):
- rank_data.py: GENERIC_KEYWORDS {agent, agents, agentic, llm, ai}, LONE_GENERIC_CAP=2; EXPLORATION_MIN_INTEREST_MATCH 3 -> 2.
- rank.py `_match`: hits made only of generic words -> signal <= 2, never strong (even a title hit). A second distinct non-generic hit backs it up (unchanged path).
- rank.py `_match`: best-interest choice now keys on the effective signal first. Found by test: "Agent tracing with opentelemetry" was assigned the top-weight "agent frameworks" interest (weak) instead of observability (strong).
- render.py `_cited`: why-lines never cite WEAK or GENERIC keywords.
- rank.py: hands-on-floor warning now "relaxed: hands-on floor lowered to 1 (some items are less tryable than usual)".

Finding (item 2): the exploration slot could NOT carry rust/AI safety. Confirmed low-weight interests max at signal 2, but exploration needed >= 3, and `_attempt` pre-filtered the exploration pool by MIN_INTEREST_MATCH_MAIN. Fixed: exploration pool is hands-on-floor filtered only, and needs strong + signal >= 2. Main slots still need >= 3. Consequence: an exploration item may ship with interest-match 2 (by design). Needs ranking-engineer/critic sign-off (rank rule change).

Tests: tests/test_slice7_generic_keywords.py (7 cases). Suite: 219 passed.
