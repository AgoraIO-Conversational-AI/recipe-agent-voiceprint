# 02 · Architecture

> Two co-located processes. The browser talks only to Next.js `/api/*`, which rewrites to the FastAPI agent backend. The backend owns Agora tokens and the agent session, passing `sal=build_sal()` (Speaker Lock) to `AgoraAgent`. The pipeline is cascading: DeepgramSTT → OpenAI (Agora-managed) → MiniMaxTTS.

## Topology

```
Browser (localhost:3000)
  │  fetch /api/*
  ▼
Next.js (web/)  ──rewrite──▶  Agent backend (server/, :8000)
                                 │  AgoraAgent with sal={"sal_mode": "locking"}
                                 │  cascading: DeepgramSTT + OpenAI + MiniMaxTTS
                                 ▼
                              Agora ConvoAI Cloud
                                 │  Speaker Lock — auto-locks onto first clear speaker;
                                 │    suppresses other voices + background noise
                                 │  user speech → Deepgram STT (nova-3, managed)
                                 │  text → OpenAI (gpt-4o-mini, Agora-managed, keyless)
                                 │  response → MiniMax TTS (managed)
                                 ▼
                              User hears agent focused on their voice; RTM transcript + metrics → web UI
```

- **`web/`** — Next.js 16 / React 19 / TypeScript. Owns UI plus the RTC/RTM client lifecycle. Calls only `/api/*`.
- **`server/`** — Python FastAPI (:8000). Owns Agora token generation and agent session lifecycle. SDK: `agora-agents>=2.3.0` (`import agora_agent`).
- No `llm/` service — OpenAI is Agora-managed (keyless by default). No tunnel required.

## Request lifecycle

1. Browser `GET /api/get_config` → Next rewrites to backend `/get_config`; backend mints a Token007 from `AGORA_APP_ID` + `AGORA_APP_CERTIFICATE` and returns channel + UIDs.
2. Browser joins the RTC channel, then `POST /api/startAgent`; backend builds the cascading vendors and starts an async agent session with `sal=build_sal()`.
3. Speaker Lock (`sal_mode: "locking"`) auto-locks onto the first clear speaker in the channel and suppresses other voices and background noise.
4. Deepgram STT (nova-3) transcribes the locked speaker's audio; OpenAI generates a concise reply; MiniMax TTS speaks it back.
5. RTM delivers transcript + metrics to the web UI.
6. `POST /api/stopAgent { agentId }` ends the session.

## Why no `llm/` service

The recipe uses the **managed OpenAI vendor** (`agora_agent.agentkit.vendors.OpenAI`). Agora holds the OpenAI API key on its cloud — the recipe is **zero-key by default**. An optional `OPENAI_API_KEY` env var lets you bring your own account. Unlike the MLLM-based realtime recipe, this pipeline is cascading (three separate vendors) but does not require a local LLM service or a public tunnel.

## Key abstractions

- **`Agent`** (`server/src/agent.py`) — async wrapper around `AgoraAgent`; builds cascading vendors at `start()` time; owns the `AsyncAgora` client, env, and in-memory `_sessions` map keyed by `agent_id`.
- **`build_sal()`** (`server/src/sal_config.py`) — pure function returning `{"sal_mode": "locking"}`; passed as `sal=build_sal()` to `AgoraAgent(...)`.
- **`turn_detection`** — set directly on `AgoraAgent(...)` as a top-level dict (VAD config with `speech_threshold`, `start_of_speech`, and `end_of_speech` modes). Unlike the MLLM recipe, VAD is agent-owned.
- **Rewrite proxy** (`web/next.config.ts`) — the only browser→backend boundary; no Next Route Handlers exist for agent/token logic.

## Tech decisions

- **Rewrites, not Route Handlers** — hides backend placement behind `/api/*` so the same client works locally and deployed (set `AGENT_BACKEND_URL`).
- **Zero-key cascading pipeline** — all three vendors (Deepgram, OpenAI, MiniMax) are Agora-managed; only Agora credentials are required.
- **SAL as a pure config dict** — `sal_config.py` is free of SDK imports; the dict is passed to `AgoraAgent(...)` at construction.

## Related Deep Dives

- [sal_locking_flow](L2/sal_locking_flow.md) — Speaker Lock config, SAL modes, enrollment gap, and session parameters.
- [session_lifecycle](L2/session_lifecycle.md) — browser orchestration of config + start/stop, RTC/RTM, transcript mapping.
