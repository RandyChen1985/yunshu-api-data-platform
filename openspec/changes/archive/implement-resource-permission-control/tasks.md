# 任务清单：实现资源权限控制

## 核心逻辑实现
- [ ] 修改 `app/core/dependencies.py`，实现 `verify_resource_access` 和 `check_resource_permission` <!-- id: 0 -->
- [ ] 修改 `app/api/v1/endpoints/resources.py`，为每个端点添加权限检查依赖 <!-- id: 1 -->
- [ ] 修改 `app/api/v1/endpoints/query.py`，在通用查询中添加权限检查逻辑 <!-- id: 2 -->

## 测试验证
- [ ] 编写测试用例 `tests/api/v1/test_permission.py`，覆盖授权和未授权场景 <!-- id: 3 -->
- [ ] 执行测试并确保通过 <!-- id: 4 -->
