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
STRONG_HITS = 2  # >= this many distinct keyword hits, or a STRONG keyword in the title, is a strong match
# Weak keywords are generic: a single weak hit scores one tier lower and is never strong via the title alone.
WEAK_KEYWORDS = {"production", "document", "form", "schema", "trace", "retrieval", "benchmark", "monitoring",
                 "incident", "ticket", "pdf", "extraction"}
# Keywords matched as a prefix (stems). Everything else is a whole word with an optional plural "s".
STEM_KEYWORDS = {"quantiz", "orchestrat"}
# An interest whose words are ambiguous alone needs one of these terms in the text (repos/tools are exempt).
CONTEXT_REQUIRED = {"rust tooling": ["llm", "ml", "ai", "agent", "inference", "model", "machine learning"]}
CONTEXT_EXEMPT_TYPES = ("repo", "tool")

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
    "ai-art": ["ai art", "ai-art", "ai artist", "ai-generated art", "ai generated art", "artcraft", "photoshop",
               "image generation", "image generator", "text-to-image", "midjourney", "generative art"],
    "think-piece": ["will change", "future of work", "will replace"],
}
EXCLUDE_WHOLE_WORD = {"ai-art"}  # these rules match whole words ("ai art" must not fire on "ai artifacts")
LISTICLE_RE = r"^\d+\s+(ways|tips|tricks|prompts|tools|hacks)\b"
ANNOUNCEMENT_WORDS = ["announces", "announcing", "launches", "introducing", "partnership", "now available", "raises"]
CTA_WORDS = ["pricing", "sign up", "signup", "book a demo", "request a demo", "free trial", "get started for free"]
VENDOR_SOURCES = ["Hugging Face blog", "LangChain blog"]  # company blogs: CTA test applies
TRYABLE_WORDS = ["github.com", "notebook", "step-by-step", "tutorial", "colab", "quickstart", "repository"]  # whole words only

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

# --- Traction (critic cycle 3, change 2). Starting guesses; ranking-engineer tunes on real output. ---
TRACTION_LADDER = [(1000, 5), (200, 4), (50, 3), (10, 2), (0, 1)]  # (min stars or HN points, source-quality)
MIN_REPO_STARS = 25                   # GitHub repos below this are dropped unless another item points at them
VELOCITY_MAX_AGE_DAYS = 7             # a repo this young with >= VELOCITY_MIN_STARS counts as at least VELOCITY_QUALITY
VELOCITY_MIN_STARS = 50
VELOCITY_QUALITY = 4

# --- Topic fatigue (critic cycle 3, change 5) ---
FATIGUE_EDITIONS = 5                  # look at the last N editions
FATIGUE_MIN_HITS = 3                  # interest delivered in >= this many of them -> novelty capped
FATIGUE_NOVELTY = 3

# --- Top-interest guardrail (critic cycle 3, change 4) ---
TOP_INTEREST_CAP_FRACTION = 0.6       # at most round(0.6*n) items (3 of 5) from the top-3 interests combined

# --- Slice 4 (ranking-engineer cycle 6 eval) ---
MIN_INTEREST_MATCH_MAIN = 3           # slice 6: items scoring <= 2 are dropped, never used to fill a slot or a source type
EXPLORATION_MIN_INTEREST_MATCH = 3    # exploration pick needs a strong match (Scored.strong) AND at least this
EXPLORATION_EXCLUDED_SOURCE_TYPES = ("Substack",)  # newsletter headlines are not tryable
TAIL_REPO_STARS = 50                  # at most MAX_TAIL_REPOS delivered repos below this per edition
MAX_TAIL_REPOS = 1
# Same repo name under different owners = one cluster (clone defect), only for distinctive names.
CLONE_MIN_NAME_LEN = 8
CLONE_GENERIC_NAMES = {"agent", "agents", "examples", "demo", "starter", "playground", "tutorial"}

# --- Slice 5 (ranking-engineer cycle 7 eval, MF1) ---
SUMMARY_CAP_SOURCE_TYPES = ("HN", "Lobsters")  # long promotional bodies: summary-only hits are capped
SUMMARY_ONLY_CAP = 3
