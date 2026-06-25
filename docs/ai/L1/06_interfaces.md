# 06 · Interfaces

> Boundary contracts: backend routes, the `/api/*` rewrite map, env vars, the response envelope, and the cascading vendor + SAL config.

## Backend routes (port 8000)

The browser calls these as `/api/<name>`; Next rewrites to the backend `/<name>`.

### `GET /get_config`

- Query (optional): `channel?: string`, `uid?: int` (≤ 0 or missing → backend generates one).
- Returns `data`: `{ app_id, token, uid (string), channel_name, agent_uid (string) }`.
- Token is a Token007 RTC+RTM token, expiry 3600s, for a concrete non-zero UID.

### `POST /startAgent`

- Body: `{ channelName: string, rtcUid: int, userUid: int, parameters?: object }`.
  - `parameters.output_audio_codec?: string` is the only honored parameter field.
- Returns `data`: `{ agent_id, channel_name, status: "started" }`.
- 400 if `channelName`, `rtcUid`, or `userUid` is invalid. 500 if `AGORA_APP_ID`/`AGORA_APP_CERTIFICATE` are missing (Agent construction fails at boot).

### `POST /stopAgent`

- Body: `{ agentId: string }`.
- Returns `{ code: 0, msg: "success" }` (no `data`).

## Response envelope

```json
{ "code": 0, "msg": "success", "data": { } }
```

`data` omitted when the route has no payload. Non-zero `code` or missing `data` = error on the client side.

## Rewrite map (`web/next.config.ts`)

| Browser path        | Backend destination |
| ------------------- | ------------------- |
| `/api/get_config`   | `/get_config`       |
| `/api/startAgent`   | `/startAgent`       |
| `/api/stopAgent`    | `/stopAgent`        |

`rewrites()` returns `[]` when `AGENT_BACKEND_URL` is unset. The contract is asserted by `verify-api-contracts.ts` and exercised by `verify-local-proxy.ts`.

## Browser API client (`web/src/services/api.ts`)

- `getConfig({ channel?, uid? }) → GetConfigResponse`
- `startAgent(channelName, rtcUid, userUid) → agent_id`
- `stopAgent(agentId) → void`

## Environment variables

| Variable                | Scope          | Required | Default                         |
| ----------------------- | -------------- | :------: | ------------------------------- |
| `AGORA_APP_ID`          | backend        |    ✅    | —                               |
| `AGORA_APP_CERTIFICATE` | backend        |    ✅    | —                               |
| `OPENAI_MODEL`          | backend        |          | `gpt-4o-mini`                   |
| `OPENAI_API_KEY`        | backend        |          | — (Agora-managed; BYO optional) |
| `TTS_VOICE`             | backend        |          | `English_captivating_female1`   |
| `AGENT_GREETING`        | backend        |          | built-in line                   |
| `AGENT_BACKEND_URL`     | web (deploy)   |   ✅\*   | `http://localhost:8000` (dev)   |
| `PORT`                  | backend (env only) |      | `8000` — do **not** put in `.env.example` |

\* Required wherever the web app is deployed; rewrites are empty without it.

## Speaker Lock (SAL) config (`sal_config.py`)

`build_sal()` returns:

```python
{"sal_mode": "locking"}
```

This dict is passed as `sal=build_sal()` to `AgoraAgent(...)`. The `"locking"` mode auto-locks onto the first clear speaker with no enrollment. The alternative `"recognition"` mode requires `sample_urls` pointing to a pre-hosted PCM voiceprint file — not used in this recipe.

## Cascading vendor config (`agent.py`)

`Agent.start(...)` constructs:

- `DeepgramSTT(model="nova-3")` — Agora-managed, keyless.
- `OpenAI(api_key=None|OPENAI_API_KEY, model=OPENAI_MODEL, system_messages=[...], greeting_message=..., temperature=0.3)` — Agora-managed by default.
- `MiniMaxTTS(model="speech_2_6_turbo", voice_id=TTS_VOICE)` — Agora-managed, keyless.

Session parameters passed to `AgoraAgent(...)`:

| Parameter             | Value / Default          |
| --------------------- | ------------------------ |
| `audio_scenario`      | `"chorus"` (ultra-low-latency) |
| `data_channel`        | `"rtm"`                  |
| `enable_error_message`| `True`                   |
| `enable_metrics`      | `True`                   |
| `idle_timeout`        | 30 s                     |
| `expires_in`          | 3600 s                   |
| `output_audio_codec`  | per-request (optional)   |

## Related Deep Dives

- [sal_locking_flow](L2/sal_locking_flow.md) — full SAL config, SAL modes, and session parameter details.
