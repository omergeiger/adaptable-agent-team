from pathlib import Path

from pfeed.ledger import Ledger
from pfeed.models import make_candidate
from pfeed.profile import parse_profile
from pfeed.rank_data import DEFAULT_WEIGHTS

ROOT = Path(__file__).resolve().parents[1]
PROFILE = parse_profile((ROOT / "profile" / "alex.md").read_text(encoding="utf-8"), "alex")


def cand(title, url, stype="GitHub", itype="repo", summary="", source=None, published="", **extras):
    return make_candidate(title, url, source or stype, stype, itype, summary, published, extras)


def empty_ledger(tmp_path):
    return Ledger(tmp_path / "ledger.md")


def good_pool():
    """Enough real-shaped (synthetic, test-only) candidates to fill an edition across >= 3 source types."""
    return [
        cand("o1/agentflow", "https://github.com/o1/agentflow", summary="agent framework with tool use", stars=900),
        cand("o2/agent-evals", "https://github.com/o2/agent-evals", summary="evals for llm agents", stars=300),
        cand("o3/gguf-tool", "https://github.com/o3/gguf-tool", summary="quantization to gguf for llama.cpp", stars=200),
        cand("Tracing LLM pipelines with OpenTelemetry", "https://blog.test/tracing", "blog", "article",
             "step-by-step tracing guide with code on github.com/x/y", source="Some Blog"),
        cand("Agent tool use on HN", "https://news.ycombinator.com/item?id=1", "HN", "discussion",
             "agent frameworks thread", comments=120, points=200),
        cand("Rust candle inference", "https://github.com/o4/candle-demo", summary="rust inference demo with candle", stars=50),
        cand("Structured extraction from PDFs", "https://arxiv.org/abs/2601.00001", "arXiv", "paper",
             "structured extraction from pdf documents", repo_links=["https://github.com/p/pdfx"]),
    ]
