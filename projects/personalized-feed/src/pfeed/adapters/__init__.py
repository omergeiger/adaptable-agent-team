"""Source registry and fail-soft runner. Adding a source = adding one Source to build_sources().

Adapters raise FetchError when a source is unreachable or returns garbage; run_sources records the
error and moves on. A failed source yields zero items - nothing is ever synthesized.
"""
from dataclasses import dataclass, field
from datetime import date, timedelta
from functools import partial
from typing import Callable

from ..http import FetchError
from . import arxiv, github, hfpapers, hn, lobsters, rss

GITHUB_TOPICS = ["llm-agents", "ai-agents", "llm-evaluation", "llm-observability", "gguf",
                 "quantization", "structured-extraction", "document-parsing", "mcp"]
HN_QUERIES = ["agent framework", "eval", "llama.cpp", "quantization", "tracing", "structured extraction"]
# (catalog id, name, url, source_type)
FEEDS = [
    ("S8", "Hamel Husain", "https://hamel.dev/index.xml", "blog"),
    ("S9", "Eugene Yan", "https://eugeneyan.com/rss/", "blog"),
    ("S10", "Simon Willison", "https://simonwillison.net/atom/everything/", "blog"),
    ("S11", "Latent Space", "https://www.latent.space/feed", "Substack"),
    ("S12", "Chip Huyen", "https://huyenchip.com/feed.xml", "blog"),
    ("S13", "Sebastian Raschka", "https://magazine.sebastianraschka.com/feed", "Substack"),
    ("S14", "Interconnects", "https://www.interconnects.ai/feed", "Substack"),
    ("S15", "Lilian Weng", "https://lilianweng.github.io/index.xml", "blog"),
    ("S16", "Hugging Face blog", "https://huggingface.co/blog/feed.xml", "blog"),
    ("S17", "LangChain blog", "https://blog.langchain.com/rss.xml", "blog"),
    ("S-medium-agents", "Medium: llm-agents", "https://medium.com/feed/tag/llm-agents", "Medium"),
    ("S-medium-llmops", "Medium: llmops", "https://medium.com/feed/tag/llmops", "Medium"),
]


@dataclass
class Source:
    id: str
    url: str
    fetch: Callable  # fetch(http) -> list[Candidate]


@dataclass
class SourceReport:
    id: str
    url: str
    ok: bool
    count: int = 0
    error: str = ""


@dataclass
class RunResult:
    candidates: list = field(default_factory=list)
    reports: list = field(default_factory=list)


def build_sources(today=None):
    today = today or date.today()
    week_ago = (today - timedelta(days=7)).isoformat()
    since = None  # HN recency is handled by search_by_date ordering plus the min-points filter
    out = []
    for topic in GITHUB_TOPICS:
        url = github.url_for(f"topic:{topic}+created:>{week_ago}")
        out.append(Source(f"S1:{topic}", url, partial(github.fetch, url=url, name=f"GitHub topic:{topic}")))
    url = github.url_for(f"rust+llm+created:>{week_ago}")
    out.append(Source("S1:rust-llm", url, partial(github.fetch, url=url, name="GitHub rust+llm")))
    for q in HN_QUERIES:
        url = hn.url_for(q, since)
        out.append(Source(f"S3:{q}", url, partial(hn.fetch, url=url, name=f"HN: {q}")))
    for sid, url in [("S5:all", "https://lobste.rs/rss"), ("S5:ai", "https://lobste.rs/t/ai.rss"),
                     ("S5:ml", "https://lobste.rs/t/ml.rss")]:
        out.append(Source(sid, url, partial(lobsters.fetch, url=url)))
    out.append(Source("S7", arxiv.URL, partial(arxiv.fetch, url=arxiv.URL)))
    out.append(Source("S7c", hfpapers.URL, partial(hfpapers.fetch, url=hfpapers.URL)))
    for sid, name, url, stype in FEEDS:
        out.append(Source(sid, url, partial(rss.fetch, url=url, name=name, source_type=stype)))
    return out


def run_sources(http, sources):
    """Run every source; one failing never affects the others."""
    result = RunResult()
    for src in sources:
        try:
            items = src.fetch(http)
            result.candidates.extend(items)
            result.reports.append(SourceReport(src.id, src.url, True, len(items)))
        except FetchError as e:
            result.reports.append(SourceReport(src.id, src.url, False, 0, str(e)))
    return result
