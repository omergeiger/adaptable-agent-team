# AgentTeam - Example Adaptation Cases

Ten worked examples of adapting the framework to a domain. Each case is a complete prescription: a Claude instance should be able to take any case, run (or simulate) the /adapt wizard with the answers given here, generate the listed agents/skills/prompt rules, and verify the loop end-to-end against the acceptance criteria.

**How to use a case as an end-to-end test:**
1. Run the /adapt wizard interactively. Map the case's fields to the wizard questions: "Adapt answers" supplies project name, domain/purpose, roles, phases, output, and cadence (questions 1-6); the case's "Skills" list answers the conventions question (7); the case's "human_directives.md starters" answer the standing-directives question (8).
2. Confirm adapt generated: one worker agent file under `.claude/agents/` per worker role, one skill per "Skills" entry under `.claude/skills/`, a tailored PROMPT.md embedding the orchestrator persona and the case's "PROMPT.md domain rules", and `projects/<name>/consensus.md` + `human_directives.md` (no sentinel; standing directives pre-filled as D1, D2, ...).
3. Confirm config.yaml: `active_project` = the project, `squad` = the case's worker roles only (the orchestrator is never in squad - the headless session is the orchestrator), `single_cycle`/`loop_interval_seconds` per the case's cadence. Set the case's remaining config values (verbosity, cycle_timeout_seconds, max_cycle_logs) by hand - adapt does not touch those. Use `single_cycle: true` for the first run.
4. Run `.venv/bin/python loop.py`. Pass criteria: cycle completes, consensus.md validates and changed, the case's "Cycle 1 must produce" artifacts exist under `projects/<name>/docs/`, cycle log folder written.
5. Add one entry to `## Cycle Overrides` in human_directives.md, run a second cycle, and confirm the override was acted on and acknowledged by ID in `## What We Did This Cycle`.

Cases are ordered roughly by sophistication. "Squad" lists the orchestrator first; all others are workers delegated via the Task tool. The orchestrator persona is implemented in the tailored PROMPT.md (the headless cycle session IS the orchestrator); only worker roles become `.claude/agents/` files and `squad` entries. "Skills" are conventions agents apply during cycles - unlike /adapt itself, they are not human-only.

---

## Case 1: Daily Tech News Digest (Starter)

The smallest useful adaptation - validates the framework floor.

- **Goal**: Each cycle produces one markdown digest of the 5 most significant developments in a chosen tech area (e.g. AI tooling), with a 2-sentence "why it matters" per item.
- **Adapt answers**: domain=tech news curation; purpose=daily digest; roles=editor, researcher; phases=Collect, Rank, Publish; output=docs/digests/YYYY-MM-DD.md; cadence=daily.
- **Squad**:
  - `editor` (orchestrator): picks the day's theme, delegates collection, ranks candidates by significance over popularity, writes the final digest.
  - `researcher` (worker): web-searches the last 24h for the theme, returns 10-15 candidate items with source links and one-line summaries.
- **Skills**: `digest-format` - the exact digest template (title, date, 5 ranked items, why-it-matters, sources) so format never drifts.
- **consensus.md adaptations**: `## Current Phase` cycles Collect -> Rank -> Publish within one cycle (record final phase reached); `## Team State` tracks topics covered in the last 7 digests to avoid repetition.
- **PROMPT.md domain rules**: never repeat an item covered in the last 7 digests (check Team State); every item needs a primary-source link; exactly 5 items, no more; if fewer than 5 significant items exist, say so rather than padding.
- **human_directives.md starters**: D1: Focus area is <topic>. D2: Skip funding-round news unless >$100M.
- **Config**: loop_interval_seconds=86400, single_cycle=false (after first gated run), verbosity=false.
- **Cycle 1 must produce**: one `docs/digests/<date>.md` matching the skill template; Team State lists its 5 topics.

## Case 2: Personal Blog Studio (Starter+)

Adds a multi-stage editorial pipeline where one artifact matures across cycles.

