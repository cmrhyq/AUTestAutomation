import json
import os.path
from typing import Dict

import allure
import pytest

from base.api.services.panji_service import PanJiService
from config import env_manager, Settings, EnvironmentManager
from model.entity.panji_entity import PanjiSignEntity


@pytest.mark.api
@allure.feature("PanJi Service API")
@allure.story("用户管理")
class TestPanjiAPI:
    @pytest.fixture(scope="class")
    def env_config(self):
        env_file = os.path.join(Settings.PROJECT_ROOT, "test_data", "env_config.json")
        env = EnvironmentManager(env_file).get_config()
        yield env

    @pytest.fixture(scope="class")
    def panji_service(self, api_logger):
        service = PanJiService(logger=api_logger)
        yield service
        service.close()

    @allure.title("测试获取Token")
    @allure.description("验证能够成功获取Token数据")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_token(self, panji_service, env_config, api_cache, api_logger):
        with allure.step("发送 POST 请求获取Token"):
            panji_sign = PanjiSignEntity(
                username=env_config.basic_auth_username,
                password=env_config.basic_auth_password,
                tenant_code="monitor-group"
            )
            sign_info = panji_service.get_token(panji_sign)

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