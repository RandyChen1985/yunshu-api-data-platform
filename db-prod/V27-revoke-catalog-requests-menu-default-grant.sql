-- V27: 撤销目录权限申请菜单的默认全员授予（幂等）
-- 原因：V26 曾将 menu:catalog:requests 批量赋给所有角色，导致未分配审批权限的用户也看到侧栏入口。
-- 修复后可见条件：管理员 / 角色显式分配 menu:catalog:requests 或 element:catalog:review / 担任产品负责人
SET NAMES utf8mb4;

DELETE FROM `sys_ui_permissions`
WHERE `perm_type` = 'menu'
  AND `perm_code` = 'menu:catalog:requests'
  AND `role_id` IS NOT NULL;
