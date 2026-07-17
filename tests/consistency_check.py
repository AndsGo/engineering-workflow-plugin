# -*- coding: utf-8 -*-
# 仓库一致性检查（发布前必须 GREEN）：技能计数与路由同步 / invocation 翻转 /
# 协议参与表 / spec-fidelity 轴 / fixtures 结构 / learnings 卫生 / 版本三字段。
# 断言纪律见 docs/learnings/2026-07-17-oracle-assertions-anchor-to-structure.md：
# 锚定结构而非出现、通用模式而非字面残留、成员由推导而非点名。
# 用法: python tests/consistency_check.py   （Windows: py -3）
import re, sys, io, json, hashlib
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(__file__).resolve().parents[1]
fails = []

def check(name, cond, detail=''):
    print(('PASS  ' if cond else 'FAIL  ') + name + ('' if cond else f'  -> {detail}'))
    if not cond:
        fails.append(name)

def read(p):
    return (ROOT / p).read_text(encoding='utf-8')

# ---- 基础数据 ----
dirs = sorted(p.parent.name for p in ROOT.glob('skills/*/SKILL.md'))
actual_total = len(dirs)
actual_process = actual_total - 1  # 除 using-engineering-workflow meta
readme = read('README.md'); arch = read('ARCHITECTURE.md')
guide = read('docs/engineering-workflow-guide.md'); contrib = read('CONTRIBUTING.md')
meta = read('skills/using-engineering-workflow/SKILL.md')
proto = read('skills/using-engineering-workflow/references/learnings-protocol.md')
sr = read('skills/structured-review/SKILL.md')
chlog = read('CHANGELOG.md')
print(f'actual skill dirs: {actual_total} ({actual_process} process + 1 meta)')

# ---- 1) 技能计数（通用模式，数字必须等于实际值）----
m = re.search(r'\*\*(\d+) process skills', readme)
check('README headline process count', m and int(m.group(1)) == actual_process)
m = re.search(r'### Skills \((\d+)\)', readme)
check('README skills-section count', m and int(m.group(1)) == actual_total)
m = re.search(r'provides (\d+) specialized skills', meta)
check('meta "provides N specialized skills"', m and int(m.group(1)) == actual_process)
m = re.search(r'## Available Skills \((\d+)\)', meta)
check('meta Available Skills header count', m and int(m.group(1)) == actual_process)
avail = meta.split('## Available Skills')[1]
rows = re.findall(r'^\| `([a-z0-9-]+)`', avail, re.M)
check('meta Available Skills rows == process skills', len(rows) == actual_process,
      f'rows={len(rows)}')
for fname, text in (('README.md', readme), ('ARCHITECTURE.md', arch),
                    ('guide', guide), ('CONTRIBUTING.md', contrib)):
    stale = [x.group(0) for x in re.finditer(
        r'\b(\d+)\s*(?:个自定义\s*)?(?:process\s+)?skills?\b', text)
        if int(x.group(1)) not in (actual_process, actual_total)]
    check(f'{fname} no stale skill-count prose', not stale, str(stale))

# ---- 2) invocation 翻转 ----
for s in ('engineering-retro', 'learnings-refresh'):
    fm = read(f'skills/{s}/SKILL.md').split('---')[1]
    check(f'{s} disable-model-invocation', 'disable-model-invocation: true' in fm)
    bad = [t for t in ('Use when', 'Use weekly', 'Use monthly', 'Triggers on') if t in fm]
    check(f'{s} human-facing description', not bad, str(bad))
    check(f'meta marks {s} user-invoked', bool(re.search(rf'`{s}`.*user-invoked', meta)))
check('session-start points at /learnings-refresh',
      '/learnings-refresh' in read('hooks/session-start'))

# ---- 3) 协议参与表（锚定表格行 + 成员推导）----
for d in dirs:
    if d != 'knowledge-compound' and 'knowledge-compound' in read(f'skills/{d}/SKILL.md'):
        check(f'participation row for {d}', bool(re.search(rf'^\| `{d}` \|', proto, re.M)))

# ---- 4) 结构面 ----
tree_missing = [d for d in dirs if d not in contrib]
check('CONTRIBUTING tree lists every skills/ dir', not tree_missing, str(tree_missing))
check('CHANGELOG has current-version entry',
      bool(re.search(r'^## \[' + re.escape(json.loads(read('.claude-plugin/plugin.json'))['version']) + r'\]', chlog, re.M)))
