## 1. 数据库与模型

- [x] 1.1 创建 V18 SQL 脚本：创建 `sys_masking_rules` 表，并为 `sys_users` 和 `sys_roles` 增加 `masking_strategy` 字段。 <!-- id: 0 -->
- [x] 1.2 初始化默认脱敏规则：在 SQL 脚本中预置手机号、邮箱、身份证等规则。 <!-- id: 1 -->

## 2. 后端核心逻辑

- [x] 2.1 创建 `app/services/masking_service.py`：实现核心类 `MaskingService`。 <!-- id: 2 -->
- [x] 2.2 实现 `mask_value` 方法：包含手机号、邮箱、全遮掩等算法。 <!-- id: 3 -->
- [x] 2.3 实现 `mask_recursive` 方法：递归遍历 Dict/List 结构。 <!-- id: 4 -->
- [x] 2.4 实现规则加载与缓存逻辑：从 DB 加载规则到内存 `_RULES_CACHE`。 <!-- id: 5 -->

## 3. API 接口集成与管理

- [x] 3.1 修改 `/api/v1/resources/{key}`：接入 `MaskingService`，支持 `unmask` 参数校验。 <!-- id: 6 -->
- [x] 3.2 修改 `/api/portal/lab/execute`：接入 `MaskingService`。 <!-- id: 7 -->
- [x] 3.3 实现规则管理 API：规则的 CRUD 接口。 <!-- id: 8 -->
- [x] 3.4 扩展用户/角色 API：在获取和更新用户/角色信息时，包含脱敏策略字段。 <!-- id: 9 -->

## 4. 前端配置界面

- [x] 4.1 `SystemConfig.vue`：新增“数据脱敏”标签页，包含全局开关、规则管理和示例说明。 <!-- id: 10 -->
- [x] 4.2 `Users.vue`：用户编辑弹窗中增加“脱敏策略”配置项。 <!-- id: 11 -->
- [x] 4.3 `Roles.vue`：角色编辑弹窗中增加“脱敏策略”配置项。 <!-- id: 12 -->
- [x] 4.4 实现脱敏效果实时预览：在配置规则时展示 Mock 数据的脱敏结果。 <!-- id: 13 -->

## 5. 测试与验证

- [x] 5.1 性能测试：验证处理 1000 行数据的额外耗时是否小于 50ms。 <!-- id: 14 -->
- [x] 5.2 安全验证：确保普通用户无法通过任何手段（如参数注入）绕过脱敏。 <!-- id: 15 -->