#!/bin/bash
# 等待服务就绪脚本

set -e

echo "🔍 Checking service dependencies..."

# 加载环境变量
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# 等待 MySQL
echo "⏳ Waiting for MySQL at ${MYSQL_HOST}:${MYSQL_PORT}..."
timeout=60
counter=0
until nc -z ${MYSQL_HOST} ${MYSQL_PORT} 2>/dev/null; do
    counter=$((counter+1))
    if [ $counter -gt $timeout ]; then
        echo "❌ MySQL is not available after ${timeout}s"
        exit 1
    fi
    sleep 1
done
echo "✅ MySQL is ready"

# 等待 ClickHouse
echo "⏳ Waiting for ClickHouse at ${CLICKHOUSE_HOST}:${CLICKHOUSE_PORT}..."
counter=0
until nc -z ${CLICKHOUSE_HOST} ${CLICKHOUSE_PORT} 2>/dev/null; do
    counter=$((counter+1))
    if [ $counter -gt $timeout ]; then
        echo "❌ ClickHouse is not available after ${timeout}s"
        exit 1
    fi
    sleep 1
done
echo "✅ ClickHouse is ready"

# 等待 Redis
if [ "${REDIS_ENABLE}" = "true" ] || [ "${REDIS_ENABLE}" = "True" ]; then
    echo "⏳ Waiting for Redis at ${REDIS_HOST}:${REDIS_PORT}..."
    counter=0
    until nc -z ${REDIS_HOST} ${REDIS_PORT} 2>/dev/null; do
        counter=$((counter+1))
        if [ $counter -gt $timeout ]; then
            echo "❌ Redis is not available after ${timeout}s"
            exit 1
        fi
        sleep 1
    done
    echo "✅ Redis is ready"
else
    echo "⚠️  Redis check skipped (disabled in config)"
fi

echo ""
echo "🚀 All services are ready! Starting application..."
echo ""
