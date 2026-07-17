# Fixture A — missing deliverable + unspecced substantive change

## SPEC (show to agent)

为 filetool CLI 增加 --verbose 标志：
1. 在 cli.py 的参数解析中新增 --verbose 布尔标志；
2. 置位时，每处理一个文件向 stderr 打一行日志 "processing <path>"；
3. 更新 README.md 的 Usage 一节，加入 --verbose 说明。

## DIFF (show to agent)

```diff
--- a/cli.py
+++ b/cli.py
@@ -12,6 +12,7 @@ def build_parser():
     p = argparse.ArgumentParser(prog='filetool')
     p.add_argument('paths', nargs='+')
     p.add_argument('--dry-run', action='store_true')
+    p.add_argument('--verbose', action='store_true')
     return p
@@ -31,6 +32,8 @@ def process(args):
     for path in args.paths:
+        if args.verbose:
+            print(f'processing {path}', file=sys.stderr)
         transform(path)
--- a/config.py
+++ b/config.py
@@ -3,7 +3,7 @@
 # network settings
-DEFAULT_TIMEOUT = 30
+DEFAULT_TIMEOUT = 60
 RETRIES = 3
```

## Expected (key — withhold from the agent)

- MUST flag: claim 3 missing (no README.md hunk) — P2, file README.md.
- MUST flag: unspecced substantive change — config.py DEFAULT_TIMEOUT 30→60 (no spec claim maps to it) — P2.
- MUST NOT flag: claims 1–2 (implemented as spec'd).
- Coverage summary: 3 claims — 2 implemented, 1 missing; 1 unspecced substantive change.
- autofix_class: never safe_auto.
