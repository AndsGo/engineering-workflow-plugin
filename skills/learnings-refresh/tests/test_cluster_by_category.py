import json
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "cluster_by_category.py"
FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "cluster"


def run():
    r = subprocess.run(
        ["python", str(SCRIPT), "--root", str(FIXTURE_ROOT)],
        capture_output=True, text=True, check=True,
    )
    return json.loads(r.stdout)


def test_returns_clusters_of_at_least_3():
    """3 'pattern' learnings should form a cluster."""
    out = run()
    pattern_clusters = [c for c in out if c["category"] == "pattern"]
    assert len(pattern_clusters) == 1, f"expected 1 pattern cluster, got {out}"
    assert len(pattern_clusters[0]["members"]) == 3


def test_does_not_return_clusters_below_threshold():
    """Single 'pitfall' learning should NOT form a cluster."""
    out = run()
    assert not any(c["category"] == "pitfall" for c in out)


def test_ignores_uncategorized():
    """Learning with no category should not contribute to any cluster."""
    out = run()
    # No cluster should have category == None or "" or "uncategorized"
    assert all(c["category"] for c in out)
    # And no member path should be the e.md file
    for c in out:
        assert not any("2026-04-03-e" in m for m in c["members"])
