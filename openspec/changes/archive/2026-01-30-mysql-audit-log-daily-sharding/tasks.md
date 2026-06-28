# Tasks: MySQL 审计日志按日物理分表

## 第一阶段：模板与基建
- [x] 1. 创建 V14 SQL 脚本：建立 `api_access_logs_template` 模板表。
- [x] 2. 编写 `app/utils/sharding.py`：实现 `ensure_audit_table_exists` 逻辑（带内存缓存）。

## 第二阶段：中间件改造
- [x] 3. 修改 `app/core/middleware.py`：
    - [x] 动态计算 `api_access_logs_yyyyMMdd`。
    - [x] 实现合并写入逻辑（主表+扩展字段）。
    - [x] 移除对旧扩展表 `api_access_logs_ext` 的写入。

## 第三阶段：查询层重构
- [x] 4. 重构 `app/api/portal/endpoints/audit.py`：
    - [x] 移除 Join 逻辑。
    - [x] 实现跨天查询的 `UNION ALL` 动态构建逻辑（增加表存在性校验）。
- [x] 5. 适配 Dashboard (今日统计) 到当天的物理表，并确保表不存在时优雅降级。
- [x] 6. 适配 `app/api/portal/endpoints/logs.py` 的 access 日志接口。

## 第四阶段：任务与清理
- [x] 7. 更新 `app/jobs/aggregator.py`：使其支持扫描当天的物理表及历史回填。
- [x] 8. 修改 `app/jobs/cleaner.py`：实现按 `sys_config` 保留天数执行 `DROP TABLE`。

## 验证与维护
- [x] 9. 适配所有自动化测试用例 (`tests/`)。
- [x] 10. 修复前端 `ResourceList.vue` 的编译错误。