# 部署规范 (Deployment Specifications)

## ADDED Requirements

### Requirement: Docker 镜像组成 (Docker Image Composition)

生产环境的 Docker 镜像必须 (MUST) 包含运行完整应用程序（后端 API + 前端 UI）所需的所有组件，无需外部文件挂载。

#### Scenario: 全栈可用 (Full Stack Available)
-   **Given** 从 `nanzi-api` 镜像启动的运行中容器
-   **When** 用户访问根 URL `/`
-   **Then** 管理门户前端 (SPA) 应该加载。

#### Scenario: 前端构建 (Frontend Build)
-   **Given** 源代码
-   **When** 执行 `docker build`
-   **Then** Vue.js 应用程序应该从源码编译。
-   **And** 生成的产物应该被放置在 `frontend/dist` 中。
