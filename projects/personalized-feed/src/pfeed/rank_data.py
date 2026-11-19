"""Heuristic tables for ranking. Plain data so ranking-engineer can review and revise them as small diffs.

Any change to DEFAULT_WEIGHTS or the selection rules in rank.py needs a critic GO/NO-GO.
"""

# --- Score weights (loop-plugin:relevance-rubric defaults; sum to 1.0) ---
DEFAULT_WEIGHTS = {"interest-match": 0.35, "novelty": 0.20, "hands-on": 0.20,
                   "thought-leadership": 0.15, "source-quality": 0.10}
SIGNALS = list(DEFAULT_WEIGHTS)

# --- Interest keyword sets. Key = lowercase PREFIX of the profile's interest name. ---
# Matching is on lowercase title + summary + topics. A hit in the title counts as strong.
INTEREST_KEYWORDS = {
    "agent frameworks": ["agent", "agents", "agentic", "langgraph", "crewai", "autogen", "smolagents",
                         "tool use", "tool calling", "function calling", "orchestrat", "multi-agent", "mcp"],
    "evals for llm": ["eval", "evals", "evaluation", "benchmark", "llm-as-a-judge", "llm-as-judge", "regression test",
                      "prompt testing", "promptfoo", "test suite"],
    "running models locally": ["llama.cpp", "gguf", "quantiz", "ollama", "local llm", "on-device", "small model",
                               "small language model", "4-bit", "int8", "vllm", "mlx", "consumer gpu", "run locally"],
    "retrieval beyond": ["structured extraction", "document parsing", "extraction", "pdf", "ocr", "schema",
                         "structured output", "json mode", "retrieval", "rerank", "graphrag", "chunking"],
    "observability": ["observability", "tracing", "opentelemetry", "otel", "langfuse", "telemetry", "monitoring",
                      "llm logging", "trace"],
    "ai safety": ["interpretability", "red team", "red-team", "jailbreak", "guardrail", "alignment eval",
                  "sparse autoencoder", "mechanistic"],
    "rust tooling": ["rust", "cargo", "candle", "burn-rs", "tokio"],
    "document-processing agents": ["document", "invoice", "shipping", "support copilot", "ticket", "form extraction"],
    "production reliability": ["reliability", "production", "retry", "fallback", "hardening", "postmortem",
                              "post-mortem", "guardrails", "incident", "sla", "failure mode"],
    "classic ml": ["forecasting", "time series"],  # weight 0 in the profile: never eligible
}
STRONG_HITS = 2  # >= this many distinct keyword hits, or any hit in the title, is a strong match

# --- Exclude rules. Profile "Anti-interests" bullet text (lowercase substring) -> rule name. ---
EXCLUDE_RULE_FOR_TEXT = {
    "crypto": "crypto", "funding": "funding", "prompt \"hacks\"": "listicle", "prompt hacks": "listicle",
    "ai art": "ai-art", "vendor marketing": "vendor-cta", "think-pieces": "think-piece",
    "nothing to try": "announcement",
}
EXCLUDE_KEYWORDS = {
    "crypto": ["crypto", "blockchain", "web3", "nft", "bitcoin", "ethereum"],
    "funding": ["raises $", "funding round", "series a", "series b", "valuation", "acquires", "acquisition"],
    "listicle": ["prompt hack", "chatgpt prompts", "prompt tricks"],
    "ai-art": ["ai art"],
    "think-piece": ["will change", "future of work", "will replace"],
}
LISTICLE_RE = r"^\d+\s+(ways|tips|tricks|prompts|tools|hacks)\b"
ANNOUNCEMENT_WORDS = ["announces", "announcing", "launches", "introducing", "partnership", "now available", "raises"]
CTA_WORDS = ["pricing", "sign up", "signup", "book a demo", "request a demo", "free trial", "get started for free"]
VENDOR_SOURCES = ["Hugging Face blog", "LangChain blog"]  # company blogs: CTA test applies
TRYABLE_WORDS = ["github.com", "notebook", "step-by-step", "tutorial", "code", "repo", "colab", "quickstart"]

# --- Signal heuristics ---
HANDS_ON_BY_ITEM_TYPE = {"repo": 5, "tool": 4, "paper": 2, "article": 2, "discussion": 2}
HANDS_ON_DISCUSSION_MANY_COMMENTS = (50, 3)  # (min comments, score)
HANDS_ON_TRYABLE_ARTICLE = 4
HANDS_ON_PAPER_WITH_REPO = 4

# source-quality: first matching key (prefix of Candidate.source) wins, else by source_type
SOURCE_QUALITY_BY_SOURCE = {"Hamel Husain": 5, "Eugene Yan": 5, "Simon Willison": 5, "Chip Huyen": 5,
                            "Sebastian Raschka": 5, "Lilian Weng": 5, "Latent Space": 4, "Interconnects": 4,
                            "Hugging Face blog": 4, "LangChain blog": 3}
SOURCE_QUALITY_BY_TYPE = {"GitHub": 4, "HN": 4, "arXiv": 4, "Lobsters": 4, "blog": 3, "Substack": 3, "Medium": 2}

# thought-leadership: 5 for notable authors (match on Candidate.source or extras["author"]), 3 for repos >= 5k stars
NOTABLE_AUTHORS = ["Hamel Husain", "Eugene Yan", "Simon Willison", "Chip Huyen", "Sebastian Raschka", "Lilian Weng"]
NOTABLE_REPO_STARS = 5000

# novelty: recency of delivered author/domain, counted in editions
NOVELTY_RECENT_EDITIONS = 7
AGGREGATOR_HOSTS = {"news.ycombinator.com", "lobste.rs"}  # discussions: host says nothing about the author

# --- Selection ---
TARGET_N = 5
MIN_N = 3
INTEREST_CAP_FRACTION = 0.4
MIN_SOURCE_TYPES = 3
DEFAULT_HANDS_ON_FLOOR = 2   # items with hands-on below this are dropped (design says "<= 1 dropped")
EXPLORATION_MIN_HANDS_ON = 4
TOP_INTERESTS_FOR_EXPLORATION = 3  # exploration pick must come from outside the top N interests by weight
