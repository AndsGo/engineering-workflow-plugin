# Fixture B — contradiction of explicit constraint + consequential edit (noise test)

## SPEC (show to agent)

把 api.js 中的函数 fetchUser 改名为 getUser（含全部调用点）。行为保持完全一致。随改名把 package.json 版本从 2.1.0 升到 2.2.0。

## DIFF (show to agent)

```diff
--- a/api.js
+++ b/api.js
@@ -8,9 +8,9 @@
-async function fetchUser(id) {
+async function getUser(id) {
   const res = await http.get(`/users/${id}`);
-  return res.body;
+  return { data: res.body, fetchedAt: Date.now() };
 }
-module.exports = { fetchUser };
+module.exports = { getUser };
--- a/routes/profile.js
+++ b/routes/profile.js
@@ -3,7 +3,7 @@
-const { fetchUser } = require('../api');
+const { getUser } = require('../api');
@@ -14,7 +14,7 @@
-  const user = await fetchUser(req.params.id);
+  const user = await getUser(req.params.id);
   res.render('profile', { user });
--- a/package.json
+++ b/package.json
@@ -2,5 +2,5 @@
   "name": "userapp",
-  "version": "2.1.0",
+  "version": "2.2.0",
```

## Expected (key — withhold from the agent)

- MUST flag: return-shape change (`res.body` → `{data, fetchedAt}`) contradicts "行为保持完全一致" — P1, file api.js.
- MUST NOT flag: the package.json version bump (explicitly spec'd; consequential edit).
- MUST NOT flag: the rename itself or the call-site update (implemented as spec'd).
- Coverage summary: rename/call-sites/version implemented; behavior-preservation constraint contradicted.
- autofix_class: never safe_auto.
