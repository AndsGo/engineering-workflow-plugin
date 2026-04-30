import json
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "parse_learnings.py"
FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "parse"


def run(extra_args=()):
    result = subprocess.run(
        ["python", str(SCRIPT), "--root", str(FIXTURE_ROOT), *extra_args],
        capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)


def test_returns_list_of_learnings():
    out = run()
    assert isinstance(out, list)
    paths = {entry["path"] for entry in out}
    assert any("with-frontmatter" in p for p in paths)
    assert any("no-frontmatter" in p for p in paths)


def test_skips_index_and_archive():
    out = run()
    paths = {entry["path"] for entry in out}
    assert not any("INDEX.md" in p for p in paths)
    assert not any("archive" in p for p in paths)


def test_parses_frontmatter_when_present():
    out = run()
    fm_entry = next(e for e in out if "with-frontmatter" in e["path"])
    assert fm_entry["frontmatter"]["track"] == "knowledge"
    assert fm_entry["frontmatter"]["status"] == "active"
    assert fm_entry["frontmatter"]["category"] == "pattern"
    assert fm_entry["frontmatter"]["last_verified"] == "2026-04-29"


def test_applies_defaults_when_no_frontmatter():
    out = run()
    no_fm = next(e for e in out if "no-frontmatter" in e["path"])
    assert no_fm["frontmatter"]["track"] == "knowledge"
    assert no_fm["frontmatter"]["status"] == "active"
    assert no_fm["frontmatter"]["category"] is None
    assert no_fm["frontmatter"]["last_verified"]


def test_extracts_code_refs_with_path_separator():
    """W2: `code_refs` regex requires a path separator (/) to filter out
    `package.json`, `learnings-protocol.md`, etc."""
    out = run()
    fm_entry = next(e for e in out if "with-frontmatter" in e["path"])
    assert "pkg/foo/bar.go" in fm_entry["code_refs"]
    assert "cmd/baz/main.go" in fm_entry["code_refs"]
    assert "package.json" not in fm_entry["code_refs"]  # no path separator
    assert "learnings-protocol.md" not in fm_entry["code_refs"]  # .md excluded


def test_preserves_colon_in_frontmatter_value():  # A13 fix
    """A13: partition(':', 1) preserves colons in values."""
    out = run()
    entry = next(e for e in out if "colon-in-category" in e["path"])
    assert entry["frontmatter"]["category"] == "race-condition: server-side"
