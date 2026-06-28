# 提案：集成前端构建到 Docker

## 摘要 (Summary)
更新 Docker 构建流程，使其自动编译 Vue.js 前端并将静态资源包含在最终的 Docker 镜像中。这确保了 Docker 镜像成为一个包含 API 后端和管理门户前端的独立、可部署单元。

## 背景 (Background)
目前，`Dockerfile` 仅打包了 Python 后端。前端必须单独构建并手动放置在主机或容器中，这容易出错并使部署变得复杂。

## 目标 (Goals)
-   **自动化构建**：Docker 构建命令触发前端编译。
-   **单一镜像**：一个 Docker 镜像包含运行平台所需的一切。
-   **简化部署**：将部署步骤减少为仅需“运行容器”。

## 非目标 (Non-Goals)
-   使用 Nginx 替换 FastAPI StaticFiles（FastAPI 内置的静态服务目前已足够）。
