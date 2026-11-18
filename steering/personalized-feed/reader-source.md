# Reader source material

> Fictional reader created for the AgentTeam personalized-feed example. The person, employer
> and preferences below are invented; any resemblance to real people or organizations is
> coincidental.

This file is the ONLY source of truth about user #1 (`alex`). It stands in for the human
reader, who is not present during this run (see D8-D10).

---

## 1. Intake note from Alex (pasted, unedited)

hey - quick brain dump for the feed thing, sorry it's long-ish

i'm Alex, ML engineer, ~7 yrs, currently at a mid-size logistics company (Northwind
Freightworks) building internal LLM tools -
mostly agents that read shipping docs + a support copilot. before that classic ML, demand
forecasting, so i still care about evals and boring reliability stuff.

what i actually want: stuff i can *try*. a repo i can clone on a friday, a paper with code,
a good writeup from someone who actually shipped it. i do NOT want another "10 ways AI will
change X" post.

topics, roughly by how much i care:
- agent frameworks / orchestration / tool use - the main thing right now
- evals for LLM apps, esp. agent evals, regression testing prompts
- running models locally / small models / quantization (i have a 4090 at home)
- retrieval that isn't naive RAG - structured extraction from documents
- observability / tracing for LLM pipelines
- less: AI safety/alignment - interesting, but only the technical/hands-on side
- sometimes: rust tooling, i'm learning it slowly

not interested: crypto anything, funding/valuation news, prompt "hacks" listicles, AI art
drama, vendor marketing posts dressed up as tutorials.

sources i like: github trending, hacker news (comments more than links tbh), r/LocalLLaMA,
arxiv if there's code, a couple of medium/substack engineering blogs. lobste.rs sometimes.

## 2. Answers given in advance

- **Profile confirmation:** the interests in section 1 are CONFIRMED as stated, with weights
  in the order listed (agent frameworks highest; rust lowest). Anything else you infer
  stays `inferred` at weight <= 2 and must not dominate a feed.
- **Slack delivery (D4):** out of scope for this run. The canonical output is the markdown
  feed edition. Do not ask for credentials.
- **Sources needing auth or a ToS decision:** skip them; use only public APIs/RSS.
- **Anything else:** pick the conservative default, record it under Key Decisions, continue.

## 3. Simulated reactions (how Alex rates each edition)

Apply after each edition ships, through the feedback mechanism the team built (D6), and
log each one as `simulated` in the profile's engagement history:

- 👍 hands-on items (a repo, code, a reproducible writeup) on agent frameworks, LLM evals,
  or local / small models.
- 👍 one "broadening" item per edition outside the top interests, if it is hands-on.
- 👎 news / announcement items with nothing to try.
- 👎 anything in the "not interested" list above that slipped through.
- "more like this" on the single best eval-related item, if there is one.
- No reaction (neutral) on everything else.
