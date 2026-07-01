"""目录权限审批通知：并行推送至已启用的 IM 群机器人通道。"""
import logging
from typing import Optional

from app.services.dingtalk_notification_service import DingTalkNotificationService
from app.services.wecom_notification_service import WeComNotificationService

logger = logging.getLogger(__name__)


class ApprovalNotificationService:
    @classmethod
    async def notify_access_request_created(
        cls,
        *,
        request_id: int,
        product_key: str,
        product_name: str,
        applicant_name: str,
        message: Optional[str] = None,
    ) -> None:
        kwargs = dict(
            request_id=request_id,
            product_key=product_key,
            product_name=product_name,
            applicant_name=applicant_name,
            message=message,
        )
        try:
            await DingTalkNotificationService.notify_access_request_created(**kwargs)
        except Exception as e:
            logger.warning("DingTalk access request notification failed: %s", e)
        try:
            await WeComNotificationService.notify_access_request_created(**kwargs)
        except Exception as e:
            logger.warning("WeCom access request notification failed: %s", e)

    @classmethod
    async def notify_access_request_handled(
        cls,
        *,
        request_id: int,
        product_key: str,
        product_name: str,
        applicant_name: str,
        approved: bool,
        handler_name: str,
        remark: Optional[str] = None,
    ) -> None:
        kwargs = dict(
            request_id=request_id,
            product_key=product_key,
            product_name=product_name,
            applicant_name=applicant_name,
            approved=approved,
            handler_name=handler_name,
            remark=remark,
        )
        try:
            await DingTalkNotificationService.notify_access_request_handled(**kwargs)
        except Exception as e:
            logger.warning("DingTalk approval notification failed: %s", e)
        try:
            await WeComNotificationService.notify_access_request_handled(**kwargs)
        except Exception as e:
            logger.warning("WeCom approval notification failed: %s", e)