- **Goal**: Take a post from idea to publishable draft over ~3 cycles: outline, draft, polish.
- **Adapt answers**: domain=blog writing; purpose=publish-ready posts in the author's voice; roles=editor-in-chief, writer, fact-checker; phases=Ideate, Outline, Draft, Polish, Done; output=docs/posts/<slug>/; cadence=gated (human approves between stages).
- **Squad**:
  - `editor-in-chief` (orchestrator): owns the pipeline, decides which stage the current post is in, delegates, and gates progression on quality.
  - `writer` (worker): produces outlines and prose in a voice defined by 2-3 sample posts the human drops in `docs/voice-samples/`.
  - `fact-checker` (worker): verifies every factual claim in a draft against web sources; returns claim-by-claim verdicts.
- **Skills**: `voice-match` - how to extract and apply style rules from the voice samples; `post-structure` - frontmatter, hook, section, CTA conventions.
- **consensus.md adaptations**: `## Current Phase` = pipeline stage of the active post; `## Team State` tracks active post slug, stage, and fact-check status; `## Open Questions` is the channel for asking the human about angle/voice choices.
- **PROMPT.md domain rules**: one post in flight at a time; never advance a stage in the same cycle it was entered (human reviews between stages - this exercises gated mode); a draft with unresolved fact-check failures cannot enter Polish.
- **human_directives.md starters**: D1: Posts are 800-1200 words. D2: Voice samples in docs/voice-samples/ are the style ground truth.
- **Config**: single_cycle=true permanently (gated is the point), verbosity=false.
- **Cycle 1 must produce**: `docs/posts/<slug>/outline.md` plus 3 candidate titles; consensus Next Action = await human review of the outline.

## Case 3: Open-Source Maintainer Assistant (Intermediate)

First case where agents operate on an external git repo - tests workspace discipline.

- **Goal**: Keep a designated GitHub repo healthy: triage new issues, draft replies, review open PRs, maintain a changelog draft.
- **Adapt answers**: domain=OSS maintenance; purpose=reduce maintainer toil; roles=maintainer, triager, reviewer; phases=Triage, Review, Report; output=docs/triage/ and docs/reviews/; cadence=daily.
- **Squad**:
  - `maintainer` (orchestrator): prioritizes the day's work across triage and review, synthesizes the daily report.
  - `triager` (worker): pulls new issues via `gh`, labels each (bug/feature/question/duplicate), drafts a reply, flags reproduction steps missing.
  - `reviewer` (worker): for each open PR, produces a review memo: what it changes, risks, test coverage, merge recommendation.
- **Skills**: `gh-readonly` - exact `gh` commands permitted (list/view only; comments and labels are DRAFTED to docs/, never posted); `review-memo` - the PR memo template.
- **consensus.md adaptations**: `## Team State` tracks issue numbers triaged and PR numbers reviewed (the dedup ledger); `## Key Decisions` records standing label taxonomy choices.
- **PROMPT.md domain rules**: READ-ONLY against GitHub - never post comments, push, or merge; all output is drafts in docs/ for the human to apply; never re-triage an issue number already in Team State; clone/fetch of the target repo goes under projects/<name>/workspace/ only.
- **human_directives.md starters**: D1: Target repo is <owner>/<repo>. D2: Security-labeled issues jump the queue. D3: Never draft a close recommendation for an issue less than 14 days old.
- **Config**: loop_interval_seconds=86400, verbosity=true (audit what gh commands ran).
- **Cycle 1 must produce**: `docs/triage/<date>.md` covering every open untriaged issue, and one review memo per open PR (or an explicit empty-queue note). Verify nothing was posted to GitHub.

## Case 4: Job Search Campaign Manager (Intermediate)

Personal-stakes domain; tests structured long-running state and strict factuality rules.

- **Goal**: Run a job search as a pipeline: source roles, score fit, tailor application materials, track status.
- **Adapt answers**: domain=job search; purpose=land interviews for <role type>; roles=campaign-manager, scout, application-writer; phases=Source, Score, Apply, Track; output=docs/pipeline.md and docs/applications/; cadence=daily.
- **Squad**:
  - `campaign-manager` (orchestrator): maintains the pipeline doc, decides which stage needs work, enforces the factuality rule.
  - `scout` (worker): searches postings matching the profile, returns role, company, link, requirements digest.
  - `application-writer` (worker): tailors resume bullets and a cover letter per posting, using ONLY facts from the human's master resume.
