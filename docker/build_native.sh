#!/bin/bash
# 按当前机器原生架构构建（Mac M 系=arm64，x86 Mac/Linux=amd64）
# 适合本机 docker run 调试；部署到服务器请用 build_linux_x86.sh 或 build_linux_arm.sh
set -e
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ -z "$1" ]; then
  echo "错误: 请指定版本号，例如: $0 1.2.0"
  exit 1
fi
export VERSION="$1"
unset PLATFORM
exec "$SCRIPT_DIR/_build_common.sh" "$@"
