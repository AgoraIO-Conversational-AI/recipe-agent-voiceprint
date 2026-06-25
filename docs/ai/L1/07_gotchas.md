# 07 · Gotchas

> Non-obvious pitfalls specific to the voiceprint recipe. Read before changing the agent, SAL config, env, or verify scripts.

## `"recognition"` mode requires a pre-hosted PCM voiceprint — SDK has no enrollment API

`sal_mode: "recognition"` locks onto a *named* speaker, but the SDK has **no enrollment endpoint**. You must supply a pre-hosted 16 kHz / 16-bit mono PCM voiceprint (≤ 2 MB) via `sample_urls` in the SAL dict. Do not attempt `"recognition"` mode without a ready-to-serve PCM URL — the agent will fail to start or silently ignore the speaker filter.

## Agent initialization fails at server boot if Agora credentials are missing

Unlike the realtime recipe (where `OPENAI_API_KEY` is checked at start, not boot), `Agent.__init__` raises `ValueError` immediately if `AGORA_APP_ID` or `AGORA_APP_CERTIFICATE` are missing. The server sets `agent = None` on init failure and returns HTTP 500 on all routes. Always check `doctor:local` before a live run.

## OPENAI_API_KEY is optional — do not treat it as required

The `OpenAI` vendor is Agora-managed by default. `OPENAI_API_KEY` is only needed if your account requires a BYO key. Do not add a presence check for it in `Agent.__init__` or `start()`.

## Do not put `PORT` in `server/.env.example`

`verify:local:fastapi` injects a random `PORT` and loads env with `load_dotenv(override=True)`. A `PORT` line in `.env.example` (copied to `.env.local`) would clobber the injected port and break the smoke test.

## Keep `/api/*` ownership in rewrites

Adding `web/app/api/**/route.ts` for agent/token logic breaks the boundary — `verify-api-contracts.ts` explicitly fails if a `route.ts` exists under `app/api`. Token logic belongs in `server/`.

## camelCase request fields

`StartAgentRequest` uses `channelName`, `rtcUid`, `userUid` (camelCase) to match the browser client. Renaming one side without the other breaks the contract tests.

## UID normalization in transcripts

`normalizeTranscript` maps `uid === '0'` to the local UID. Token issuance also rejects zero/negative UIDs and generates a concrete one. Preserve both — speaker mapping and tokens depend on concrete UIDs.

## SAL config is a pure dict — keep `sal_config.py` import-free

`sal_config.py` has no `agora_agent` imports, making it independently testable (`test_sal_config.py`). Do not import SDK symbols into it; the dict is consumed by `AgoraAgent(...)` in `agent.py`.

## Local calls under a global proxy

Global proxies (Clash, etc.) can break `localhost`/RFC-1918 traffic. Configure the proxy to send `127.0.0.1`, `localhost`, and private ranges DIRECT, or use `socksio` (in `requirements.txt`) plus `all_proxy` to route the backend through SOCKS.

## Related Deep Dives

- [sal_locking_flow](L2/sal_locking_flow.md) — SAL modes and the enrollment SDK gap.
