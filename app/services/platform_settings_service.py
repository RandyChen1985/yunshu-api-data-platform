from typing import Any, Dict, Optional

from app.schemas.platform_settings import (
    BrandingPlatformSettings,
    CatalogPlatformSettings,
    DingTalkPlatformSettings,
    McpPlatformSettings,
    PlatformSettingsResponse,
    PlatformSettingsUpdate,
    WeComPlatformSettings,
)
from app.services.branding_settings_service import BrandingSettingsService
from app.services.catalog_service import CatalogService
from app.services.dingtalk_notification_service import DingTalkNotificationService
from app.services.mcp_settings_service import McpSettingsService
from app.services.wecom_notification_service import WeComNotificationService


class PlatformSettingsService:
    @classmethod
    async def get_settings(cls, request_base_url: str = "") -> PlatformSettingsResponse:
        catalog_raw = await CatalogService.get_catalog_settings()
        dingtalk_raw = await DingTalkNotificationService.get_settings()
        wecom_raw = await WeComNotificationService.get_settings()
        mcp_raw = await McpSettingsService.get_settings(request_base_url)
        branding_raw = await BrandingSettingsService.get_raw_settings()
        return PlatformSettingsResponse(
            catalog=CatalogPlatformSettings(**catalog_raw),
            dingtalk=DingTalkPlatformSettings(**dingtalk_raw),
            wecom=WeComPlatformSettings(**wecom_raw),
            mcp=McpPlatformSettings(**mcp_raw),
            branding=BrandingPlatformSettings(**branding_raw),
        )

    @classmethod
    async def update_settings(
        cls,
        body: PlatformSettingsUpdate,
        *,
        request_base_url: str = "",
    ) -> PlatformSettingsResponse:
        if body.catalog is not None:
            await CatalogService.update_catalog_settings(
                default_owner_strategy=body.catalog.default_owner_strategy,
                group_owner_map=body.catalog.group_owner_map,
                notify_resource_change_enabled=body.catalog.notify_resource_change_enabled,
                notify_resource_change_webhook_url=body.catalog.notify_resource_change_webhook_url,
            )
        if body.dingtalk is not None:
            await DingTalkNotificationService.update_settings(
                enabled=body.dingtalk.enabled,
                webhook_url=body.dingtalk.webhook_url,
                secret=body.dingtalk.secret,
                notify_on_request=body.dingtalk.notify_on_request,
                notify_on_result=body.dingtalk.notify_on_result,
            )
        if body.wecom is not None:
            await WeComNotificationService.update_settings(
                enabled=body.wecom.enabled,
                webhook_url=body.wecom.webhook_url,
                secret=body.wecom.secret,
                notify_on_request=body.wecom.notify_on_request,
                notify_on_result=body.wecom.notify_on_result,
            )
        if body.mcp is not None:
            await McpSettingsService.update_settings(
                enabled=body.mcp.enabled,
                instructions=body.mcp.instructions,
            )
        if body.branding is not None:
            await BrandingSettingsService.update_settings(
                enabled=body.branding.enabled,
                product_name=body.branding.product_name,
                login_subtitle=body.branding.login_subtitle,
                icon_url=body.branding.icon_url,
                hide_login_sso=body.branding.hide_login_sso,
                hide_version_link=body.branding.hide_version_link,
                contact_markdown=body.branding.contact_markdown,
                copyright_text=body.branding.copyright_text,
            )
        return await cls.get_settings(request_base_url)

    @classmethod
    async def get_catalog_dict(cls) -> Dict[str, Any]:
        return (await cls.get_settings()).catalog.model_dump()
