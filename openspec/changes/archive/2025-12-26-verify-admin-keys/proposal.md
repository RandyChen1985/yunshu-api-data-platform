# 提案：验证管理接口 (API 密钥管理)

## Why
- **覆盖率缺失**: 当前 `tests/CHECKLIST.md` 显示 `/keys` 接口完全未测试 (❌)。
- **安全性**: API 密钥是认证系统的核心；未经验证的变更可能导致用户无法登录或未授权访问。
- **完整性**: 在正式发布前完成 API 测试策略的最后一块拼图。

## What Changes
- **后端测试**: 新增 `tests/api/v1/test_keys.py`。
- **验证**: 验证 `POST /api/v1/keys` (创建) 逻辑，包括 `AuthService.generate_api_key`。
- **文档**: 更新 `tests/CHECKLIST.md`。

## Risks
- **数据库依赖**: 测试依赖 `AuthService`，该服务会写入 MySQL。必须确保测试隔离（通过现有的 `conftest.py` 事务回滚或测试数据库机制处理）。
