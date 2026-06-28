# 提案：容器化部署 (Docker Deployment)

## Why
- **一致性 (Consistency)**: 消除开发环境与生产环境的差异 (It was working on my machine)。
- **交付标准 (Delivery)**: 满足现代化微服务交付要求，便于 DevOps 流程集成。
- **快速启动 (Quick Start)**: 允许新成员一键启动所有依赖服务 (Redis, ClickHouse Mock) 进行开发。

## What Changes
- **新增配置**:
  - `docker/Dockerfile`: API 服务镜像构建定义。
  - `docker/docker-compose.yml`: 全栈开发环境编排。
  - `docker/docker-compose.api.yml`: 生产环境/独立部署编排。
  - `docker/build.sh`: 镜像构建脚本。
- **文档更新**: 更新 `docker/README.md` 和根目录 `README.md`。
- **构建产物**: 增加 `docker/release/` 目录用于存放 tar 包 (Git 忽略)。

## Risks
- **镜像体积**: Python Slim 镜像相对较小，但如果添加因赖过多需关注体积控制。
- **端口冲突**: 默认 compose 使用 8000/6379/8123 等端口，可能与本地服务冲突。
