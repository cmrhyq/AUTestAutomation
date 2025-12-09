import logging
from typing import Dict, Any

from base.api.services.base_service import BaseService
from config import env_manager


class PanJiPortalInnerService(BaseService):
    DEFAULT_BASE_URL = 'http://openapi.portal.nbpod3-31-181-20030.4a.cmit.cloud:20030'

    def __init__(self, base_url: str = None, logger: logging.Logger = None):
        """
        初始化 Panji Portal InnerAPI 服务

        Args:
            base_url: API 基础 URL
            logger: 日志记录器
        """
        super().__init__(
            base_url=base_url or self.DEFAULT_BASE_URL,
            logger=logger
        )
        self.logger.info(f"Initializing PanJi InnerAPI Service with base_url: {self.base_url}")

    def get_user_full_data(self) -> Dict[str, Any]:
        """
        获取用户全量数据

        Returns:
            Dict[str, Any]
        """
        self.logger.info(f"Getting User's Full Data")
        # 本地调用时需要在portal后加入/server，其他情况则去除
        url = "/portal/server/api/user/list"
        headers = {
            "apikey": env_manager.get_config().get("apikey"),
            "tenantCode": env_manager.get_config().get("tenant_code"),
            "x-app-id": "portal",
        }
        response = self.get(endpoint=url, headers=headers)
        return response.json()
