# 自动化测试指南 (Automated Testing Guide)

本项目使用 `pytest` + `httpx` (AsyncClient) 构建自动化集成测试框架。测试直接针对 FastAPI 应用实例运行，**无需**预先启动 `uvicorn` 服务。

## 1. 快速开始

### 方式一：使用测试脚本（推荐）

```bash
# 在项目根目录执行
./tests/run_tests.sh

# 或者在 tests 目录中执行
cd tests && ./run_tests.sh
```

测试脚本会自动：
- 设置正确的 PYTHONPATH
- 检测 pytest 是否安装
- 运行所有测试

### 方式二：手动执行 pytest

在项目根目录下执行以下命令：

```bash
# 运行所有测试
export PYTHONPATH=$PYTHONPATH:. 
python3 -m pytest tests/

# 运行特定模块的测试
python3 -m pytest tests/api/v1/test_resources_donghuan.py

# 显示详细输出
python3 -m pytest tests/ -v

# 显示测试覆盖率
python3 -m pytest tests/ --cov=app
```

## 2. 环境要求

- 确保依赖已安装：
  ```bash
  pip install -r requirements.txt
  ```
- 确保本地数据库（ClickHouse, MySQL, Redis）已启动且配置正确（参考 `.env` 文件）。

## 3. 目录结构

```text
tests/
├── conftest.py          # 测试固件配置 (Fixtures)
│   ├── client           # 异步 HTTP 客户端 (httpx.AsyncClient)
│   └── valid_api_key    # 测试用的合法 API Key
├── run_tests.sh         # 一键测试脚本（自动配置环境）
├── api/
│   ├── portal/          # Portal 管理接口测试
│   │   └── test_*.py
│   └── v1/              # V1 数据接口测试
│       └── test_*.py
└── README.md            # 本指南
```

## 4. 常见问题

### Q: 为什么会出现 `RuntimeError: Event loop is closed`?
**A**: 这是 `pytest-asyncio` 在 Python 3.13 环境下清理异步资源（如 Redis 连接池）时的一个已知副作用。
如果你的测试摘要显示 `N passed`（例如 `2 passed`），说明业务逻辑测试是**成功**的。该错误发生在测试结束后的清理阶段，不影响代码功能的正确性验证。

### Q: 需要先启动 API 服务吗？
**A**: **不需要**。
测试框架使用 `ASGITransport` 直接与 FastAPI 应用实例交互。测试运行时会自动触发应用的生命周期事件（如初始化数据库连接池），测试结束后自动关闭。
