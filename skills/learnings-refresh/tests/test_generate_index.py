import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "generate_index.py"
FIXTURE_OK = Path(__file__).parent / "fixtures" / "index"
FIXTURE_BAD = Path(__file__).parent / "fixtures" / "index-with-unknown"
INDEX_OK = FIXTURE_OK / "docs" / "learnings" / "INDEX.md"


def run(root, *args, expect_fail=False):
    r = subprocess.run(["python", str(SCRIPT), "--root", str(root), *args],
                       capture_output=True, text=True)
    if expect_fail:
        assert r.returncode != 0, f"expected failure but got {r.returncode}: {r.stdout}"
    else:
        assert r.returncode == 0, f"expected success but got {r.returncode}: {r.stderr}"
    return r


def test_dry_run_does_not_write():
    original = INDEX_OK.read_text()
    run(FIXTURE_OK, "--dry-run")
    assert INDEX_OK.read_text() == original


def test_preserves_authored_sections():
    r = run(FIXTURE_OK, "--dry-run")
    assert "## How to Use This Index" in r.stdout
    assert "This is custom user content" in r.stdout
    assert "## Notes for Future Refreshes" in r.stdout
    assert "Custom note that must survive" in r.stdout


def test_idempotent():
    run(FIXTURE_OK)
    first = INDEX_OK.read_text()
    run(FIXTURE_OK)
    second = INDEX_OK.read_text()
    assert first == second


def test_refuses_on_non_empty_unknown_section():  # B3 fix
    """B3 guard: refuse to write if it would drop a non-empty unrecognized section."""
    r = run(FIXTURE_BAD, expect_fail=True)
    assert "unknown" in r.stderr.lower() or "refuse" in r.stderr.lower()


def test_heading_normalization(tmp_path):  # A12 fix
    """A12: heading match should normalize whitespace + case before compare."""
    learnings = tmp_path / "docs" / "learnings"
    learnings.mkdir(parents=True)
    (learnings / "2026-01-01-x.md").write_text(
        "---\ntrack: knowledge\nstatus: active\n---\n\n# X\n",
        encoding="utf-8",
    )
    (learnings / "INDEX.md").write_text(
        "# Project Learnings Index\n\n"
        "##  how to use this index\n\n"
        "Custom user content that MUST survive regeneration.\n",
        encoding="utf-8",
    )
    r = subprocess.run(
        ["python", str(SCRIPT), "--root", str(tmp_path), "--dry-run"],
        capture_output=True, text=True, check=True,
    )
    assert "Custom user content that MUST survive" in r.stdout
