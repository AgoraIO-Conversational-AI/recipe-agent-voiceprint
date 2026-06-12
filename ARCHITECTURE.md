# Architecture — Voiceprint / Speaker Lock Recipe

Two processes. The browser talks only to Next.js `/api/*`, which rewrites to the
agent backend. The agent backend owns Agora tokens and agent lifecycle. OpenAI is
Agora-managed (keyless) — no separate LLM service is needed.

## Request flow

```
Browser
  │  GET /api/get_config            → token + channel/UIDs
  │  POST /api/startAgent           → start agent session
  ▼
Next.js  (rewrites /api/* → AGENT_BACKEND_URL)
  ▼
Agent backend (server/, :8000)
  │  builds AgoraAgent with sal={"sal_mode": "locking"} (Speaker Lock)
  │  managed OpenAI vendor (model=OPENAI_MODEL, plain assistant system prompt)
  ▼
Agora ConvoAI Cloud
  │  Speaker Lock — auto-locks onto primary speaker, suppresses other voices + noise
  │  user speech → Deepgram STT (managed, nova-3)
  │  text → OpenAI assistant (Agora-managed, keyless)
  │  response → MiniMax TTS (managed)
  ▼
User hears agent focused on their voice; RTM transcript + metrics → web UI
```

`POST /api/stopAgent { agentId }` ends the session.

## Speaker Lock (SAL)

`server/src/sal_config.py` contains the pure `build_sal` function:

```python
def build_sal() -> dict:
    return {"sal_mode": "locking"}
```

This dict is passed as `sal=build_sal()` to the `AgoraAgent(...)` constructor.
The SDK sends it to Agora ConvoAI Cloud, which activates Speaker Lock — no
voiceprint enrollment or extra credentials are required.

### SAL modes

| Mode | Value | Enrollment |
| --- | --- | --- |
| Speaker Lock (this recipe) | `"locking"` | None — locks onto the first clear speaker automatically |
| Named-speaker recognition | `"recognition"` | Requires a pre-hosted 16 kHz / 16-bit mono PCM voiceprint (≤ 2 MB) supplied via `sample_urls`. The SDK has no enrollment API — you must host the PCM file yourself. |

## Why no llm/ service

The recipe uses the **managed OpenAI vendor**
(`agora_agent.agentkit.vendors.OpenAI`). Agora holds the OpenAI API key on its
cloud; the recipe is zero-key by default. An optional `OPENAI_API_KEY` env var
lets you bring your own account if needed.

This means:
- No `llm/` service to expose publicly.
- No tunnel (ngrok) required.
- The only required credentials are `AGORA_APP_ID` + `AGORA_APP_CERTIFICATE`.

## API (agent backend, port 8000)

| Endpoint | Method | Description |
| --- | --- | --- |
| `/get_config` | GET | Token + channel/UID config |
| `/startAgent` | POST | Start the speaker-lock agent session |
| `/stopAgent` | POST | Stop the agent by `agent_id` |

The browser calls these as `/api/*`; Next rewrites them to `AGENT_BACKEND_URL`.

## Auth

- Browser → agent backend: none (local dev).
- Agent backend → Agora cloud: Token007, generated from `AGORA_APP_ID` +
  `AGORA_APP_CERTIFICATE`.
- Agora cloud → OpenAI: Agora-managed key (transparent to this recipe).
  Optionally overridden by `OPENAI_API_KEY` if provided.
