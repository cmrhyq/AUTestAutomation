import logging
from dataclasses import dataclass
from typing import Dict, Any

from base.api.services.base_service import BaseService
from core import DataCache


@dataclass
class PanjiSignEntity(object):
    username: str = None
    password: str = None
    tenant_code: str = None
    expire_time: int = 18000000

class PanJiService(BaseService):

    DEFAULT_BASE_URL = 'http://openapi.portal.nbpod3-31-181-20030.4a.cmit.cloud:20030'

    def __init__(self, base_url: str = None, logger: logging.Logger = None):
        super().__init__(
            base_url=base_url or self.DEFAULT_BASE_URL,
            logger=logger
        )
        self.logger.info(f"Initializing PanJi Service with base_url: {self.base_url}")

    def get_token(self, panji_sign: PanjiSignEntity) -> Dict[str, Any]:
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
        self.logger.info(f"Getting First Field Info")
        cache = DataCache.get_instance()
        headers = {
            "Authorization": cache.get("token"),
        }
        response = self.get(endpoint="/openapi/portal/restApi/firstFieldInfo/list", headers=headers)
        return response.json()