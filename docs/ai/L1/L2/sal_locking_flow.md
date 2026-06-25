# Speaker Lock (SAL) — Locking Flow

**When to Read This:** You are modifying the Speaker Lock config, switching SAL modes, adjusting VAD / session parameters, or adding named-speaker recognition support.

## What Speaker Lock does

Agora's Speaker Lock (SAL — Selective Attention Lock) is activated by passing a `sal` dict to `AgoraAgent(...)`. In `"locking"` mode, the SDK auto-detects the first clear voice in the channel, locks onto that speaker, and suppresses all other voices and background noise — no enrollment, no voiceprint file, no extra credentials.

## `build_sal()` — the config builder

`server/src/sal_config.py`:

```python
def build_sal() -> dict:
    return {"sal_mode": "locking"}
```

- **Pure function** — no SDK imports, no side effects. Independently testable.
- Returns a plain dict; `AgoraAgent(...)` receives it as `sal=build_sal()`.

## SAL modes

| Mode          | `sal_mode`      | Enrollment required | Notes                                                                                 |
| ------------- | --------------- | :-----------------: | ------------------------------------------------------------------------------------- |
| Speaker Lock  | `"locking"`     | None                | Auto-locks onto the first clear speaker. Zero-key. Used in this recipe.               |
| Named-speaker | `"recognition"` | Yes                 | Must supply `sample_urls` pointing to a pre-hosted 16 kHz / 16-bit mono PCM (≤ 2 MB). SDK has **no enrollment API** — you must host the PCM file yourself. Not used here. |

## AgoraAgent construction in `agent.py`

Relevant portions of `Agent.start()`:

```python
agora_agent = AgoraAgent(
    client=self.client,
    greeting=self.greeting,
    failure_message="Please wait a moment.",
    max_history=50,
    turn_detection={
        "config": {
            "speech_threshold": 0.5,
            "start_of_speech": {
                "mode": "vad",
                "vad_config": {
                    "interrupt_duration_ms": 160,
                    "prefix_padding_ms": 300,
                },
            },
            "end_of_speech": {
                "mode": "vad",
                "vad_config": {
                    "silence_duration_ms": 480,
                },
            },
        },
    },
    advanced_features={"enable_rtm": True},
    parameters=parameters,
    sal=build_sal(),   # ← Speaker Lock activated here
)
```

`turn_detection` is **agent-owned** in this cascading recipe (unlike the MLLM realtime recipe where it is vendor-owned). Do not move `turn_detection` onto a vendor.

## Session parameters

| Parameter             | Value / Default                | Notes                                          |
| --------------------- | ------------------------------ | ---------------------------------------------- |
| `audio_scenario`      | `"chorus"`                     | Ultra-low-latency chorus profile for web client |
| `data_channel`        | `"rtm"`                        | RTM used for transcript + metrics              |
| `enable_error_message`| `True`                         | Error events forwarded via RTM                 |
| `enable_metrics`      | `True`                         | Pipeline metrics forwarded via RTM             |
| `idle_timeout`        | 30 s                           | Session auto-terminates after 30 s idle        |
| `expires_in`          | 3600 s                         | Max session lifetime                           |
| `output_audio_codec`  | per-request or omitted         | Passed from `POST /startAgent parameters`      |

## Cascading vendor pipeline

```
DeepgramSTT(model="nova-3")        Agora-managed, keyless
   ↓ transcribed text
OpenAI(model=OPENAI_MODEL,         Agora-managed (keyless) unless OPENAI_API_KEY is set
       temperature=0.3,
       system_messages=[...])
   ↓ assistant reply text
MiniMaxTTS(model="speech_2_6_turbo", Agora-managed, keyless
           voice_id=TTS_VOICE)
```

All three vendors are built inside `Agent.start()`, not in `__init__`.

## Adding named-speaker recognition (not used here)

To use `"recognition"` mode you must:

1. Host a 16 kHz / 16-bit mono PCM voiceprint file (≤ 2 MB) at a public HTTPS URL.
2. Update `build_sal()` to return:
   ```python
   {"sal_mode": "recognition", "sample_urls": ["https://your-host/voiceprint.pcm"]}
   ```
3. Update `test_sal_config.py` to assert the new payload shape.
4. The SDK has no enrollment or recording API — you must produce and host the PCM file externally.
