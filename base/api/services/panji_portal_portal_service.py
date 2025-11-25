import logging
from dataclasses import dataclass
from typing import Dict, Any

from base.api.services.base_service import BaseService
from core import DataCache


@dataclass
class PortalSignEntity(object):
    username: str = None
    password: str = None
    tenant_code: str = None
    expire_time: int = 18000000

class PanJiPortalService(BaseService):

    DEFAULT_BASE_URL = 'http://openapi.portal.nbpod3-31-181-20030.4a.cmit.cloud:20030'

    def __init__(self, base_url: str = None, logger: logging.Logger = None):
        """
        初始化 Panji Portal 服务

        Args:
            base_url: API 基础 URL，默认使用 JSONPlaceholder 官方地址
            logger: 日志记录器
        """
        super().__init__(
            base_url=base_url or self.DEFAULT_BASE_URL,
            logger=logger
        )
        self.logger.info(f"Initializing PanJi Service with base_url: {self.base_url}")

    def get_token(self, panji_sign: PortalSignEntity) -> Dict[str, Any]:
        """
        登陆获取Token

        Args:
            panji_sign: PortalSignEntity (
                username: str
                password: str
                tenant_code: str
                expire_time: int = 18000000
            )

        Returns:
            Dict[str, Any]
        """
        self.logger.info(f"Getting PanJi Token")
        sign_info = {
            "userName": panji_sign.username,
            "password": panji_sign.password,
            "tenantCode": panji_sign.tenant_code,
            "expireTime": panji_sign.expire_time,
        }
        response = self.post("/apisix/plugin/jwt/sign", json=sign_info)
        return response.json()

    def get_first_field_info(self) -> Dict[str, Any]:
        """
        获取一级域信息

        Returns:
            Dict[str, Any]
        """
        self.logger.info(f"Getting First Field Info")
        cache = DataCache.get_instance()
        headers = {
            "Authorization": cache.get("token"),
        }
        response = self.get(endpoint="/openapi/portal/restApi/firstFieldInfo/list", headers=headers)
        return response.json()

    def get_second_field_info(self) -> Dict[str, Any]:
        """
        获取二级域信息

        Returns:
            Dict[str, Any]
        """
        self.logger.info(f"Getting Second Field Info")
        cache = DataCache.get_instance()
        headers = {
            "Authorization": cache.get("token"),
        }
        response = self.get(endpoint="/openapi/portal/restApi/secondFieldInfo/list", headers=headers)
        return response.json()
