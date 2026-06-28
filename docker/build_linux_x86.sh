#!/bin/bash
# 构建 x86_64 Linux 镜像（常见云服务器 / 传统 PC 服务器）
# 平台标识: linux/amd64
set -e
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ -z "$1" ]; then
  echo "错误: 请指定版本号，例如: $0 1.2.0"
  exit 1
fi
export VERSION="$1"
export PLATFORM=linux/amd64
exec "$SCRIPT_DIR/_build_common.sh" "$@"