- **Skills**: `fit-score` - rubric scoring a posting 1-10 against the profile (skills match, seniority, location, comp signal); `tailor` - rules for adapting master-resume bullets to a posting without inventing anything.
- **consensus.md adaptations**: `## Team State` mirrors pipeline counts per stage (sourced/scored/drafted/applied); `## Open Questions` surfaces "apply or skip?" decisions for borderline scores.
- **PROMPT.md domain rules**: NEVER fabricate experience, dates, or skills - every resume line must trace to docs/master-resume.md; nothing is ever submitted anywhere - drafts only; fit-score below threshold (D2) is dropped with one-line rationale in the pipeline doc.
- **human_directives.md starters**: D1: Master resume at docs/master-resume.md is the only source of biographical truth. D2: Auto-drop fit scores below 6. D3: Target comp/location constraints: <fill in>.
- **Config**: loop_interval_seconds=86400, single_cycle=true initially (human reviews drafts), verbosity=false.
- **Cycle 1 must produce**: `docs/pipeline.md` with 10+ scored postings, and tailored materials under docs/applications/ for the top 2. Spot-check: every claim in the tailored resume exists in the master resume.

## Case 5: Literature Review Synthesizer (Intermediate)

Tests citation discipline and convergence - a survey that must end, not sprawl.

- **Goal**: Produce a structured literature review on a research question, growing docs/review.md cycle by cycle until saturation.
- **Adapt answers**: domain=academic synthesis; purpose=survey of <research question>; roles=lead-author, paper-scout, summarizer, synthesizer; phases=Search, Summarize, Synthesize, Saturated; output=docs/review.md + docs/papers/; cadence=every few hours.
- **Squad**:
  - `lead-author` (orchestrator): owns the review's argument structure, decides which themes are thin, declares saturation.
  - `paper-scout` (worker): finds relevant papers (arXiv, Semantic Scholar, Google Scholar via web), returns metadata + abstract + link.
  - `summarizer` (worker): one structured note per paper in docs/papers/<key>.md: claims, method, evidence strength, relevance.
  - `synthesizer` (worker): rewrites review sections to integrate new notes, maintains the bibliography.
- **Skills**: `paper-note` - the per-paper note template with a citation-key convention; `evidence-grading` - rubric for labeling evidence strength (strong/moderate/weak/anecdotal).
- **consensus.md adaptations**: `## Team State` tracks papers ingested per theme and themes marked saturated; `## Current Phase` moves to Saturated when two consecutive cycles add no new theme.
- **PROMPT.md domain rules**: every claim in review.md carries a citation key resolving to a note in docs/papers/; never cite a paper without a note; a theme is saturated after 2 cycles with no new distinct findings - stop searching it (this implements the convergence rule concretely); contradictory findings are reported as contradictions, never averaged away.
- **human_directives.md starters**: D1: Research question: <fill in>. D2: Prioritize work from the last 5 years. D3: Exclude non-peer-reviewed sources unless flagged as preprint.
- **Config**: loop_interval_seconds=14400, verbosity=false, max_cycle_logs=50.
- **Cycle 1 must produce**: 5+ paper notes, a review.md skeleton with themed sections, bibliography consistent with notes. Multi-cycle check: by cycle 3, review.md prose cites only existing note keys (scriptable check: every `[@key]` has a matching docs/papers/<key>.md).

## Case 6: Novel-Writing Studio (Intermediate-Advanced)

Creative domain with hard consistency constraints - tests memory/ as a continuity database.

- **Goal**: Write a novella chapter by chapter with consistent characters, timeline, and plot logic.
- **Adapt answers**: domain=fiction; purpose=complete a ~30k-word novella; roles=showrunner, prose-writer, continuity-editor, critic; phases=Worldbuild, Outline, Draft, Revise, Complete; output=docs/manuscript/ + docs/bible/; cadence=gated initially, then 2-3 cycles/day.
- **Squad**:
  - `showrunner` (orchestrator): owns the outline and arc, decides what gets written or revised this cycle, arbitrates between critic and writer.
  - `prose-writer` (worker): drafts one scene/chapter per delegation, following the bible and outline.
  - `continuity-editor` (worker): checks each draft against docs/bible/ (characters, timeline, established facts); returns a violations list; updates the bible with newly established facts.
  - `critic` (worker): adversarial read of the latest chapter - pacing, stakes, dialogue; 3 concrete fixes max.
