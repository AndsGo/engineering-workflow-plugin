#!/usr/bin/env python3
"""Regenerate INDEX.md. Stdlib-only. Python 3.7+.

Critical safety: refuses to write if it would drop a non-empty section
whose heading is not in the allowlist (B3 plan-review fix).
"""
import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from parse_learnings import collect_learnings, resolve_learnings_dir  # noqa: E402

# S2: hardcoded allowlist (no --preserve-sections flag)
PRESERVED_HEADINGS = [
    "## How to Use This Index",
    "## Refresh Cycle",
    "## Notes for Future Refreshes",
]
# 机器管理的章节，始终重新生成（不属于"未知"）
MACHINE_MANAGED = ["## By Domain", "## By Track", "## Stats"]

HEADING_RE = re.compile(r"^## .+$", re.MULTILINE)


def normalize_heading(h):
    """A12: 折叠内部空白，转小写后比较。"""
    return " ".join(h.split()).lower()


def is_preserved(heading):
    return normalize_heading(heading) in {normalize_heading(p) for p in PRESERVED_HEADINGS}


def is_machine_managed(heading):
    return normalize_heading(heading) in {normalize_heading(m) for m in MACHINE_MANAGED}


def split_sections(text):
    """将文本按 ## 级标题拆分为 (heading, body) 列表。"""
    if not text:
        return []
    matches = list(HEADING_RE.finditer(text))
    parts = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        heading = m.group().strip()
        body = text[m.end():end]
        parts.append((heading, body))
    return parts


def check_unknown_sections(existing_text):
    """B3 guard: 返回非空未知章节的 (heading, body) 列表。"""
    unknown = []
    for heading, body in split_sections(existing_text):
        if is_preserved(heading) or is_machine_managed(heading):
            continue
        if body.strip():
            unknown.append((heading, body))
    return unknown


def extract_preserved(existing_text):
    """提取所有保留章节，返回 {normalized_heading: (original_heading, body)}。"""
    out = {}
    for heading, body in split_sections(existing_text):
        if is_preserved(heading):
            out[normalize_heading(heading)] = (heading, body)
    return out


def render_by_track(learnings):
    by_track = defaultdict(list)
    for e in learnings:
        by_track[e["frontmatter"]["track"]].append(e)
    out = ["## By Track\n"]
    for track in ("bug", "knowledge", "decision"):
        items = by_track.get(track, [])
        if not items:
            continue
        out.append(f"\n### {track.title()} ({len(items)})\n")
        for e in sorted(items, key=lambda x: x["path"]):
            out.append(f"- [{e['title']}]({Path(e['path']).name})")
        out.append("")
    return "\n".join(out)


def render_by_domain(learnings):
    by_cat = defaultdict(list)
    for e in learnings:
        cat = e["frontmatter"].get("category") or "Uncategorized"
        by_cat[cat].append(e)
    out = ["## By Domain\n"]
    for cat in sorted(by_cat):
        items = by_cat[cat]
        out.append(f"\n### {cat} ({len(items)})\n")
        for e in sorted(items, key=lambda x: x["path"]):
            out.append(f"- [{e['title']}]({Path(e['path']).name})")
        out.append("")
    return "\n".join(out)


def build_index(learnings, preserved):
    parts = ["# Project Learnings Index", "", f"Total active: {len(learnings)}", ""]
    for canonical_heading in PRESERVED_HEADINGS:
        key = normalize_heading(canonical_heading)
        if key in preserved:
            heading, body = preserved[key]
            parts.append(heading)
            parts.append("")  # 空行分隔标题与正文（固定，确保幂等）
            parts.append(body.strip())  # strip 两端空白保证幂等
            parts.append("")
    parts.append(render_by_domain(learnings))
    parts.append(render_by_track(learnings))
    return "\n".join(parts).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    learnings_dir = resolve_learnings_dir(Path(args.root))
    index_path = learnings_dir / "INDEX.md"
    existing = index_path.read_text(encoding="utf-8") if index_path.exists() else ""

    # B3: 若发现非空的未知章节，拒绝写入
    unknown = check_unknown_sections(existing)
    if unknown:
        print("ERROR: refuse to write — found unknown non-empty section(s) outside the preservation allowlist:",
              file=sys.stderr)
        for heading, body in unknown:
            print(f"  {heading}  ({len(body.strip())} chars)", file=sys.stderr)
        print("\nResolve by either:", file=sys.stderr)
        print("  - Adding the heading to PRESERVED_HEADINGS in generate_index.py", file=sys.stderr)
        print("  - Removing the section from INDEX.md (preserve content elsewhere if needed)", file=sys.stderr)
        sys.exit(1)

    preserved = extract_preserved(existing)
    learnings = collect_learnings(learnings_dir)
    new_content = build_index(learnings, preserved)

    if args.dry_run:
        print(new_content)
    else:
        index_path.write_text(new_content, encoding="utf-8")
        print(f"Wrote {index_path}")


if __name__ == "__main__":
    main()
