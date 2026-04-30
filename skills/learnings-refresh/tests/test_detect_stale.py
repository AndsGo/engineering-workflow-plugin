import json
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "detect_stale.py"
FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "stale"


def run():
    r = subprocess.run(
        ["python", str(SCRIPT), "--root", str(FIXTURE_ROOT)],
        capture_output=True, text=True, check=True,
    )
    return json.loads(r.stdout)


def test_flags_ref_missing():
    """Learning citing a non-existent path should be flagged."""
    out = run()
    flagged = [e for e in out if any(s["kind"] == "ref-missing" for s in e["signals"])]
    assert any("2025-01-01-stale" in e["path"] for e in flagged), \
        f"expected stale learning to be flagged, got: {out}"


def test_does_not_flag_fresh_with_extant_refs():
    """Learning citing an existing path should NOT appear in output."""
    out = run()
    flagged_paths = {e["path"] for e in out}
    assert not any("2026-04-29-fresh" in p for p in flagged_paths), \
        f"fresh learning should not be flagged, got: {flagged_paths}"
