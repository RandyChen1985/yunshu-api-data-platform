# 任务清单

## 1. 后端接口 (Backend)
- [ ] 定义 `ResourceDetailResponse` Schema (包含字段详情、配置等)
- [ ] 实现 `GET /api/portal/dashboard/my-resources` 接口
    - [ ] 逻辑: 获取当前用户权限 -> 聚合 Resource Meta 信息 -> 返回列表

## 2. 前端组件 (Frontend)
- [ ] 创建 `MyPermissionsModal.vue` 组件
    - [ ] UI 布局: 模态框，列表展示
    - [ ] 交互: 字段详情 Popover, 调用示例 Modal
- [ ] 修改 `Dashboard.vue`
    - [ ] Header 增加 "我的权限(N)" 按钮
    - [ ] 集成 `MyPermissionsModal`
    - [ ] 页面加载时调用 `fetchMyResources` (或者在 `auth/me` 后懒加载)

## 3. 验证 (Verification)
- [ ] 验证普通用户看到的权限列表是否正确
- [ ] 验证管理员看到的权限列表（应为全部）
- [ ] 验证复制、字段查看等交互功能
