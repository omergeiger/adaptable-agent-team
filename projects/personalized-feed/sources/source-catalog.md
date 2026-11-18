# Source Catalog - personalized-feed

Last verified: 2026-11-18 (cycle 1) by source-scout, via curl from the build machine, unauthenticated.
Reader constraint (reader-source 2, D8): public API/RSS only, no auth, no ToS-gray scraping.
Status labels: VERIFIED = returned 200 with expected payload on 2026-11-18. UNVERIFIED = not confirmed. BLOCKED = failed.
Reliability labels: confirmed / likely / speculative. Quality 1-5 (5 = best fit for Alex). Fragility: LOW / MED / HIGH.
Use a generic User-Agent (e.g. `personalized-feed/0.1`). Cache with ETag/If-Modified-Since where offered.

## Summary of source types (D2 needs >=3 per daily feed)
| Type | Sources available |
|---|---|
| GitHub (repos) | S1 search API (primary); S2 trending page (HTML only - NOT used) |
| Blog / newsletter (Medium, Substack, personal) | S8-S16 |
| Technical forum | S3 HN Algolia, S4 HN Firebase, S5 lobste.rs; S6 r/LocalLLaMA (BLOCKED) |
| Papers with code | S7 arXiv API, S7b arXiv RSS, S7c HF Daily Papers |

D2 can be met without Reddit: GitHub + HN + lobste.rs + arXiv + blogs.

## Repos

### S1. GitHub Search API (stand-in for "trending")  - VERIFIED
- Endpoint: `https://api.github.com/search/repositories?q=<query>&sort=stars&order=desc&per_page=30`
- Tested: `q=topic:llm-agents+pushed:>2026-11-01` returned 200, total_count 2632.
- Trending proxy: query `created:>YYYY-MM-DD` (last 7 days) + `topic:` or keyword, sort by stars. Gives "new and rising" rather than GitHub's own trending.
- Topics to query: llm-agents, ai-agents, llm-evaluation, llm-observability, gguf, quantization, structured-extraction, document-parsing, mcp, rust (+ llm).
- Auth: none (optional token raises limits; not used). Rate limit: 60 req/hr unauthenticated for core (measured: limit 60); search endpoint has its own, tighter bucket (about 10/min unauth). Budget 10-15 queries per run.
- Quality 5 (hands-on, matches "repo to clone"). Reliability: confirmed. Fragility LOW. ToS: official API.
- Caveat: stars alone favor hype repos; ranking should require README/recent commits, and reject awesome-lists.

### S2. github.com/trending HTML  - REACHABLE BUT NOT RECOMMENDED
- `https://github.com/trending` returns 200 HTML, but there is no official API; parsing it is scraping. Fragility HIGH. Use S1 instead. Third-party mirror rsshub.app/github/trending returned 403 (BLOCKED). Do not use.

## Forums

### S3. Hacker News via Algolia API  - VERIFIED
- Endpoints: `https://hn.algolia.com/api/v1/search_by_date?query=<q>&tags=story&hitsPerPage=N`; `.../search?query=<q>&tags=comment` for comment threads; add `numericFilters=points>50,created_at_i>T`.
- Tested: both story and comment queries returned 200 JSON.
- Auth: none. Rate limit: documented about 10,000 req/hr per IP. Cadence: near real time.
- Quality 4-5: Alex values comments over links; use `tags=comment` and item pages (`/api/v1/items/<id>`) to pull top comments. Reliability: confirmed. Fragility LOW.
- Queries: "agent framework", "eval", "llama.cpp", "quantization", "tracing", "structured extraction", "Show HN" + tag `show_hn`.

### S4. Hacker News Firebase API  - VERIFIED
- `https://hacker-news.firebaseio.com/v0/topstories.json` (200, list of ids); item: `/v0/item/<id>.json`.
- Auth none; no published hard limit. Use for "currently top" ranking, then S3 for search. Quality 3, Reliability confirmed, Fragility LOW. Needs one request per item (fan-out).

### S5. lobste.rs RSS  - VERIFIED
- `https://lobste.rs/rss` (200), `https://lobste.rs/t/ai.rss` (200), `https://lobste.rs/t/ml.rss` (200). Rust tag feed `https://lobste.rs/t/rust.rss` is UNVERIFIED (not probed; same URL pattern).
- Auth none; no published limit; poll at most hourly. Low volume, high signal. Quality 3 (Alex: "sometimes"; good for rust tooling). Reliability confirmed. Fragility LOW.

### S6. r/LocalLLaMA RSS  - BLOCKED from build machine
- Tried `https://www.reddit.com/r/LocalLLaMA/.rss`, `/new/.rss`, `/top.rss?t=week`: HTTP 429 (an earlier `/top/.rss?t=week` returned 404 with an Atom body). JSON endpoint returned 403. old.reddit `.rss` returned an HTML page, not a feed.
- Reddit throttles unauthenticated/generic clients; the reliable route is OAuth, which is excluded by reader constraint. Rating: Reliability speculative. Fragility HIGH.
- Recommendation: treat as OPTIONAL; implement with retry/backoff and a descriptive UA, and fail soft (log "unreachable", never fabricate). Cover the topic through S3 (HN), S7c (HF Daily Papers), S1 (gguf/quantization topics) and blogs S13/S9. Decision for tech-lead: accept degraded coverage of r/LocalLLaMA or retest from the run environment.

