# 设计：Docker 多阶段构建

## 架构 (Architecture)
我们将利用 Docker **多阶段构建 (Multi-Stage Builds)** 来保持最终镜像体积小巧，同时仅在构建阶段包含必要的构建工具。

### 阶段 1：前端构建器 (`frontend-builder`)
-   **基础镜像**：`node:20-slim` (轻量级 Node 环境)
-   **输入**：`frontend/` 源代码。
-   **动作**：`npm install && npm run build`。
-   **输出**：包含静态资源的 `frontend/dist/` 目录。

### 阶段 2：最终运行时 (`backend`)
-   **基础镜像**：`python:3.10-slim` (与当前一致)
-   **输入**：
    -   Python 源码 (`app/`, `requirements.txt`).
    -   **COPY --from=frontend-builder**: `dist/` -> `/app/frontend/dist`.
-   **动作**：安装 Python 依赖，启动 `uvicorn`。

## 权衡 (Trade-offs)
-   **构建时间**：由于需要执行 `npm install` 和 `build`，构建时间会增加。
-   **镜像大小**：应保持大致相同（仅增加极少的静态文件），实际上比分开的镜像更小且高效。
