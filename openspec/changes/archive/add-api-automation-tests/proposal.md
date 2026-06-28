# Change: Add API Automation Testing Mechanism

## Why
目前项目缺乏自动化的测试机制，每次开发新接口后需要手动验证，效率低且容易引入回归问题。
为了保证后续快速迭代（如补全剩余 4 个接口）的质量，需要建立一套自动化的 API 测试框架。

## What Changes
1.  **引入测试框架**: 使用 `pytest` + `httpx` (AsyncClient) + `pytest-asyncio` 构建异步测试环境。
2.  **建立测试脚手架**: 创建 `tests/` 目录结构，配置 `conftest.py` 以管理 FastAPI app 实例和数据库连接生命周期。
3.  **实现首个接口测试**: 编写针对 `/api/v1/resources/donghuan/real-metrics` 的集成测试用例，验证状态码、数据结构和业务逻辑。
4.  **依赖更新**: 添加 `pytest-asyncio` 到 `requirements.txt`。

## Impact
-   **Affected Specs**: `testing` (New Capability)
-   **Affected Code**:
    -   `tests/` (New directory)
    -   `requirements.txt`
    -   `scripts/run_tests.sh` (Optional helper)
