# Cycle 1 source-scout note: initial catalog
Reader: alex (profile read; reader info only from steering reader-source.md per D8).
Output: projects/personalized-feed/sources/source-catalog.md

## Method
curl probes (unauthenticated, generic UA) on 2026-11-18 against about 30 candidate endpoints; catalog lists only what returned expected payloads, with failures marked.

## Findings
- Confirmed working: GitHub Search API, HN Algolia + Firebase, lobste.rs (all/ai/ml), arXiv API + RSS, HF daily papers, 12 blog/Substack RSS feeds, Medium tag feeds.
- Blocked/failed: Reddit r/LocalLLaMA RSS (429/403; OAuth excluded by constraint), Papers with Code API (returns HTML), rsshub trending mirror (403), LangChain /rss/ (HTML; /rss.xml works), Langfuse and vLLM feed guesses (404).
- Not used: github.com/trending (HTML scraping, fragile).
- Structural point: GitHub search by new-repo + topic replaces trending; HN comments (Algolia) are the highest-signal unique asset for Alex.
- Labels: API/RSS availability confirmed; relative content quality per source is likely (judged from feed metadata, not yet from item-level on-interest checks).

## Open items
- Run on-interest candidate searches per source next cycle to validate quality.
- Reddit decision for tech-lead (degrade or retest).
