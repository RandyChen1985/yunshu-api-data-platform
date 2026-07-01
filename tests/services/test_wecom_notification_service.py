"""企业微信群机器人通知服务测试"""
from unittest.mock import AsyncMock, patch

import pytest

from app.services.wecom_notification_service import WeComNotificationService


@pytest.mark.asyncio
async def test_send_markdown_skips_when_disabled():
    with patch.object(
        WeComNotificationService,
        "get_settings",
        new=AsyncMock(return_value={"enabled": False, "webhook_url": "https://example.com", "secret": ""}),
    ):
        ok = await WeComNotificationService.send_markdown("test")
    assert ok is False


@pytest.mark.asyncio
async def test_send_markdown_posts_wecom_payload():
    with patch("app.services.wecom_notification_service.httpx.AsyncClient") as mock_client_cls:
        mock_response = AsyncMock()
        mock_response.json.return_value = {"errcode": 0}
        mock_response.raise_for_status = lambda: None
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_cls.return_value = mock_client

        ok = await WeComNotificationService.send_markdown(
            "### hello",
            webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
            secret="",
            require_enabled=False,
        )

    assert ok is True
    call_kwargs = mock_client.post.await_args
    assert call_kwargs.kwargs["json"]["msgtype"] == "markdown"
    assert call_kwargs.kwargs["json"]["markdown"]["content"] == "### hello"


@pytest.mark.asyncio
async def test_notify_access_request_created_respects_on_request_flag():
    with patch.object(
        WeComNotificationService,
        "get_settings",
        new=AsyncMock(
            return_value={
                "enabled": True,
                "notify_on_request": False,
                "notify_on_result": True,
            }
        ),
    ), patch.object(WeComNotificationService, "send_markdown", new=AsyncMock()) as mock_send:
        await WeComNotificationService.notify_access_request_created(
            request_id=1,
            product_key="p1",
            product_name="产品",
            applicant_name="user1",
        )
    mock_send.assert_not_called()
