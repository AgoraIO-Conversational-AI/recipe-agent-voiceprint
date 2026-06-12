import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import sal_config as sc  # noqa: E402


def test_speaker_lock_no_enrollment():
    payload = sc.build_sal()
    assert payload["sal_mode"] == "locking"
    assert "sample_urls" not in payload
