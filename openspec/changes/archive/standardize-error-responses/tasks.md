# 任务清单：统一全局异常响应格式

## 核心代码实现
- [ ] 在 `app/main.py` 中引入 `Request`, `JSONResponse`, `HTTPException` 和 `BaseResponse` 相关依赖 <!-- id: 0 -->
- [ ] 实现 `http_exception_handler` 函数，格式化 HTTP 错误响应 <!-- id: 1 -->
- [ ] 实现 `general_exception_handler` 函数，格式化 500 错误响应 <!-- id: 2 -->
- [ ] 在 `app` 实例中注册这两个异常处理器 <!-- id: 3 -->

## 测试验证
- [ ] 编写测试用例 `tests/core/test_error_handling.py`，模拟 403 和 500 错误场景 <!-- id: 4 -->
- [ ] 运行测试确保响应格式符合预期 <!-- id: 5 -->
