"""
Allure 报告辅助模块

该模块提供 Allure 报告的辅助功能：
- AllureHelper: Allure 辅助工具类
- allure_step: 创建测试步骤的便捷函数
"""

from core.allure.allure_helper import AllureHelper, allure_step

__all__ = [
    'AllureHelper',
    'allure_step',
]