- **Skills**: `story-bible` - schema for bible entries (characters.md, timeline.md, world.md, established-facts.md) and the update protocol; `scene-craft` - craft checklist (POV discipline, scene goal, conflict, exit hook).
- **consensus.md adaptations**: `## Team State` tracks chapters drafted/revised/final and total word count; `## Key Decisions` records irreversible plot commitments (these are append-only by rule).
- **PROMPT.md domain rules**: no chapter is final with open continuity violations; bible updates happen in the same cycle as the draft that established the fact; plot commitments in Key Decisions are never silently retconned - a retcon requires a Cycle Override from the human; one chapter per cycle max (quality over throughput).
- **human_directives.md starters**: D1: Genre/premise/tone: <fill in>. D2: Target 12 chapters, ~2500 words each. D3: No POV changes without my approval via Answers.
- **Config**: single_cycle=true for chapters 1-2, then loop_interval_seconds=28800; verbosity=false.
- **Cycle 1 must produce**: complete docs/bible/ skeleton with 3+ character entries, full chapter outline, and chapter 1 draft with a continuity report appended. Multi-cycle check: introduce a deliberate contradiction via Cycle Override in cycle 2 and verify the continuity-editor catches it.

## Case 7: Competitive Intelligence Desk (Advanced)

Long-horizon monitoring - tests trend memory across many cycles, not single-cycle output quality.

- **Goal**: Track 3-5 named competitors continuously; emit a weekly brief on moves, and same-day alerts on major events.
- **Adapt answers**: domain=market intelligence; purpose=keep leadership ahead of competitor moves; roles=intel-chief, watcher, analyst; phases=Watch, Analyze, Brief; output=docs/briefs/ + docs/alerts/ + memory/competitor-profiles/; cadence=2x daily.
- **Squad**:
  - `intel-chief` (orchestrator): triages watcher findings into noise/log/alert, schedules the weekly brief, owns profile quality.
  - `watcher` (worker): per competitor - news, blog/changelog, pricing pages, hiring signals since the last sweep; returns dated raw findings.
  - `analyst` (worker): integrates findings into memory/competitor-profiles/<name>.md (strategy read, trajectory, last 10 moves) and drafts brief sections.
- **Skills**: `signal-triage` - classification rubric: alert (ship/pricing/exec/funding), log (minor), noise (drop), with examples; `brief-format` - weekly brief template (per-competitor delta, cross-competitor pattern, so-what for us).
- **consensus.md adaptations**: `## Team State` tracks last-sweep timestamp per competitor and days until next brief; `## Next Action` alternates between sweep cycles and brief cycles.
- **PROMPT.md domain rules**: every finding gets a date and source URL; profiles live in memory/ and are updated incrementally, never rewritten from scratch (the accumulated trajectory IS the product); an alert-class finding produces docs/alerts/<date>-<competitor>.md in the same cycle; the weekly brief must lead with what CHANGED, not restate profiles.
- **human_directives.md starters**: D1: Competitors: <list>. D2: We care most about <segment>; weight findings accordingly. D3: Alert threshold - pricing changes always alert.
- **Config**: loop_interval_seconds=43200, verbosity=false, max_cycle_logs=60.
- **Cycle 1 must produce**: a profile in memory/competitor-profiles/ per competitor plus a baseline brief. Multi-cycle check: after 4+ cycles, profiles show dated incremental entries (not rewrites), and a brief references a trend spanning multiple sweeps.

## Case 8: Legacy Codebase Modernization Crew (Advanced)

Engineering case with objective pass/fail signals - tests the loop on real code where mistakes are detectable.

- **Goal**: Incrementally modernize a legacy repo (e.g. Python 2-era code to modern Python 3 + type hints + pytest) without ever breaking the test suite.
- **Adapt answers**: domain=software modernization; purpose=modernize <repo> safely; roles=tech-lead, migrator, test-engineer, code-reviewer; phases=Audit, Stabilize, Migrate, Verify, Done; output=workspace/ (the cloned repo) + docs/migration-log.md; cadence=hourly, gated for the first 3 cycles.
- **Squad**:
  - `tech-lead` (orchestrator): owns the migration plan in docs/, picks the next smallest safe slice, enforces the test gate, writes the migration log.
  - `migrator` (worker): executes exactly one migration slice (one module/pattern) on a branch in workspace/.
  - `test-engineer` (worker): before any migration, raises coverage on the target module; after, runs the full suite and reports.
  - `code-reviewer` (worker): diffs each slice for behavior changes disguised as refactors; verdict: approve/reject with reasons.
