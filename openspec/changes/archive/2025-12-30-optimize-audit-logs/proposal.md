# Audit Log Optimization Proposal

**Change ID**: `optimize-audit-logs`
**Status**: DRAFT

## 目标 (Goal)
优化审计日志功能的搜索体验，修复用户名搜索无效的问题，并增强日志详情的展示。

## 背景 (Context)
当前审计日志页面中，用户名和客户端 IP 的搜索采用的是精确匹配（Exact Match），导致管理员在不记得完整用户名或 IP 时无法有效地检索日志。此外，日志详情页的 JSON 数据展示较为生硬，缺乏良好的阅读体验。

## 变更范围 (Scope)
1.  **后端 (Backend)**:
    - 修改 `user_name` 过滤逻辑，支持模糊匹配 (LIKE)。
    - 修改 `client_ip` 过滤逻辑，支持模糊匹配 (LIKE)。
    - 保持现有的其他过滤逻辑不变。

2.  **前端 (Frontend)**:
    - 确保前端传递的搜索参数格式正确（目前已正确，只需后端适配）。
    - 优化详情页 Request Params 和 Response Body 的展示（确保格式化 JSON）。

## 验证计划 (Verification Plan)
1.  **自动化测试**:
    - 更新 `tests/api/portal/test_audit_enhanced.py`，新增针对模糊搜索的测试用例。
2.  **手动验证**:
    - 进入审计日志页面。
    - 输入部分用户名（如 "admin" 的 "adm"），验证能否搜出结果。
    - 输入部分 IP，验证能否搜出结果。
    - 点击详情，检查 JSON 数据也可以正确展开和阅读。
