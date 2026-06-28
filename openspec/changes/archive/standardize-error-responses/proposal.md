# 提案：统一全局异常响应格式

## 1. 背景
当前项目虽然在成功响应时遵循了统一的 `BaseResponse` 格式（包含 `code`, `message`, `data` 等字段），但在抛出 `HTTPException` 时（例如权限校验失败、参数错误等），FastAPI 默认仅返回 `{"detail": "..."}`。这导致前端处理错误逻辑时需要兼容两种不同的响应结构，增加了复杂度，且不符合中台服务的 API 规范。

## 2. 目标
通过 FastAPI 的全局异常处理器（Global Exception Handler），拦截系统抛出的所有 `HTTPException` 以及意外的 `Exception`，将其统一转换为符合 `BaseResponse` 的 JSON 格式：

```json
{
  "code": 403,  // 与 HTTP 状态码一致，或自定义业务码
  "message": "Access denied: ...",
  "data": null,
  "timestamp": "2025-01-01T12:00:00",
  "trace_id": "req-123456"
}
```

## 3. 实施方案

### 3.1 修改 `app/main.py`
- 定义 `http_exception_handler`：拦截 `HTTPException`。
- 定义 `general_exception_handler`：拦截所有未捕获的 `Exception`（作为 500 处理）。
- 确保异常处理器中能够获取或生成 `trace_id`。
- 移除原有的分散的异常处理逻辑（如果存在冲突）。

### 3.2 涉及文件
- `app/main.py`: 注册异常处理器。
- `app/api/v1/schemas/data.py`: 确保 `BaseResponse` 定义清晰（已存在）。

## 4. 验证计划
- 触发一个 403 权限错误，检查响应格式。
- 触发一个 404 资源未找到错误，检查响应格式。
- 触发一个 500 内部错误（如模拟除零异常），检查响应格式。
