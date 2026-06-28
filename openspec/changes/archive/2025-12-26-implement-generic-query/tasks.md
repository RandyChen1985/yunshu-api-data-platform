# 任务：实现通用查询接口 (Implement Generic Query)

- [ ] 创建 `app/api/v1/endpoints/query.py` <!-- id: 0 -->
    - 定义 `LogicalQueryRequest` Schema (Pydantic)
    - 实现 `POST /` 路由处理函数
    - 集成 `adapter.execute(query)`
- [ ] 注册路由到 `app/main.py` <!-- id: 1 -->
    - 添加 `app.include_router(query.router, prefix="/api/v1/query", tags=["query"])`
- [ ] 编写测试用例 `tests/api/v1/test_query.py` <!-- id: 2 -->
    - 测试正常查询 (Happy Path)
    - 测试非法资源名 (Security)
    - 测试参数校验 (Validation)
- [ ] 更新 `tests/CHECKLIST.md` <!-- id: 3 -->
