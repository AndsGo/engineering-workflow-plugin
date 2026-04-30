#!/usr/bin/env python3
"""Detect stale learnings. Stdlib-only. Python 3.7+.

Two signals:
- ref-missing: learning cites a code path that no longer exists
- old-and-uncited: learning's last-verified is > ORPHAN_DAYS old AND has no code_refs

Outputs JSON to stdout (only learnings with at least one signal).
"""
import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from parse_learnings import collect_learnings, resolve_learnings_dir, git_toplevel  # noqa: E402

# 硬编码阈值 (S3 plan-review 修复)。如有第二个项目需要不同周期再引入 CLI 参数或环境变量。
ORPHAN_DAYS = 180


def days_since(date_str):
    """Days between today and date_str.

    Returns 0 for missing/empty dates (parse_learnings substitutes
    git_creation_date when frontmatter omits last-verified).
    Returns sys.maxsize for malformed non-empty dates (treats as
    maximally stale; warns to stderr).
    Returns 0 for future dates (clamped; warns to stderr).
    """
    if not date_str:
        return 0
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print(f"warning: unparseable last_verified date {date_str!r}; treating as stale",
              file=sys.stderr)
        return sys.maxsize
    age = (date.today() - d).days
    if age < 0:
        print(f"warning: future last_verified date {date_str!r} (age={age}); clamping to 0",
              file=sys.stderr)
        return 0
    return age


def detect(project_root, learnings_dir):
    learnings = collect_learnings(learnings_dir)
    out = []
    for entry in learnings:
        signals = []
        for ref in entry["code_refs"]:
            ref_path = project_root / ref
            if not ref_path.exists():
                signals.append({"kind": "ref-missing", "ref": ref})
        age = days_since(entry["frontmatter"].get("last_verified"))
        if age > ORPHAN_DAYS and not entry["code_refs"]:
            signals.append({
                "kind": "old-and-uncited",
                "last_verified": entry["frontmatter"].get("last_verified"),
            })
        if signals:
            out.append({"path": entry["path"], "signals": signals})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    learnings_dir = resolve_learnings_dir(root)
    # 用 --root 作为代码引用存在性检查的基准目录。
    # git_toplevel 仅用于 collect_learnings 内部生成相对路径；
    # 不能用来解析代码引用，否则 fixture 子目录场景下路径会指向外层仓库根。
    out = detect(root, learnings_dir)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
