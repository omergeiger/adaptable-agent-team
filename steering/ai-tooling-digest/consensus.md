## Last Updated
2026-11-19T08:23:09Z

## Current Phase
Publish

## What We Did This Cycle
- Collect: editor chose theme (open agent interoperability and observability layer); researcher returned 13 candidates (11 cleanly in window, no in-window A2A, Mistral, xAI, JetBrains, Cursor or funding items).
- Rank: editor scored candidates per significance-rubric and shortlisted 5; dropped 5 as stale or unsourced (A2A SDK commit with no URL, LangSmith, Copilot team customizations, GitHub CLI event listen with unconfirmed times, MS Agent Framework Go outside window) and 3 on score.
- Publish: wrote projects/ai-tooling-digest/digests/2026-11-19-3.md (5 items) and appended to covered-items.md. Orchestrator fixed the Theme line (editor had written a generic theme); no second editor call needed.
- Acknowledged directives: D1, D2, D3, D4, D5, D6, D7

## Key Decisions
- Used the -3 filename suffix so the earlier 2026-11-19 digests were not overwritten.
- Published OpenTelemetry GenAI merged PRs as item 5 and labeled them as not yet a tagged release (score 14, confirmed timestamps).
- Dropped Copilot team customizations GA and GitHub CLI `gh event listen` because only dates, not times, were confirmed (D7); they are re-check candidates.

## Next Action
Run Collect -> Rank -> Publish for the next digest: pick a theme that avoids covered items; have the researcher fetch exact publish times for date-only sources (GitHub changelog entries) and cover still-open gaps (A2A spec/SDK releases, Mistral, xAI, JetBrains, Microsoft Agent Framework main repo, Cursor, Codex CLI newer than 0.170.0, funding over $100M from a primary source).

## Team State
Cycle 3 complete, no blockers. Three digests were published on 2026-11-19 (cycles 1-3).
- Digests published: 3
- Last digest: projects/ai-tooling-digest/digests/2026-11-19-3.md
- Covered items (last 7 digests):
2026-11-19 | Gemini 4 Neon GA in GitHub Copilot | https://github.blog/changelog/2026-11-18-gemini-4-neon-in-github-copilot
2026-11-19 | GitHub Copilot eight verified MCP connectors (preview) | https://github.blog/changelog/2026-11-18-connect-supabase-box-calendly-and-more-to-copilot
2026-11-19 | Claude Code 2.1.328 auto mode on third-party clouds | https://code.claude.com/docs/en/changelog
2026-11-19 | Pydantic AI 2.71.0 harness capabilities | https://github.com/pydantic/pydantic-ai/releases/tag/v2.71.0
2026-11-19 | Vercel AI SDK 7.0.177 interrupt option | https://github.com/vercel/ai/releases
2026-11-19 | openai-node 7.60.0 Live MCP server configuration | https://github.com/openai/openai-node/releases/tag/v7.60.0
2026-11-19 | MCP Inspector 2.16.0 load header and cookie jar | https://github.com/modelcontextprotocol/inspector/releases/tag/2.16.0
2026-11-19 | Gemini CLI 0.69.0 /stats heatmap | https://github.com/google-gemini/gemini-cli/releases/tag/v0.69.0
2026-11-19 | LangGraph 1.2.23 Send tool call state fix | https://github.com/langchain-ai/langgraph/releases/tag/1.2.23
2026-11-19 | TensorRT-LLM v1.4.0rc4 | https://github.com/NVIDIA/TensorRT-LLM/releases/tag/v1.4.0rc4
2026-11-19 | Visual Studio Code 1.147 agent workflows | https://code.visualstudio.com/updates/v1_147
2026-11-19 | Mastra core 1.84.0 storage v2 and crash recovery | https://github.com/mastra-ai/mastra/releases/tag/%40mastra%2Fcore%401.84.0
2026-11-19 | Agent Client Protocol v1.19.0 session cursors | https://github.com/agentclientprotocol/agent-client-protocol/releases/tag/v1.19.0
2026-11-19 | crewAI 1.15.42 Knowledge defaults to local Qdrant | https://github.com/crewAIInc/crewAI/releases/tag/1.15.42
2026-11-19 | OpenTelemetry GenAI conventions PRs 721 and 724 | https://github.com/open-telemetry/semantic-conventions-genai/pull/724
- Last cycle candidates: 13 found / 0 dropped as repeats / 0 dropped as funding
- Note: 5 candidates dropped as stale or unsourced, 3 on score. The editor wrote item text from the candidate notes without opening source pages. Re-check candidates: Copilot team customizations GA (https://github.blog/changelog/2026-11-18-customize-github-copilot-for-your-team), GitHub CLI v2.105.0 gh event listen (https://github.blog/changelog/2026-11-18-wait-for-pull-request-events-with-github-cli), LangSmith for Coding Agents. Researcher blockers: JetBrains blog 403, microsoft/agent-framework 404, Mistral and xAI docs give month-level dates only.

## Open Questions
(none)