- **Skills**: `slice-protocol` - definition of a valid slice (single concern, <300 lines changed, reversible, has covering tests BEFORE migration); `test-gate` - exact commands to run the suite in the workspace venv and how to interpret/record results.
- **consensus.md adaptations**: `## Team State` tracks modules migrated/remaining, coverage %, and suite status (must read "green" to proceed); `## Key Decisions` records pattern-level choices (e.g. dataclasses over namedtuples) so slices stay consistent.
- **PROMPT.md domain rules**: the target repo is cloned to projects/<name>/workspace/ and ALL code changes happen there - never in the AgentTeam repo; a red test suite blocks all migration work until fixed (Stabilize preempts Migrate); every slice is a separate commit in the workspace clone with the migration log updated in the same cycle; coverage on a module must exceed 70% before it may be migrated; reviewer rejection means the slice is reverted, not patched forward.
- **human_directives.md starters**: D1: Target repo: <url>, branch from `main`, never push (human pushes after review). D2: Do not migrate <fragile module> until I say so. D3: Style: ruff + mypy --strict as the bar.
- **Config**: single_cycle=true for 3 cycles then loop_interval_seconds=3600; cycle_timeout_seconds=3600 (code work is slow); verbosity=true.
- **Cycle 1 must produce**: docs/migration-log.md with a full audit (module inventory, coverage map, dependency-ordered plan) and a green baseline test run recorded. Multi-cycle check: by cycle 4, 2+ slices committed in workspace/, suite green after each, and one reviewer rejection exercised (inject one via Cycle Override: "migrate module X without tests" - the rules must refuse).

## Case 9: Data Journalism Investigation Unit (Advanced)

Combines computation with narrative - tests reproducibility discipline and honest uncertainty.

- **Goal**: Investigate a question in public data (e.g. "how did city restaurant inspections change post-2020?"), producing a story draft backed by a reproducible analysis.
- **Adapt answers**: domain=data journalism; purpose=publishable data story on <question>; roles=editor, data-engineer, analyst, writer; phases=Acquire, Clean, Analyze, Verify, Write; output=docs/story/ + workspace/analysis/; cadence=2-3 cycles/day.
- **Squad**:
  - `editor` (orchestrator): owns the angle, kills findings that don't survive verification, sequences the work.
  - `data-engineer` (worker): finds and downloads public datasets into workspace/analysis/data/, documents provenance and caveats in a data dictionary.
  - `analyst` (worker): writes analysis scripts (Python in the project venv), produces findings with effect sizes and charts saved to docs/story/figures/.
  - `writer` (worker): turns verified findings into narrative; every number in prose links to the script that produced it.
- **Skills**: `provenance` - dataset documentation standard (source URL, retrieval date, license, known biases, row counts); `finding-card` - one card per finding: claim, magnitude, script path, confidence, caveats - the unit of editorial review.
- **consensus.md adaptations**: `## Team State` tracks findings by status (candidate/verified/killed/written); `## Open Questions` carries methodology calls for the human (e.g. exclusion criteria).
- **PROMPT.md domain rules**: every published number must be reproducible by re-running a named script on archived data - no numbers from memory or ad-hoc shell math; findings need a finding-card and verification before the writer may touch them; uncertainty is stated, never smoothed (report CIs or ranges where the data is thin); raw data is never edited in place - cleaning happens in scripts.
- **human_directives.md starters**: D1: Investigation question: <fill in>. D2: Datasets must be publicly redistributable. D3: Flag any finding implicating named individuals to me before writing it.
- **Config**: loop_interval_seconds=21600, cycle_timeout_seconds=2400, verbosity=true.
- **Cycle 1 must produce**: 2+ documented datasets with provenance records and an analysis plan in docs/story/plan.md. Verification check at cycle 3+: pick a number from the draft, re-run its named script, and confirm the number reproduces.

