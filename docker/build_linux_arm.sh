#!/bin/bash
# 构建 ARM64 Linux 镜像（鲲鹏、Ampere、树莓派 64 位等）
# 平台标识: linux/arm64
set -e
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ -z "$1" ]; then
  echo "错误: 请指定版本号，例如: $0 1.2.0"
  exit 1
fi
export VERSION="$1"
export PLATFORM=linux/arm64
exec "$SCRIPT_DIR/_build_common.sh" "$@"
