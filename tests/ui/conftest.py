"""
UI 测试专用的 conftest 配置

该文件仅在运行 UI 测试时加载 UI fixtures，
避免在 API 测试时初始化浏览器
"""

# 导入 UI fixtures（仅在 UI 测试目录下生效）
from base.ui.fixtures import *