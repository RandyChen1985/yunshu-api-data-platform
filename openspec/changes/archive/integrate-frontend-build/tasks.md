# 任务：集成前端构建

- [x] 更新 `Dockerfile` 以支持多阶段构建。
    - [x] 添加 Node.js 构建阶段。
    - [x] 复制 `frontend/` 源码。
    - [x] 运行 `npm install` 和 `npm run build`。
    - [x] 将 `dist/` 复制到后端阶段。
- [ ] 验证 Docker 构建 (`./docker/build.sh`)。
- [ ] 验证运行容器能正确服务前端页面。