## Papers with code

### S7. arXiv API  - VERIFIED
- `https://export.arxiv.org/api/query?search_query=cat:cs.CL+AND+all:agent&max_results=N&sortBy=submittedDate&sortOrder=descending` (200 Atom).
- Code filter: add `AND+abs:github` (tested: returned an entry); the `comment` and abstract fields often hold repo links. Also extract `github.com/...` from the summary/comment, and drop papers with none (Alex: arXiv only with code).
- Categories: cs.CL, cs.AI, cs.LG, cs.SE, cs.IR, cs.MA. Auth none. Limit: 1 request per 3 s, single connection (arXiv API terms). Updates daily.
- Quality 4. Reliability confirmed. Fragility LOW-MED (query syntax quirks; code detection is heuristic).

### S7b. arXiv RSS  - VERIFIED
- `https://rss.arxiv.org/rss/cs.CL` (200 RSS). Same policy; daily batch, no code filter. Quality 3. Fragility LOW.

### S7c. Hugging Face Daily Papers API  - VERIFIED (undocumented, public)
- `https://huggingface.co/api/daily_papers?limit=N` (200 JSON). Curated papers, often with linked GitHub repo and upvotes; good Papers-with-Code replacement.
- Auth none; limits unpublished. Quality 4. Reliability likely. Fragility MED (not a documented stable API).
- Papers with Code: `https://paperswithcode.com/api/v1/papers/` returned HTML, not JSON (service appears folded into Hugging Face). BLOCKED; do not use.

## Blogs and newsletters (RSS verified)
All below returned 200 with a feed body on 2026-11-18. Auth none; poll at most every few hours. Fragility LOW unless noted.

| ID | Source | Feed URL | Type | Fit to Alex | Quality |
|---|---|---|---|---|---|
| S8 | Hamel Husain | https://hamel.dev/index.xml | personal blog | LLM evals, practitioner (weight 4) | 5 |
| S9 | Eugene Yan | https://eugeneyan.com/rss/ | personal blog | LLM app patterns, evals, shipped systems | 5 |
| S10 | Simon Willison | https://simonwillison.net/atom/everything/ | personal blog | local models, tool use, hands-on; very high volume (filter) | 4 |
| S11 | Latent Space | https://www.latent.space/feed | Substack | agents/engineering; mixed with news (filter) | 3 |
| S12 | Chip Huyen | https://huyenchip.com/feed.xml | personal blog | agents, ML systems; low cadence | 4 |
| S13 | Sebastian Raschka (Ahead of AI) | https://magazine.sebastianraschka.com/feed (also sebastianraschka.substack.com/feed) | Substack | local/small models, from-scratch code | 4 |
| S14 | Interconnects (Nathan Lambert) | https://www.interconnects.ai/feed | Substack | model training/evals; some policy/news (filter) | 3 |
| S15 | Lilian Weng | https://lilianweng.github.io/index.xml | personal blog | agents, safety (technical); very low cadence | 4 |
| S16 | Hugging Face blog | https://huggingface.co/blog/feed.xml | company blog | local/small models; watch for marketing | 3 |
| S17 | LangChain blog | https://blog.langchain.com/rss.xml | company blog | agents/evals/observability; vendor-flavored, apply the "vendor marketing" exclude | 3 |
| S18 | The Sequence | https://thesequence.substack.com/feed | Substack | overview-heavy, mostly think-piece; low fit | 2 |
| S19 | Rust blog | https://blog.rust-lang.org/feed.xml | official | rust tooling (weight 1); announcements only | 2 |

Notes: `blog.langchain.dev/rss/` and `blog.langchain.com/rss/` return HTML, not a feed; the working one is `/rss.xml`. `langfuse.com/blog/rss.xml` returned 404 (UNVERIFIED alternative). `blog.vllm.ai/feed.xml` returned 404. Anthropic engineering page has HTML only; no RSS URL found, so excluded (UNVERIFIED).

### Medium
- Tag feeds VERIFIED (200 RSS): `https://medium.com/feed/tag/llm-agents`, `https://medium.com/feed/tag/llmops`. Publication/user feed pattern `https://medium.com/feed/@netflixtechblog` verified (200).
- Medium: Quality 2 on tag feeds (listicle and promo noise; apply excludes hard); only about 10 latest items per feed, partial content. Fragility MED (Medium may rate limit or change feeds; official RSS, not an API). Prefer publication feeds from named engineering teams over tags. No specific Alex-fit Medium publication verified yet; candidates to probe next cycle: `https://medium.com/feed/tag/llm-evaluation`, `.../tag/rag`, `.../tag/local-llm` (UNVERIFIED).
- Substack: feeds at `<name>.substack.com/feed` are public RSS (verified for S13, S18).

## Fragility summary (flag to tech-lead and developer)
- HIGH: S6 Reddit (throttled), S2 GitHub trending HTML (do not use).
- MED: S7c HF Daily Papers (undocumented), Medium feeds (partial/throttled).
- Implement fail-soft: per-source timeout (15 s), one retry with backoff, log unreachable, never fabricate items.
- Dedup across sources by canonical URL (HN/lobste.rs/arXiv/GitHub overlap heavily).

## Next to verify
- lobste.rs `/t/rust.rss`; Medium tags above; a Substack on agent evals or structured extraction; Reddit from the run environment.
