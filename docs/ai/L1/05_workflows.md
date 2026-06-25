# 05 · Workflows

> Step-by-step guides for the common changes in this recipe. Each ends with the narrowest verify command to run.

## Add or change a browser-facing route

1. Add the FastAPI handler in `server/src/server.py` (return the `{ code, msg, data }` envelope).
2. Add the `/api/<name>` → `/<name>` mapping in `web/next.config.ts` `rewrites()`.
3. Add a client helper in `web/src/services/api.ts`.
4. Extend `web/scripts/verify-api-contracts.ts` with the new path + envelope assertions.
5. Verify: `bun run verify:web` (and `bun run verify:local:fastapi` if it should go through the real backend).

## Change the agent prompt / greeting / model

1. Greeting: set `AGENT_GREETING` (env) or edit the default in `server/src/agent.py`.
2. Model: set `OPENAI_MODEL` (default `gpt-4o-mini`).
3. TTS voice: set `TTS_VOICE` (default `English_captivating_female1`).
4. Other pipeline options (system prompt, temperature, VAD timing): edit `Agent.start()` in `server/src/agent.py`. See [sal_locking_flow](L2/sal_locking_flow.md).
5. Verify: `bun run verify:backend` (compile) + `cd server && pytest tests -v`.

## Change or extend the Speaker Lock config

1. Edit `build_sal()` in `server/src/sal_config.py`. Currently returns `{"sal_mode": "locking"}`.
2. If switching to `"recognition"` mode, you must supply a pre-hosted 16 kHz / 16-bit mono PCM voiceprint URL (≤ 2 MB) as `sample_urls`. The SDK has no enrollment API — see [07_gotchas](07_gotchas.md).
3. Update `test_sal_config.py` to assert the new payload shape.
4. Verify: `cd server && pytest tests -v`.

## Adjust session parameters (codec, scenario, idle timeout)

1. Edit the `parameters` dict in `Agent.start()` (`audio_scenario`, `data_channel`, `enable_metrics`, etc.).
2. `output_audio_codec` is also accepted per-request via `parameters` on `POST /startAgent`.
3. Verify: `bun run verify:local:fastapi`.

## Bring your own OpenAI key

1. Set `OPENAI_API_KEY=sk-...` in `server/.env.local`.
2. The `OpenAI` vendor uses the key if set; otherwise, Agora provides it (keyless).
3. No code changes needed — `agent.py` reads `OPENAI_API_KEY` with `os.getenv()` and passes it to the vendor.

## Run / debug locally

```bash
bun run dev              # both processes
bun run doctor:local     # check creds + .env.local before a live call
```

## Verify before finishing

| Change touches…              | Run                                                                 |
| ---------------------------- | ------------------------------------------------------------------- |
| Web only                     | `bun run verify:web`                                                |
| Backend logic / SAL config   | `bun run verify:backend` + `cd server && pytest tests -v`           |
| Route/proxy boundary         | `bun run verify:web:proxy` and/or `bun run verify:local:fastapi`    |
| Anything end-to-end (local)  | `bun run verify:local`                                              |

## Deploy

1. Deploy `web/` as a Next.js app.
2. Deploy `server/` (or any reachable FastAPI host); the published backend-only image is `ghcr.io/AgoraIO-Conversational-AI/recipe-agent-voiceprint` on `v*` tags.
3. Set `AGENT_BACKEND_URL` in the web deployment so rewrites reach the backend.
4. No separate LLM service is needed — OpenAI is Agora-managed.

## Related Deep Dives

- [sal_locking_flow](L2/sal_locking_flow.md) — SAL config build and session parameters in full.
- [session_lifecycle](L2/session_lifecycle.md) — client-side join/renewal/teardown.
