#!/usr/bin/env python3
"""Cluster learnings by category. Stdlib-only. Python 3.7+.

Returns groups of size >= MIN_CLUSTER_SIZE (hardcoded 3 per S3 plan-review).

Output: JSON list[{category, members: [paths]}] for clusters of size >=3.
Learnings with no category are excluded from clustering entirely.
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from parse_learnings import collect_learnings, resolve_learnings_dir  # noqa: E402

# 硬编码阈值，来自 S3 plan-review 审查结论。
# 若有其他项目需要不同阈值时再提取为参数。
MIN_CLUSTER_SIZE = 3


def cluster(learnings_dir):
    learnings = collect_learnings(learnings_dir)
    by_cat = defaultdict(list)
    for entry in learnings:
        cat = entry["frontmatter"].get("category")
        if cat:
            by_cat[cat].append(entry["path"])
    return [
        {"category": cat, "members": sorted(paths)}
        for cat, paths in by_cat.items()
        if len(paths) >= MIN_CLUSTER_SIZE
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    learnings_dir = resolve_learnings_dir(Path(args.root))
    out = cluster(learnings_dir)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
