"""python -m nanzi_mcp — stdio 模式启动南孜 MCP Server（供 Cursor / Claude Desktop 使用）。"""

import asyncio
import os
import sys


async def _main() -> None:
    if not os.getenv("NANZI_API_KEY"):
        print(
            "错误: 请设置环境变量 NANZI_API_KEY（南孜数据平台 API Key）",
            file=sys.stderr,
        )
        sys.exit(1)

    from nanzi_mcp.client import NanZiApiClient
    from nanzi_mcp.server import create_mcp_server_from_db, ensure_mcp_enabled

    try:
        status = await NanZiApiClient().mcp_status()
        if not status.get("enabled"):
            print(status.get("message") or "MCP Server 未启用", file=sys.stderr)
            sys.exit(1)
    except Exception as exc:
        print(f"无法连接数据平台检查 MCP 状态: {exc}", file=sys.stderr)
        sys.exit(1)

    await ensure_mcp_enabled()
    mcp = await create_mcp_server_from_db()
    await mcp.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(_main())
