#!/bin/bash
# 修复 Homebrew docker + Colima 环境下 buildx 不可用的问题
set -e

PLUGIN_DIR="${HOME}/.docker/cli-plugins"
mkdir -p "$PLUGIN_DIR"

install_via_brew() {
  if ! command -v brew >/dev/null 2>&1; then
    echo "错误: 未找到 Homebrew，请手动安装 docker-buildx"
    echo "  https://github.com/docker/buildx#installing"
    exit 1
  fi
  echo "=== 通过 Homebrew 安装 docker-buildx ==="
  brew install docker-buildx
  local brew_bin
  brew_bin="$(brew --prefix docker-buildx)/bin/docker-buildx"
  if [[ ! -x "$brew_bin" ]]; then
    echo "错误: 安装后未找到 $brew_bin"
    exit 1
  fi
  ln -sf "$brew_bin" "$PLUGIN_DIR/docker-buildx"
  echo "已链接: $PLUGIN_DIR/docker-buildx -> $brew_bin"
}

if [[ -L "$PLUGIN_DIR/docker-buildx" ]] && [[ ! -e "$PLUGIN_DIR/docker-buildx" ]]; then
  echo "移除失效的 docker-buildx 软链（原指向 Docker Desktop）"
  rm -f "$PLUGIN_DIR/docker-buildx"
fi

if docker buildx version >/dev/null 2>&1; then
  echo "docker buildx 已可用: $(docker buildx version | head -1)"
  exit 0
fi

install_via_brew

echo ""
echo "=== 验证 ==="
docker buildx version
echo ""
echo "请重新执行: ./build_linux_x86.sh <version>"
