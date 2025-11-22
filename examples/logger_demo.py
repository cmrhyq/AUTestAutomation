"""
日志管理器使用示例

演示如何使用 TestLogger 进行日志记录
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.log.logger import TestLogger, get_logger


def main():
    """演示日志管理器的基本用法"""
    
    # 1. 初始化日志系统
    print("=" * 60)
    print("日志管理器演示")
    print("=" * 60)
    
    TestLogger.setup_logger("DEBUG")
    print(f"\n✓ 日志系统已初始化")
    print(f"✓ 日志文件路径: {TestLogger.get_log_file_path()}")
    
    # 2. 获取日志记录器
    logger = get_logger("demo_module")
    print(f"\n✓ 获取日志记录器: {logger.name}")
    
    # 3. 记录不同级别的日志
    print("\n" + "=" * 60)
    print("记录不同级别的日志消息")
    print("=" * 60)
    
    logger.debug("这是一条 DEBUG 级别的日志 - 用于详细的调试信息")
    logger.info("这是一条 INFO 级别的日志 - 用于一般信息")
    logger.warning("这是一条 WARNING 级别的日志 - 用于警告信息")
    logger.error("这是一条 ERROR 级别的日志 - 用于错误信息")
    logger.critical("这是一条 CRITICAL 级别的日志 - 用于严重错误")
    
    # 4. 在不同模块中使用日志
    print("\n" + "=" * 60)
    print("在不同模块中使用日志")
    print("=" * 60)
    
    ui_logger = get_logger("ui.pages.login")
    ui_logger.info("UI 模块日志: 用户登录页面已加载")
    
    api_logger = get_logger("api.services.user")
    api_logger.info("API 模块日志: 获取用户信息成功")
    
    # 5. 日志格式说明
    print("\n" + "=" * 60)
    print("日志格式说明")
    print("=" * 60)
    print("日志格式: 时间戳 - 模块名 - 级别 - 消息")
    print("示例: 2024-01-01 12:00:00 - demo_module - INFO - 这是一条日志")
    
    # 6. 查看日志文件
    print("\n" + "=" * 60)
    print("日志文件内容预览")
    print("=" * 60)
    
    log_file_path = TestLogger.get_log_file_path()
    with open(log_file_path, 'r', encoding='utf-8') as f:
        log_content = f.read()
    
    print(log_content)
    
    print("\n" + "=" * 60)
    print("演示完成!")
    print("=" * 60)
    print(f"\n完整日志已保存到: {log_file_path}")
    print("日志同时输出到控制台和文件")
    print("在测试中，日志会自动附加到 Allure 报告")


if __name__ == "__main__":
    main()
