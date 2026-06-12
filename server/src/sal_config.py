"""Pure builder for Agora selective-attention-lock (Speaker Lock) config.

Speaker Lock (sal_mode="locking") auto-locks the first clear speaker and suppresses
other voices + background noise — NO voiceprint enrollment required (zero-key). The
named-speaker "recognition" mode would need a pre-hosted PCM voiceprint via
`sample_urls`, and the SDK has no enrollment API — not used here.
"""


def build_sal() -> dict:
    return {"sal_mode": "locking"}