pj = json.loads(read('.claude-plugin/plugin.json'))
mk = json.loads(read('.claude-plugin/marketplace.json'))
vers = {pj['version'], mk['metadata']['version'], mk['plugins'][0]['version']}
check('version identical across 3 manifest fields', len(vers) == 1, str(vers))

# ---- 5) spec-fidelity 轴 ----
REV_DIR = ROOT / 'skills/structured-review/reviewers'
reviewers = sorted(p.stem for p in REV_DIR.glob('*.md'))
n_rev = len(reviewers)
check('SKILL.md Step 0b + skip announcement', 'Step 0b' in sr and 'Spec axis skipped' in sr)
check('SKILL.md axis-separation + safe_auto backstop',
      'Axis separation' in sr and 'Spec-axis autofix backstop' in sr)
check('SKILL.md report Spec Fidelity section', 'Spec Fidelity (Spec axis' in sr)
# 每个 reviewer 文件在 Step 3 两张表之一有行（推导，防第 6 个 reviewer 无路由）
for r in reviewers:
    check(f'SKILL.md Step 3 routes reviewer {r}', bool(re.search(rf'^\| `{r}` \|', sr, re.M)))
# reviewer 计数：通用扫描，任何 "N reviewer agents" / "of N triggered" 必须等于实际数
for fname, text in (('README.md', readme), ('guide', guide), ('SKILL.md', sr)):
    stale = [x.group(0) for x in re.finditer(r'\b(\d+) reviewer agents?\b|of (\d+) triggered', text)
             if int(x.group(1) or x.group(2)) != n_rev]
    check(f'{fname} reviewer-count prose == {n_rev}', not stale, str(stale))
# meta 路由行必须反映 spec 轴（router-that-lies）
check('meta Rule 1 row mentions spec axis for structured-review',
      bool(re.search(r'^\|[^|]*spec[^|]*\| `structured-review`', meta, re.M | re.I)))
check('meta Available Skills row mentions spec for structured-review',
      bool(re.search(rf'^\| `structured-review` \|[^|]*spec', avail, re.M | re.I)))
# JSON 契约键：每个 reviewer prompt 声明 Step 4 契约字段
CONTRACT = ('"reviewer"', '"severity"', '"autofix_class"', '"confidence"',
            '"residual_risks"', '"testing_gaps"')
for r in reviewers:
    body = read(f'skills/structured-review/reviewers/{r}.md')
    missing = [k for k in CONTRACT if k not in body]
    check(f'reviewer {r} declares JSON contract keys', not missing, str(missing))
check('spec-fidelity bans safe_auto', 'Never `safe_auto`' in read('skills/structured-review/reviewers/spec-fidelity.md'))

# ---- 6) fixtures 结构（盲测协议 load-bearing 标记）----
fixtures = sorted((ROOT / 'skills/structured-review/tests/fixtures').glob('*.md'))
check('spec-fidelity fixtures exist (>=3)', len(fixtures) >= 3, str(len(fixtures)))
for f in fixtures:
    t = f.read_text(encoding='utf-8')
    ok = '## SPEC' in t and '## DIFF' in t and '## Expected (key — withhold' in t
    check(f'fixture {f.name} has SPEC/DIFF/withhold-key sections', ok)

# ---- 7) eval 记录与被测 prompt 的新鲜度钉（防「收紧后未重跑」）----
rec = read('skills/structured-review/tests/README.md')
h = hashlib.sha256((REV_DIR / 'spec-fidelity.md').read_bytes()).hexdigest()[:16]
m = re.search(r'prompt-sha256:([0-9a-f]{16})', rec)
check('eval record pins shipped prompt hash', bool(m) and m.group(1) == h,
      f'record={m.group(1) if m else "MISSING"} actual={h}')

# ---- 8) learnings 卫生 ----
learn_dir = ROOT / 'docs/learnings'
names = {p.stem for p in learn_dir.glob('*.md')}
for p in sorted(learn_dir.glob('*.md')):
    t = p.read_text(encoding='utf-8')
    fm = t.split('---')[1] if t.startswith('---') else ''
    check(f'learning {p.name} frontmatter track+status',
          'track:' in fm and 'status:' in fm)
    broken = [w for w in re.findall(r'\[\[([^\]]+)\]\]', t) if w not in names]
    check(f'learning {p.name} wikilinks resolve', not broken, str(broken))

print()
print('RESULT: ' + ('GREEN' if not fails else f'RED ({len(fails)} failures)'))
sys.exit(0 if not fails else 1)
