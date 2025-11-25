import json
import os.path
from typing import Dict

import allure
import pytest

from base.api.fixtures import api_cache
from base.api.services.panji_portal_portal_service import PanJiPortalService, PortalSignEntity


@pytest.mark.api
@allure.feature("磐基门户服务API")
@allure.story("统一门户")
class TestPanjiPortalAPI:

    @pytest.fixture(scope="class")
    def portal_service(self, api_logger):
        """创建 Panji Portal 服务实例"""
        service = PanJiPortalService(logger=api_logger)
        yield service
        service.close()

    @allure.title("测试获取Token")
    @allure.description("验证能够成功获取Token数据")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_token(self, portal_service, api_env, api_cache, api_logger):
        with allure.step("发送 POST 请求获取Token"):
            panji_sign = PortalSignEntity(
                username=api_env.get("basic_auth_username"),
                password=api_env.get("basic_auth_password"),
                tenant_code=api_env.get("tenant_code")
            )
            sign_info = portal_service.get_token(panji_sign)

        with allure.step("验证响应数据"):
            assert isinstance(sign_info, Dict), "响应应该是字典类型"
            assert "data" in sign_info, "响应应包含Token"
            assert sign_info["code"] == 200, "响应Code应等于200"

        with allure.step("缓存Token供后续使用"):
            api_cache.set("token", sign_info["data"])
            api_logger.info(f"已经登陆并缓存Token: {sign_info['data']}")

        allure.attach(
            str(sign_info),
            name="登陆响应信息",
            attachment_type=allure.attachment_type.JSON
        )

    @allure.title("测试获取一级域")
    @allure.description("验证能够成功获取一级域数据")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_first_field_info(self, portal_service, api_cache, api_logger):
        with allure.step("发送 GET 请求获取一级域"):
            first_field = portal_service.get_first_field_info()

        with allure.step("验证响应数据"):
            assert isinstance(first_field, Dict), "响应应该是字典类型"
            assert first_field["code"] == 0, "响应Code应等于0"

        with allure.step("缓存一级域id数据"):
            api_cache.set("firstFieldId", first_field["data"][0]["systemId"])
            api_logger.info(f"已缓存一级域Id: {first_field['data'][0]['systemId']}")

        allure.attach(
            str(first_field),
            name="一级域信息",
            attachment_type=allure.attachment_type.JSON
        )

    @allure.title("测试获取二级域")
    @allure.description("验证能够成功获取二级域数据")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_second_field_info(self, portal_service, api_cache, api_logger):
        with allure.step("发送 GET 请求获取二级域"):
            second_field = portal_service.get_second_field_info()

        with allure.step("验证响应数据"):
            assert isinstance(second_field, Dict), "响应应该是字典类型"
            assert second_field["code"] == 0, "响应Code应等于0"

        with allure.step("缓存二级域id数据"):
            api_cache.set("secondFieldId", second_field["data"][0]["moduleId"])
            api_logger.info(f"已缓存二级域Id: {second_field['data'][0]['moduleId']}")

        allure.attach(
            str(second_field),
            name="二级域信息",
            attachment_type=allure.attachment_type.JSON
        )
