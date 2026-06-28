# 🔄 全量编译与重启工作流 (Full Compilation & Restart Workflow)

此流程严格遵循“物理清理 -> 完整编译 -> 端口强杀 -> 启动验证”四个阶段，并确保所有日志在前台实时显示。

## 1. 物理清理 (Phase 1: Cleanup)
```bash
echo "🧹 Removing old artifacts and logs..."
rm -rf frontend/dist app.log
echo "✅ Cleanup complete."
```

## 2. 前端构建 (Phase 2: Build)
```bash
echo "🏗️  Starting Frontend Compilation..."
cd frontend && npm run build
```

## 3. 强杀进程 (Phase 3: Kill)
```bash
echo "🛑 Cleaning up port 8000..."
pid=$(lsof -t -i:8000)
if [ -n "$pid" ]; then
  kill -9 $pid
  echo "✅ Killed old backend process: $pid"
else
  echo "ℹ️  No process found on port 8000."
fi
```

## 4. 启动验证 (Phase 4: Start & Verify)
```bash
echo "🚀 Starting FastAPI Service..."
source venv/bin/activate && nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > app.log 2>&1 &
echo "✅ Backend started in background."
echo "⏳ Waiting 3s for startup logs..."
sleep 3
echo "--- Final Startup Logs ---"
cat app.log
```