## Case 10: Indie Game Design Studio (Advanced - largest squad)

Stress test: most agents, most cross-functional conflict, dynamic squad pressure - the case that most motivates iteration 2's squad.py.

- **Goal**: Take a game concept to a complete, internally consistent design package: design doc, mechanics spec, narrative bible, economy model, playtest plan, and a balance simulation.
- **Adapt answers**: domain=game design; purpose=full design package for <concept>; roles=creative-director, mechanics-designer, narrative-designer, economy-designer, ux-designer, playtest-analyst; phases=Concept, Systems, Content, Balance, Package; output=docs/design/; cadence=3-4 cycles/day.
- **Squad**:
  - `creative-director` (orchestrator): owns the vision statement, resolves conflicts between designers (the key skill: mechanics vs narrative vs economy WILL contradict), picks 2-3 workers per cycle - not all five (exercises selective delegation, prefiguring squad.py).
  - `mechanics-designer` (worker): core loop, systems, rules; outputs precise spec language, no flavor.
  - `narrative-designer` (worker): world, factions, story beats; flags where story needs mechanical support.
  - `economy-designer` (worker): resources, sources/sinks, progression curves; outputs tables and formulas; writes a simple Python simulation in workspace/sim/ to sanity-check balance.
  - `ux-designer` (worker): screen flows and onboarding; ensures systems are learnable; outputs text wireframes.
  - `playtest-analyst` (worker): adversarial - simulates player archetypes (optimizer, explorer, casual) against the current design and reports where each breaks it.
- **Skills**: `design-doc-structure` - the package's canonical doc tree and cross-reference convention; `conflict-log` - protocol for recording inter-discipline conflicts and the director's ruling (decision, rationale, losing option preserved); `balance-sim` - conventions for the economy simulation (inputs from the spec tables, not hardcoded).
- **consensus.md adaptations**: `## Team State` tracks per-discipline doc maturity (missing/draft/stable) and open conflicts count; `## Key Decisions` is the conflict-ruling ledger; `## Current Phase` may not advance with open conflicts above zero.
- **PROMPT.md domain rules**: delegate to at most 3 workers per cycle, chosen by where Team State shows the weakest maturity; every cross-discipline contradiction gets a conflict-log entry and a ruling within 2 cycles; the economy sim must be re-run whenever spec tables change, with results pasted into the balance doc; playtest-analyst runs at least every 3rd cycle; vision statement is immutable without a Cycle Override.
- **human_directives.md starters**: D1: Concept: <one-paragraph pitch>. D2: Scope cap - design for a 4-person team, 12-month build. D3: No monetization mechanics beyond premium purchase.
- **Config**: loop_interval_seconds=21600, verbosity=true (delegation choices are the thing to audit), max_cycle_logs=80.
- **Cycle 1 must produce**: vision statement, doc-tree skeleton per design-doc-structure, and initial drafts from exactly the 2-3 disciplines the director chose (verify in the transcript that NOT all workers ran). Multi-cycle check: by cycle 5, at least one conflict-log entry with a ruling exists, and the sim has run against real spec tables.

---

## Coverage map (why these ten)

| Case | Tests primarily |
|---|---|
| 1 Digest | Minimum viable adaptation, format stability |
| 2 Blog | Gated mode, multi-cycle artifact maturation |
| 3 OSS | External-repo read-only discipline, dedup ledger |
| 4 Job search | Factuality constraints, structured pipeline state |
| 5 Lit review | Citation integrity, concrete convergence/stopping rule |
| 6 Novel | memory/ as consistency database, adversarial worker |
| 7 Intel desk | Long-horizon incremental memory, alert vs cadence duality |
| 8 Modernization | Objective pass/fail gates, workspace isolation, revert protocol |
| 9 Data journalism | Reproducibility, computation + narrative handoff |
| 10 Game studio | Largest squad, selective delegation, conflict arbitration |

Sophistication is varied deliberately: 1-2 should pass almost immediately and isolate framework bugs; 8-10 will surface prompt-rule and orchestration weaknesses. Recommended test order for a fresh implementation: 1, then 2 (gated mode), then 8 (objective signals), then 10 (orchestration limits).
