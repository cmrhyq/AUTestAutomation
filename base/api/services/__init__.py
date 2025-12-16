"""
API 服务封装模块

该模块提供 API 服务的基础类和具体实现：
- BaseService: API 服务基类，提供通用的 HTTP 请求方法
- 具体服务类: 针对特定 API 的封装
"""

from base.api.services.base_service import BaseService
from base.api.services.portal_inner_service import PanJiPortalInnerService
from base.api.services.portal_open_service import PanJiPortalOpenService

__all__ = [
    'BaseService',
    'PanJiPortalInnerService',
    'PanJiPortalOpenService',
]
