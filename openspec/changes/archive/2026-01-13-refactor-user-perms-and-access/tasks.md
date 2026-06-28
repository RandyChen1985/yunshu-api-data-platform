# 任务清单

## 用户管理 UI
- [x] 重构 `frontend/src/views/Users.vue`，在创建/编辑弹窗中使用标签页界面。 <!-- id: 1 -->
- [x] 将“基础信息”（用户名、角色、备注）移至第一个标签页。 <!-- id: 2 -->
- [x] 将“权限分配”（资源授权）移至第二个标签页，且仅在角色为“普通用户”时可见。 <!-- id: 3 -->

## 接口管理访问控制
- [x] 更新 `frontend/src/views/Dashboard.vue`，向所有用户显示“接口管理”菜单。 <!-- id: 4 -->
- [x] 更新 `frontend/src/views/resources/ResourceList.vue`，对非管理员用户隐藏“新建”、“编辑”、“删除”和“状态切换”操作。 <!-- id: 5 -->
- [x] 更新 `frontend/src/views/resources/ResourceEdit.vue`，对非管理员用户禁用所有表单字段并隐藏“保存”按钮。 <!-- id: 6 -->
- [x] 更新 `app/api/portal/endpoints/meta.py`，允许普通用户进行 `GET` 请求（列出/获取资源）以及内省接口（表、列查询）。 <!-- id: 7 -->
- [x] 验证 `app/api/portal/endpoints/meta.py` 对 `POST`、`PUT`、`DELETE` 操作强制执行管理员权限校验。 <!-- id: 8 -->
