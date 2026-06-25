# 04 · Conventions

> Coding patterns shared across `server/` and `web/`. Follow these to keep local and deployed modes aligned.

## Boundary ownership

- Browser code calls only `/api/*`. Backend placement is hidden behind Next rewrites (`web/next.config.ts`).
- **Never** add `web/app/api/**/route.ts` for agent/token logic — `verify-api-contracts.ts` fails the build if a `route.ts` appears under `app/api`.
- Token generation and the App Certificate stay in `server/`.

## Backend (Python / FastAPI)

- Async throughout: route handlers are `async def`; the agent uses `AsyncAgora` and `create_async_session`.
- Request bodies are Pydantic models (`StartAgentRequest`, `StopAgentRequest`). Field names are **camelCase** (`channelName`, `rtcUid`, `userUid`) to match the browser client.
- Error mapping is centralized: `_to_http_error()` maps `ValueError → 400`, `RuntimeError → 500`, else 500. `_log_route_error()` logs with safe context + traceback. Raise plain `ValueError`/`RuntimeError`; let the route convert.
- Logging via `logging.getLogger("uvicorn.error")`.
- Env read with `os.getenv`; `.env.local` then `.env` loaded with `override=True`.

## Response envelope

All backend JSON responses use:

```json
{ "code": 0, "msg": "success", "data": { } }
```

`data` is present only when the route returns a payload. The browser client treats `code !== 0` (or missing `data`) as an error.

## SAL config

- `build_sal()` lives in `sal_config.py` as a **pure function** with no `agora_agent` imports and no side effects.
- The dict it returns (`{"sal_mode": "locking"}`) is passed as `sal=build_sal()` to `AgoraAgent(...)` at session start.
- **Do not** inline the SAL dict in `agent.py` — keep it in `sal_config.py` for testability and for easy extension if a second mode is ever needed.
- The SDK has no voiceprint-enrollment API. Do not use `sal_mode: "recognition"` without a pre-hosted PCM voiceprint URL.

## Cascading vendor configuration

- Vendors (`DeepgramSTT`, `OpenAI`, `MiniMaxTTS`) are constructed inside `Agent.start()`, not in `__init__`.
- `turn_detection` is a top-level dict on `AgoraAgent(...)` — this is a cascading pipeline, not MLLM. It uses VAD-based detection (`speech_threshold`, `start_of_speech`, `end_of_speech`).
- `OpenAI` vendor is Agora-managed (keyless by default). `api_key` is passed as `None` unless `OPENAI_API_KEY` is set in env.

## Web (TypeScript / Next.js)

- Lint/format with Biome (`bun run lint`, `bun run lint:fix` in `web/`).
- RTC client creation must be StrictMode-safe (strict mode is on).
- Transcript speaker mapping uses real UIDs (`normalizeTranscript` maps `uid === '0'` to the local UID); do not heuristically guess speakers.
- API client lives in `src/services/api.ts`; UI never calls `fetch` to the backend directly.

## Testing approach

- Backend: `pytest` in `server/`, standalone — `conftest.py` fakes env and SDK session, so no cloud or real creds are needed.
- Web: contract/proxy/fastapi smoke scripts under `web/scripts/` run without live Agora calls.
- Run the **narrowest** relevant verify command before finishing (see [05_workflows](05_workflows.md)).

## Doc upkeep

When you change request/response contracts, env vars, or workflow, update the web client, backend, contract checks, README, **and** the matching `docs/ai/L1/` file together, then bump `Last Reviewed` in [L0](../L0_repo_card.md).

## Related Deep Dives

- None.
