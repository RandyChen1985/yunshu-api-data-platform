# deployment Specification

## Purpose
TBD - created by archiving change add-docker-deployment. Update Purpose after archive.
## Requirements
### Requirement: Containerization
The system MUST support containerized deployment via Docker.
系统必须支持通过 Docker 进行容器化部署。

#### Scenario: Docker Build
- WHEN running `docker build -f docker/Dockerfile`
- THEN a runnable Docker image containing the API service MUST be created successfully.
- AND the image size SHOULD be optimized (using slim base).

### Requirement: Service Orchestration
The system MUST provide orchestration configurations for both development and production scenarios.
系统必须提供面向开发和生产场景的编排配置。

#### Scenario: Full Stack Startup
- WHEN running `docker-compose up` (using general config)
- THEN API, Redis, and ClickHouse services MUST start and interconnect automatically.

#### Scenario: Standalone Mode
- WHEN running `docker-compose -f docker-compose.api.yml up`
- THEN only the API service MUST start
- AND it MUST be configurable to connect to external databases via environment variables.

### Requirement: Build Automation
The system MUST provide scripts to automate image building and exporting.
系统必须提供脚本以自动化镜像构建和导出。

#### Scenario: Build Script
- WHEN executing `docker/build_linux_x86.sh <version>` or `docker/build_native.sh <version>`
- THEN the script MUST build a versioned image for the target platform
- AND export it to `docker/release/` directory.

