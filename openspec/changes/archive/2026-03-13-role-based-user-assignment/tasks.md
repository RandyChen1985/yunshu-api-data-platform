# 实施任务清单：角色内分配用户

## 阶段 1：后端 API 开发

- [x] 1.1 在 `app/api/portal/endpoints/management.py` 中实现 GET `/api/portal/management/roles/{role_id}/users` 接口。 <!-- id: 0 -->
- [x] 1.2 在 `app/api/portal/endpoints/management.py` 中实现 PUT `/api/portal/management/roles/{role_id}/users` 接口。 <!-- id: 1 -->
  - 实现 `sys_user_role_relation` 的全量替换逻辑。
  - 确保更新成功后调用 `PermissionService.invalidate_role_cache(role_id)`。
- [x] 1.3 在 `tests/api/test_management_enhanced.py` 中为新的角色成员接口添加自动化测试。 <!-- id: 2 -->

## 阶段 2：前端 UI 增强

- [x] 2.1 更新 `frontend/src/views/Roles.vue`：在操作列添加“成员管理”按钮。 <!-- id: 3 -->
- [x] 2.2 在 `frontend/src/views/Roles.vue` 中实现 `MemberAssignmentDialog` 组件（或作为子组件）。 <!-- id: 4 -->
  - 集成 UI 组件库中的 `Transfer` (穿梭框) 组件。
  - 在弹窗打开时获取全量用户和当前角色成员。
- [x] 2.3 集成获取和更新角色成员的 API 调用逻辑。 <!-- id: 5 -->

## 阶段 3：验证与打磨

- [x] 3.1 在浏览器中手动验证角色到用户的分配流程。 <!-- id: 6 -->
- [x] 3.2 验证已分配/已取消分配用户的权限是否正确更新（检查缓存失效逻辑）。 <!-- id: 7 -->
- [x] 3.3 确保样式与管理后台其他部分保持一致。 <!-- id: 8 -->
