import logging
from dataclasses import dataclass
from typing import Dict, Any

from base.api.services.base_service import BaseService
from core import DataCache


@dataclass
class PortalUserEntity(object):
    user_id: str = None
    username: str = None
    password: str = None
    tenant_code: str = None
    phone: str = None
    email: str = None
    expire_time: int = 18000000

@dataclass
class ClusterPlaneEntity(object):
    instance_id: str = None
    prod_inst_name: str = None


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

    def get_token(self, panji_sign: PortalUserEntity) -> Dict[str, Any]:
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
        url = "/apisix/plugin/jwt/sign"
        sign_info = {
            "userName": panji_sign.username,
            "password": panji_sign.password,
            "tenantCode": panji_sign.tenant_code,
            "expireTime": panji_sign.expire_time,
        }
        response = self.post(endpoint=url, json=sign_info)
        return response.json()

    def get_first_field_info(self) -> Dict[str, Any]:
        """
        获取一级域信息

        Returns:
            Dict[str, Any]
        """
        self.logger.info(f"Getting First Field Info")
        url = "/openapi/portal/restApi/firstFieldInfo/list"
        cache = DataCache.get_instance()
        headers = {
            "Authorization": cache.get("token"),
        }
        response = self.get(endpoint=url, headers=headers)
        return response.json()

    def get_second_field_info(self) -> Dict[str, Any]:
        """
        获取二级域信息

        Returns:
            Dict[str, Any]
        """
        self.logger.info(f"Getting Second Field Info")
        url = "/openapi/portal/restApi/secondFieldInfo/list"
        cache = DataCache.get_instance()
        headers = {
            "Authorization": cache.get("token"),
        }
        response = self.get(endpoint=url, headers=headers)
        return response.json()

    def create_cluster_plane(self, cluster_info: ClusterPlaneEntity) -> Dict[str, Any]:
        """
        新增集群平面单元
        """
        self.logger.info(f"Create cluster plane")
        url = "/openapi/portal/restApi/cluster/add"
        cache = DataCache.get_instance()
        headers = {
            "Authorization": cache.get("token"),
        }
        body = {
            "prodInstName": cluster_info.prod_inst_name,
            "prodInstCode": cluster_info.prod_inst_name,
            "prodInstType": "k8s",
            "caCert": None,
            "clientCert": None,
            "envCode": "生产环境",
            "planeCode": "a",
            "cellCode": "a",
            "endPoints": None,
            "context": None,
            "planeName": "a",
            "cellName": "a",
            "envName": "生产环境"
        }
        response = self.post(endpoint=url, json=body, headers=headers)
        return response.json()

    def query_cluster_plane(self, cluster_info: ClusterPlaneEntity) -> Dict[str, Any]:
        """
        查询集群平面单元
        """
        self.logger.info(f"Query cluster plane")
        url = "/openapi/portal/restApi/cluster/list"
        cache = DataCache.get_instance()
        headers = {
            "Authorization": cache.get("token"),
        }
        params = {
            "prodInstName": cluster_info.prod_inst_name,
        }
        response = self.get(endpoint=url, params=params, headers=headers)
        return response.json()

    def update_cluster_plane(self, cluster_info: ClusterPlaneEntity) -> Dict[str, Any]:
        """
        修改集群平面单元
        """
        self.logger.info(f"Update cluster plane")
        url = "/openapi/portal/restApi/cluster/update"
        cache = DataCache.get_instance()
        headers = {
            "Authorization": cache.get("token"),
        }
        body = {
            "instanceId": cluster_info.instance_id,
            "prodInstCode": cluster_info.prod_inst_name,
            "prodInstName": cluster_info.prod_inst_name,
            "prodInstType": "k8s",
            "cellName": "multest",
            "cellCode": "multest",
            "envCode": "PORD",
            "planeCode": "multest",
            "planeName": "multest"
        }
        response = self.patch(endpoint=url, json=body, headers=headers)
        return response.json()

    def delete_cluster_plane(self, cluster_info: ClusterPlaneEntity) -> Dict[str, Any]:
        """
        删除集群平面单元
        """
        self.logger.info(f"Delete cluster plane")
        url = "/openapi/portal/restApi/cluster/delete"
        cache = DataCache.get_instance()
        headers = {
            "Authorization": cache.get("token"),
        }
        params = {
            "instanceId": cluster_info.instance_id,
        }
        response = self.delete(endpoint=url, params=params, headers=headers)
        return response.json()

    def query_bind_cluster_list(self) -> Dict[str, Any]:
        """
        根据租户、环境查询绑定集群信息
        """
        self.logger.info(f"Query bind cluster list")
        url = "/openapi/portal/restApi/bindCluster/list"
        cache = DataCache.get_instance()
        headers = {
            "Authorization": cache.get("token"),
        }
        response = self.get(endpoint=url, headers=headers)
        return response.json()

    def tenant_bind_cluster(self) -> Dict[str, Any]:
        """
        租户绑定集群平面单元
        """
        self.logger.info(f"Tenant bind cluster plane cell")
        url = "/openapi/portal/restApi/tenantCluster/addBatch"
        cache = DataCache.get_instance()
        headers = {
            "Authorization": cache.get("token"),
        }
        body = [
            {
                "clusterInstanceId": "348",
                "envCode": "生产环境",
                "envName": "生产环境",
                "tenantId": "1"
            }
        ]
        response = self.post(endpoint=url, json=body, headers=headers)
        return response.json()

    def query_tenant_info_by_username(self, username: str) -> Dict[str, Any]:
        """
        根据用户名查询绑定的租户信息
        """
        self.logger.info(f"Query tenant info by username: {username}")
        url = f"/openapi/portal/restApi/v1/user/{username}/tenants"
        cache = DataCache.get_instance()
        headers = {
            "Authorization": cache.get("token"),
        }
        response = self.get(endpoint=url, headers=headers)
        return response.json()

    def get_menu_permission_data(self) -> Dict[str, Any]:
        """
        获取菜单权限数据
        """
        self.logger.info(f"Get menu permission data")
        url = "/openapi/portal/restApi/menu/list"
        cache = DataCache.get_instance()
        headers = {
            "Authorization": cache.get("token"),
        }
        response = self.get(endpoint=url, headers=headers)
        return response.json()

    def sync_user_api(self, user_info: PortalUserEntity) -> Dict[str, Any]:
        """
        同步用户
        """
        self.logger.info(f"Sync user information")
        url = "/openapi/portal/restApi/sync/user"
        cache = DataCache.get_instance()
        headers = {
            "Authorization": cache.get("token"),
        }
        body = {
            "sourceCode": "1",
            "phone": user_info.phone,
            "displayName": "shengsong",
            "expireDate": "2099-12-31 23:59:59",
            "userName": user_info.username,
            "locked": False,
            "email": user_info.email,
            "tenantRoleList": [
                {
                    "roles": [
                        "platform_manager"
                    ],
                    "tenantCode": "tenant_admin"
                }
            ]
        }
        response = self.post(endpoint=url, json=body, headers=headers)
        return response.json()

    def user_bind_tenant(self, user_info: PortalUserEntity) -> Dict[str, Any]:
        """
        绑定租户
        """
        self.logger.info(f"Bind tenant")
        url = "/openapi/portal/restApi/addTenantUsers"
        cache = DataCache.get_instance()
        headers = {
            "Authorization": cache.get("token"),
        }
        body = {
            "tenantId": "1",
            "userIdJsonStr": [
                {
                    "userId": user_info.user_id,
                    "userName": user_info.username,
                    "status": 1
                }
            ]
        }
        response = self.post(endpoint=url, json=body, headers=headers)
        return response.json()

    def user_bind_role(self, user_info: PortalUserEntity) -> Dict[str, Any]:
        """
        绑定角色
        """
        self.logger.info(f"Bind role")
        url = "/openapi/portal/restApi/addRoleMember"
        cache = DataCache.get_instance()
        headers = {
            "Authorization": cache.get("token"),
        }
        body = {
            "tenantId": "1",
            "roleId": "1",
            "userList": [
                {
                    "userId": user_info.user_id,
                    "userName": user_info.username
                }
            ]
        }
        response = self.post(endpoint=url, json=body, headers=headers)
        return response.json()

    def query_system(self, system_code: str) -> Dict[str, Any]:
        """
        查询系统
        """
        self.logger.info(f"Query system")
        url = "/openapi/portal/restApi/system/list"
        cache = DataCache.get_instance()
        headers = {
            "Authorization": cache.get("token"),
        }
        body = {
            "systemEnvironment": "PROD",
            "systemName": system_code
        }
        response = self.post(endpoint=url, json=body, headers=headers)
        return response.json()

