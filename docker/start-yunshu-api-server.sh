#!/bin/bash

# 云枢数据服务平台 - Docker 启动脚本
# 用途：启动 API 服务容器（依赖外部 MySQL/ClickHouse/Redis）

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

COMPOSE_FILE="docker-compose.api.yml"
CONTAINER_NAME="yunshu-api"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== 云枢数据服务平台 Docker 启动 ===${NC}"

if [ ! -f ".env" ]; then
    echo -e "${RED}错误: .env 文件不存在${NC}"
    echo "请先复制 env.example 到 docker 目录: cp ../env.example .env"
    exit 1
fi

if ! docker images | grep -q "yunshu-api"; then
    echo -e "${YELLOW}警告: yunshu-api 镜像不存在${NC}"
    echo "请先构建镜像，例如: ./build_linux_x86.sh 1.2.0"
    exit 1
fi

if [ "$(docker ps -aq -f name=${CONTAINER_NAME})" ]; then
    echo -e "${YELLOW}停止并删除旧容器...${NC}"
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
fi

echo -e "${GREEN}启动 API 容器...${NC}"
if docker compose version >/dev/null 2>&1; then
    docker compose -f "$COMPOSE_FILE" up -d
else
    docker-compose -f "$COMPOSE_FILE" up -d
fi

echo -e "${YELLOW}等待服务启动并检查依赖连接...${NC}"
sleep 5

echo -e "${YELLOW}检查数据库连接状态...${NC}"
docker logs "$CONTAINER_NAME" 2>&1 | grep -E "(Connecting to|connected successfully|Redis)" || true
echo ""

if [ "$(docker ps -q -f name=${CONTAINER_NAME})" ]; then
    echo -e "${GREEN}✓ 服务启动成功！${NC}"
    echo ""
    echo "服务信息:"
    echo "  - API 地址: http://localhost:8000"
    echo "  - API 文档: http://localhost:8000/docs"
    echo "  - 管理后台: http://localhost:8000/"
    echo ""
    echo "查看日志: docker logs -f ${CONTAINER_NAME}"
    echo "停止服务: ./stop-yunshu-api-server.sh"
else
    echo -e "${RED}✗ 服务启动失败${NC}"
    echo "查看日志: docker logs ${CONTAINER_NAME}"
    exit 1
fi
