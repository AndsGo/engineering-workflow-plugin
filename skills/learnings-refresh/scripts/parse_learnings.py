#!/usr/bin/env python3
"""Parse learning files: extract frontmatter, title, body code-refs.

Outputs JSON to stdout. Stdlib-only. Python 3.7+.
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

DEFAULT_ROOT = Path("docs/learnings")
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# W2: tighten code-ref regex
# Require: at least one path separator (/) AND extension from allowlist (excluding .md)
# CONSTRAINT: requires POSIX-style path separator (/). Windows-authored
# learnings citing `pkg\foo\bar.go` will not be detected. Project convention:
# always use / in markdown code-refs even on Windows.
CODE_REF_EXTENSIONS = {"go", "py", "ts", "tsx", "js", "jsx", "rs", "java", "c", "cpp", "h", "hpp",
                      "rb", "php", "sh", "bash", "yaml", "yml", "toml", "json", "sql", "graphql"}
_ext_pattern = "|".join(re.escape(e) for e in CODE_REF_EXTENSIONS)
CODE_REF_RE = re.compile(rf"`([^`\s]*?/[^`\s]+\.({_ext_pattern}))(?::\d+)?`")


def parse_frontmatter(text):
    """Return (frontmatter_dict, body_text). Frontmatter may be empty."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    block = m.group(1)
    body = text[m.end():]
    fm = {}
    for line in block.splitlines():
        line = line.rstrip()
        if not line or ":" not in line:
            continue
        # A13: str.partition splits on FIRST colon, preserving colons in values
        key, _, value = line.partition(":")
        fm[key.strip()] = value.strip()
    return fm, body


def git_toplevel(path):
    """Return the git toplevel for the given path, or None if not a repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=path if path.is_dir() else path.parent,
            capture_output=True, text=True, check=True,
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def git_creation_date(path, toplevel):
    """Return YYYY-MM-DD of file's first commit, or today.

    Uses --diff-filter=A for the ADD commit. Resolves repo-relative path
    against the provided toplevel; runs `git log` from toplevel directory.
    """
    if not toplevel:
        return datetime.now().strftime("%Y-%m-%d")
    try:
        rel = path.resolve().relative_to(toplevel)
    except ValueError:
        return datetime.now().strftime("%Y-%m-%d")
    try:
        result = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%ad", "--date=short", "--", str(rel)],
            cwd=toplevel, capture_output=True, text=True, check=True,
        )
        lines = [l.strip() for l in result.stdout.strip().splitlines() if l.strip()]
        if lines:
            return lines[-1]  # --diff-filter=A typically returns 1 line; last line = oldest
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return datetime.now().strftime("%Y-%m-%d")


def extract_title(body):
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def extract_code_refs(body):
    """Find inline code refs that are file paths (have separator + allowed ext)."""
    seen = set()
    for m in CODE_REF_RE.finditer(body):
        seen.add(m.group(1))
    return sorted(seen)


def parse_file(path, learnings_dir, toplevel):
    text = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    fm_normalized = {
        "track": fm.get("track", "knowledge"),
        "status": fm.get("status", "active"),
        "category": fm.get("category") or None,
        "last_verified": fm.get("last-verified") or fm.get("last_verified") or git_creation_date(path, toplevel),
        "superseded_by": fm.get("superseded-by") or fm.get("superseded_by") or None,
    }
    # POSIX-style relative path
    if toplevel:
        try:
            rel = path.resolve().relative_to(toplevel).as_posix()
        except ValueError:
            print(f"warning: path {path} is outside git toplevel {toplevel}; using absolute path", file=sys.stderr)
            rel = str(path)
    else:
        try:
            rel = path.resolve().relative_to(learnings_dir.parent).as_posix()
        except ValueError:
            print(f"warning: path {path} is outside learnings_dir.parent {learnings_dir.parent}; using absolute path", file=sys.stderr)
            rel = str(path)
    return {
        "path": rel,
        "frontmatter": fm_normalized,
        "title": extract_title(body),
        "code_refs": extract_code_refs(body),
    }


def collect_learnings(learnings_dir):
    if not learnings_dir.exists():
        return []
    toplevel = git_toplevel(learnings_dir)
    out = []
    for path in sorted(learnings_dir.glob("*.md")):
        if path.name == "INDEX.md":
            continue
        out.append(parse_file(path, learnings_dir, toplevel))
    return out


def resolve_learnings_dir(root):
    root = Path(root).resolve()
    candidate = root / "docs" / "learnings"
    if candidate.is_dir():
        return candidate
    if root.name == "learnings" and root.is_dir():
        return root
    # No learnings directory found — return a non-existent path so collect_learnings
    # gracefully returns [] (it checks .exists() first).
    import sys as _sys
    print(f"warning: no docs/learnings/ found under {root}; returning empty learnings list",
          file=_sys.stderr)
    return root / "_no_learnings_dir_"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    args = ap.parse_args()
    learnings_dir = resolve_learnings_dir(args.root)
    out = collect_learnings(learnings_dir)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
