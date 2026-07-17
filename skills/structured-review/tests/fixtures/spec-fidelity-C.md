# Fixture C — partial implementation + silent reinterpretation + descoped non-item

## SPEC (show to agent)

1. 新增健康检查：在 server.js 增加 `GET /health` 端点，返回 JSON `{"status":"ok"}`；并在 docs/api.md 增加该端点的说明（两处交付面）。
2. 登录限流：auth.js 中对登录尝试限流为每分钟 5 次。
3. 服务器就绪时输出一条就绪日志，内容含监听端口。

## ORCHESTRATOR NOTE (show to agent)

会话中用户已明确将第 2 条（登录限流）移出本次范围（descoped），以最新议定版为准。

## DIFF (show to agent)

```diff
--- a/server.js
+++ b/server.js
@@ -18,6 +18,10 @@ const app = express();
 app.use(express.json());
 
+app.get('/health', (req, res) => {
+  res.json({ status: 'ok' });
+});
+
 app.listen(PORT, () => {
-  startCleanupTimer();
+  startCleanupTimer();
+  fs.appendFileSync('logs/boot.log', `ready on port ${PORT}\n`);
 });
```

## Expected (key — withhold from the agent)

- MUST flag: claim 1 **partial** — `GET /health` implemented in server.js, but docs/api.md untouched（两处交付面只做了一处）— P2.
- MUST surface: claim 3 的**静默重解读** — 「输出一条就绪日志」被实现为写入 logs/boot.log 文件而非常规的 console 输出，读法二选一未向用户表明（P3/advisory 或 P2 均可，关键是把这个选择作为 finding 呈现）。
- MUST NOT flag: claim 2（登录限流）缺失 — orchestrator note 已声明 descoped，最新议定版为准。
- autofix_class: never safe_auto.
