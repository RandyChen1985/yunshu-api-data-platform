## 1. 数据库准备

- [ ] 1.1 创建 SQL 迁移脚本 `db-prod/V15-add-datasource-sort-order.sql`，新增 `sort_order` 字段。
- [ ] 1.2 执行迁移脚本更新本地数据库。

## 2. 后端开发

- [ ] 2.1 修改 `app/schemas/datasource.py`，在 `DataSourceInternal` 和 `DataSourceResponse` 中添加 `sort_order` 字段。
- [ ] 2.2 修改 `app/services/datasource_service.py` 中的 `list_datasources` 方法，增加排序逻辑。
- [ ] 2.3 在 `app/services/datasource_service.py` 中新增 `reorder_datasources` 方法，实现批量更新逻辑。
- [ ] 2.4 在 `app/api/portal/endpoints/datasource.py` 中新增 `PUT /reorder` 路由。

## 3. 前端开发

- [ ] 3.1 在 `frontend` 目录安装 `vuedraggable` 依赖。
- [ ] 3.2 修改 `frontend/src/views/datasource/DataSourceList.vue`，引入并配置拖拽功能。
- [ ] 3.3 实现拖拽结束后的 `handleDragEnd` 逻辑，调用后端 `reorder` API。
- [ ] 3.4 检查并确认 SQL Lab 等页面的数据源列表顺序已同步更新。

## 4. 验证与测试

- [ ] 4.1 编写单元测试验证 `reorder_datasources` 服务层逻辑。
- [ ] 4.2 自动化测试：手动验证拖拽后刷新页面，顺序是否保持一致。
- [ ] 4.3 更新 `tests/CHECKLIST.md`，添加排序功能测试项。
