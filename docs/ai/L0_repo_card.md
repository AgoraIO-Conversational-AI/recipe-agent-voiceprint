# recipe-agent-voiceprint — Repo Card

> Next.js web client + Python FastAPI backend for an Agora Conversational AI voice agent with Speaker Lock (`sal_mode: "locking"`). Cascading pipeline: DeepgramSTT → OpenAI (Agora-managed, keyless) → MiniMaxTTS. Zero-key — no enrollment, no `OPENAI_API_KEY` required.

## Identity

| Field          | Value                                                                        |
| -------------- | ---------------------------------------------------------------------------- |
| Repo           | `AgoraIO-Conversational-AI/recipe-agent-voiceprint`                          |
| Type           | `distributed-system` (single repo, two co-located processes)                 |
| Language       | Python 3.10+ (FastAPI + uvicorn) backend + Next.js 16 / React 19 web         |
| Deploy Target  | `web/` as Next.js app, `server/` as a reachable FastAPI service              |
| Owner          | Agora Conversational AI DevEx                                                |
| Last Reviewed  | 2026-06-25                                                                   |
| Recipe Role    | `base`                                                                       |
| Recipe Version | `1.0.0`                                                                      |
| Recipe Status  | `experimental`                                                               |

## L1 — Summaries

The Audience column helps agents prioritise: **Use** = consuming the recipe's behavior, **Maintain** = modifying internals.

| File                                     | Purpose                                                                           | Audience       |
| ---------------------------------------- | --------------------------------------------------------------------------------- | -------------- |
| [01_setup](L1/01_setup.md)               | bun + venv + pip setup, env vars (zero-key; only Agora creds required), commands | Use & Maintain |
| [02_architecture](L1/02_architecture.md) | Two-process topology, Speaker Lock flow, cascading pipeline, request lifecycle    | Maintain       |
| [03_code_map](L1/03_code_map.md)         | `web/` and `server/` trees with key file responsibilities                        | Maintain       |
| [04_conventions](L1/04_conventions.md)   | Python async + FastAPI patterns, Biome, JSON envelope, SAL config ownership       | Maintain       |
| [05_workflows](L1/05_workflows.md)       | Add a route, change pipeline config, adjust SAL mode, verify, deploy             | Use            |
| [06_interfaces](L1/06_interfaces.md)     | FastAPI route contracts, rewrites, env vars, SAL config, cascading vendor config | Use & Maintain |
| [07_gotchas](L1/07_gotchas.md)           | SAL enrollment SDK gap, no `PORT` in env, no Route Handlers, UID normalization   | Maintain       |
| [08_security](L1/08_security.md)         | Token007, App Certificate server-only, keyless OpenAI, CORS, codec              | Maintain       |

## Recipe Profile

This repo declares `Recipe Role: base`. See [RECIPE.md](RECIPE.md) for extension points, invariants, and stable contracts before changing reusable surfaces.
