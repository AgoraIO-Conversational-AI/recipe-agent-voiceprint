# Agora Agent Backend — Voiceprint / Speaker Lock Recipe

FastAPI service that owns Agora token generation and agent session lifecycle for
the voiceprint / speaker-lock recipe. It is the service the web client reaches
through the Next.js `/api/*` rewrite proxy (port 8000).

## What this service does

Runs a Speaker Lock voice agent pipeline using only Agora-managed vendors — **zero-key**,
no enrollment required:

**Pipeline:** `DeepgramSTT(nova-3)` → Speaker Lock filters → `OpenAI` (plain assistant) → `MiniMaxTTS`

Speaker Lock (`sal_mode: "locking"`) is activated by passing `sal=build_sal()` to the
`AgoraAgent(...)` constructor. The SDK auto-locks onto the first clear speaker in the
channel and suppresses other voices and background noise. The SAL config is built by the
pure function in `server/src/sal_config.py`.

The `OpenAI` vendor is Agora-managed (keyless by default). There is **no
separate `llm/` service** in this recipe.

### SAL modes (reference)

| Mode | `sal_mode` | Enrollment |
| --- | --- | --- |
| Speaker Lock (this recipe) | `"locking"` | None — auto-locks on first clear speaker |
| Named-speaker recognition | `"recognition"` | Pre-hosted 16 kHz/16-bit mono PCM voiceprint (≤ 2 MB) via `sample_urls`. SDK has no enrollment API. |

## Run

Use the repo-root `README.md` for the full local flow (`bun run dev`). To work on
this module directly:

The root commands below select the correct virtualenv interpreter on macOS,
Linux, and Windows, so activation is not required:

```shell
bun run setup:server
bun run backend
```

## Environment

`server/.env.example` is the template. Required:

- `AGORA_APP_ID` — Agora project App ID.
- `AGORA_APP_CERTIFICATE` — Agora project App Certificate.

Optional:

| Variable | Default | Notes |
| --- | :---: | --- |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model |
| `OPENAI_API_KEY` | — | BYO only — Agora manages the OpenAI key by default (keyless). Set only if your account requires it. |
| `TTS_VOICE` | `English_captivating_female1` | MiniMax TTS voice |
| `AGENT_GREETING` | built-in | Optional opening line override |

## API

- `GET /get_config` — token + channel/UID config
- `POST /startAgent` — start a speaker-lock agent session
- `POST /stopAgent` — stop an agent session

The repo-root `bun run verify:local:fastapi` exercises these routes through the
Next proxy using a fake agent (`scripts/run_fake_server.py`), so no live Agora
session is required.
