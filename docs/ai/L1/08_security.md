# 08 · Security

> Trust boundaries, secret handling, and auth for the voiceprint recipe.

## Trust boundaries

| Hop                           | Auth                                                                   |
| ----------------------------- | ---------------------------------------------------------------------- |
| Browser → agent backend       | None in local dev (the `/api/*` rewrite is same-origin).               |
| Agent backend → Agora cloud   | Token007, generated from `AGORA_APP_ID` + `AGORA_APP_CERTIFICATE`.     |
| Agora cloud → OpenAI          | Agora-managed key (transparent); optionally `OPENAI_API_KEY` if set.   |
| Agora cloud → Deepgram / MiniMax | Agora-managed keys (transparent to this recipe).                    |

## Secret handling

- **Server-only secrets:** `AGORA_APP_CERTIFICATE` lives only in `server/.env.local` and never reaches the browser. The browser receives a short-lived token, never the certificate.
- `OPENAI_API_KEY` is optional. If set, it stays in `server/.env.local` and never reaches the browser — Agora manages the OpenAI key by default.
- `server/.env.local` is gitignored; `server/.env.example` ships placeholders and a comment clarifying `OPENAI_API_KEY` is optional.
- Tokens (`generate_convo_ai_token`) expire after 3600s and are minted per `get_config` call for a concrete non-zero UID.

## CORS

The backend sets `CORSMiddleware` with `allow_origins=["*"]` — open by design for a local/dev recipe. **Lock this down to known origins before any production deployment.**

## Validation

- `Agent.__init__` raises `ValueError` immediately if `AGORA_APP_ID` or `AGORA_APP_CERTIFICATE` are missing — the server sets `agent = None` and returns HTTP 500 on all routes.
- `Agent.start()` rejects empty `channel_name` and non-positive `agent_uid`/`user_uid` before issuing tokens or starting a session.
- Route errors are sanitized: `_log_route_error` logs only non-`None` context; SDK exceptions map to 400/500 without leaking internals beyond the error message.

## Deployment notes

- Set `AGENT_BACKEND_URL` only to a backend you control; the rewrite forwards browser requests there verbatim.
- The published Docker image is **backend-only** (`:8000`); it does not bundle secrets. No LLM sidecar is needed.
- No voiceprint file is stored by this recipe — `sal_mode: "locking"` is entirely stateless.

## Related Deep Dives

- None.
