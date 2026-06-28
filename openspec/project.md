# Project Context

## Purpose
**云枢・数据服务平台 (Yunshu Data API Platform)**

该项目（`yovole-yunshu-api-data-platform`）定位为**通用 Data API 平台**。
主要职责是对上屏蔽底层存储的差异，对下统一封装多种数据源（ClickHouse, HBase, MySQL），将大数据平台加工后的结果及各类在线库统一服务化为 REST/JSON API。
它是所有上层应用（如云枢・运营控制台）和 AI 智能体平台（AI Agent Platform）的“取数中枢”，提供统一的认证鉴权、权限控制、查询编排与多数据源路由能力。

## Tech Stack
- **Language**: Python 3.10+
- **Web Framework**: FastAPI
- **ASGI Server**: Uvicorn (standard), Gunicorn
- **Data Validation & Settings**: Pydantic v2, Pydantic Settings
- **Database Drivers/Connectors**:
    - **ClickHouse**: `clickhouse-driver`, `asynch` (async)
    - **MySQL**: `aiomysql` (async)
    - **Redis**: `redis` (async)
- **HTTP Client**: `httpx`
- **Testing**: `pytest`
- **Type Checking**: `mypy`
- **Frontend**: Vue 3 + TailwindCSS + TypeScript (Admin Portal)

## Project Conventions

### Code Style
- **Python**: Follow PEP 8.
- **Typing**: Strict type hints using Python standard `typing` and Pydantic models.
- **Formatting**: Likely standard Python tooling (Black/Isort style implicit, though not explicitly configured in the file list, we follow standard conventions).
- **Naming**:
    - Variables/Functions: `snake_case`
    - Classes: `PascalCase`
    - Constants: `UPPER_CASE`
    - Files: `snake_case.py`

### Architecture Patterns
- **Layered Architecture**:
    - `app/api/v1/endpoints`: Controllers/Routers (HTTP handling, request validation).
    - `app/services`: Business logic, data adaptation (`data_adapter.py`), authentication (`auth_service.py`).
    - `app/core`: Core infrastructure (Configuration `config.py`, Database connections `database.py`, Redis `redis.py`).
    - `app/schemas`: Data Transfer Objects (DTOs) and Pydantic models.
- **Unified Response**: JSON Envelope format `{ code, message, data, timestamp, trace_id }`.
- **Async First**: Extensive use of `async`/`await` for I/O bound operations (DB, Network).

### Testing Strategy
- **Framework**: `pytest` for unit and integration tests.
- **Scope**: Test API endpoints, service logic, and data adapters.

### Git Workflow
- **Commit Messages**: Must be in **Chinese**.
- **Documentation**: All project documentation (Markdown) must be in **Chinese**.
- **Branching**: Standard feature branching workflow.
- **Safety**: No automatic commits unless explicitly requested.

## Domain Context
- **Data Foundation**: The system consumes data from "Yunshu Data Foundation" (ClickHouse/HBase).
- **Consumers**: Primary consumers are "Yunshu Ops Console" (Web UI) and "Yunshu AI Agent Platform".
- **Concepts**:
    - **Region/Room**: Key dimensions for data resource permissioning.
    - **Unified Auth**: Centralized authentication and role-based access control.

## Important Constraints
- **Performance**: High throughput and low latency for data queries are critical.
- **Security**: Strict enforcement of data permissions (Row-level/Column-level security logic via API).
- **Stability**: Must handle connection failures to underlying data sources gracefully.

## External Dependencies
- **ClickHouse**: Primary OLAP storage.
- **MySQL**: Business metadata storage.
- **Redis**: Caching and session management.
- **Yunshu AI Agent Platform**: (Downstream consumer)
- **Yunshu Ops Console**: (Downstream consumer)