# 提案：Dashboard "我的权限" 功能 (Add My Permissions Feature)

## 背景 (Background)
目前 Dashboard 缺乏直观的用户权限展示入口。用户无法快速查看自己拥有的资源权限，了解资源详情（如字段、更新时间）以及如何调用接口。虽然可以通过“API 调试”进行探索，但缺乏聚合的视图。

用户明确提出了在 Header 对这一功能的需求。

## 目标 (Goal)
- **提升透明度**: 在 Dashboard 顶栏直观展示用户拥有的资源权限数量（如 "我的权限(9)"）。
- **聚合资源信息**: 点击后通过弹窗展示完整的资源列表，包括 ID、API 示例、字段详情等。
- **降低接入成本**: 提供复制资源 ID 和查看标准/直接调用示例的快捷方式。

## 范围 (Scope)
- **前端 (Frontend)**:
    - 修改 `Dashboard.vue` Header 区域，新增“我的权限”按钮。
    - 新增“我的权限”弹窗组件 (`MyPermissionsModal.vue` 或集成在 Dashboard 中)。
    - 弹窗内包含：
        - 资源列表（支持搜索/过滤可选）。
        - 资源详情卡片/行（Show: ID, Group, Fields, Updated At）。
        - 字段详情展示（Popover 或展开）。
        - 调用示例展示（Tabs: 通用调用 vs 接口调用）。
- **后端 (Backend)**:
    - 现有 `AuthService` 和 `MetaService` 已足以支撑，只需确保 `api/portal/auth/me` 或 `dashboard/user-stats` 返回的数据足够（可能需要增强 `auth/me` 返回完整的资源列表，或者新增接口 `/api/portal/dashboard/my-resources`）。
    - **决定**: 为避免加重 `auth/me` 负担，新增 `GET /api/portal/dashboard/my-resources` 接口，专门返回当前用户有权访问的资源详细列表（包含字段配置等元数据）。

## 成功标准 (Success Criteria)
- Header 显示正确的权限数量。
- 点击按钮能弹出资源列表。
- 资源列表包含用户 ID、Group、字段信息。
- 用户能从界面直接复制 ID 和查看调用代码。
