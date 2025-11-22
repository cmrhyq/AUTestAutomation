"""
全局配置模块

该模块定义了测试框架的所有配置项，支持从环境变量加载配置。
配置项包括浏览器设置、API设置、日志设置、并行执行设置等。
"""

import os
from typing import Optional, Literal
from pathlib import Path
from dotenv import load_dotenv



class Settings:
    """
    测试框架全局配置类
    
    所有配置项都可以通过环境变量覆盖，环境变量名称为配置项名称的大写形式。
    例如：BROWSER_TYPE 环境变量会覆盖 browser_type 配置。
    """
    load_dotenv()
    
    # ==================== 浏览器配置 ====================
    
    # 浏览器类型：chromium, firefox, webkit
    # 环境变量：BROWSER_TYPE
    BROWSER_TYPE: Literal["chromium", "firefox", "webkit"] = os.getenv(
        "BROWSER_TYPE", "chromium"
    )
    
    # 是否使用无头模式运行浏览器
    # 环境变量：HEADLESS (true/false)
    HEADLESS: bool = os.getenv("HEADLESS", "false").lower() == "true"
    
    # 浏览器操作超时时间（毫秒）
    # 环境变量：BROWSER_TIMEOUT
    BROWSER_TIMEOUT: int = int(os.getenv("BROWSER_TIMEOUT", "30000"))
    
    # 页面加载超时时间（毫秒）
    # 环境变量：PAGE_LOAD_TIMEOUT
    PAGE_LOAD_TIMEOUT: int = int(os.getenv("PAGE_LOAD_TIMEOUT", "30000"))
    
    # 浏览器启动参数
    # 环境变量：BROWSER_ARGS (逗号分隔)
    BROWSER_ARGS: list = os.getenv("BROWSER_ARGS", "").split(",") if os.getenv("BROWSER_ARGS") else []
    
    # 视口大小
    # 环境变量：VIEWPORT_WIDTH, VIEWPORT_HEIGHT
    VIEWPORT_WIDTH: int = int(os.getenv("VIEWPORT_WIDTH", "1920"))
    VIEWPORT_HEIGHT: int = int(os.getenv("VIEWPORT_HEIGHT", "1080"))
    
    # 是否启用浏览器开发者工具
    # 环境变量：DEVTOOLS (true/false)
    DEVTOOLS: bool = os.getenv("DEVTOOLS", "false").lower() == "true"
    
    # ==================== API 配置 ====================
    
    # API 基础 URL
    # 环境变量：API_BASE_URL
    API_BASE_URL: str = os.getenv("API_BASE_URL", "")
    
    # API 请求超时时间（秒）
    # 环境变量：API_TIMEOUT
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))
    
    # API 连接超时时间（秒）
    # 环境变量：API_CONNECT_TIMEOUT
    API_CONNECT_TIMEOUT: int = int(os.getenv("API_CONNECT_TIMEOUT", "10"))
    
    # API 读取超时时间（秒）
    # 环境变量：API_READ_TIMEOUT
    API_READ_TIMEOUT: int = int(os.getenv("API_READ_TIMEOUT", "30"))
    
    # 是否验证 SSL 证书
    # 环境变量：VERIFY_SSL (true/false)
    VERIFY_SSL: bool = os.getenv("VERIFY_SSL", "true").lower() == "true"
    
    # ==================== 认证配置 ====================
    
    # Bearer Token
    # 环境变量：BEARER_TOKEN
    BEARER_TOKEN: Optional[str] = os.getenv("BEARER_TOKEN")
    
    # API Key
    # 环境变量：API_KEY
    API_KEY: Optional[str] = os.getenv("API_KEY")
    
    # API Key Header 名称
    # 环境变量：API_KEY_HEADER
    API_KEY_HEADER: str = os.getenv("API_KEY_HEADER", "X-API-Key")
    
    # Basic Auth 用户名
    # 环境变量：BASIC_AUTH_USERNAME
    BASIC_AUTH_USERNAME: Optional[str] = os.getenv("BASIC_AUTH_USERNAME")
    
    # Basic Auth 密码
    # 环境变量：BASIC_AUTH_PASSWORD
    BASIC_AUTH_PASSWORD: Optional[str] = os.getenv("BASIC_AUTH_PASSWORD")
    
    # ==================== 日志配置 ====================
    
    # 日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL
    # 环境变量：LOG_LEVEL
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = os.getenv(
        "LOG_LEVEL", "INFO"
    )
    
    # 日志目录
    # 环境变量：LOG_DIR
    LOG_DIR: str = os.getenv("LOG_DIR", "logs")
    
    # 日志文件名格式
    # 环境变量：LOG_FILE_FORMAT
    LOG_FILE_FORMAT: str = os.getenv("LOG_FILE_FORMAT", "test_{timestamp}.log")
    
    # 是否在控制台输出日志
    # 环境变量：LOG_TO_CONSOLE (true/false)
    LOG_TO_CONSOLE: bool = os.getenv("LOG_TO_CONSOLE", "true").lower() == "true"
    
    # 是否输出日志到文件
    # 环境变量：LOG_TO_FILE (true/false)
    LOG_TO_FILE: bool = os.getenv("LOG_TO_FILE", "true").lower() == "true"
    
    # 日志格式
    # 环境变量：LOG_FORMAT
    LOG_FORMAT: str = os.getenv(
        "LOG_FORMAT",
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # 日志时间格式
    # 环境变量：LOG_DATE_FORMAT
    LOG_DATE_FORMAT: str = os.getenv("LOG_DATE_FORMAT", "%Y-%m-%d %H:%M:%S")
    
    # ==================== 并行执行配置 ====================
    
    # 并行 worker 数量：auto 表示自动检测 CPU 核心数，或指定具体数字
    # 环境变量：PARALLEL_WORKERS
    PARALLEL_WORKERS: str = os.getenv("PARALLEL_WORKERS", "auto")
    
    # 是否启用并行执行
    # 环境变量：ENABLE_PARALLEL (true/false)
    ENABLE_PARALLEL: bool = os.getenv("ENABLE_PARALLEL", "true").lower() == "true"
    
    # 并行执行分发策略：loadscope, loadfile, loadgroup, load
    # 环境变量：PARALLEL_DIST_MODE
    PARALLEL_DIST_MODE: Literal["loadscope", "loadfile", "loadgroup", "load"] = os.getenv(
        "PARALLEL_DIST_MODE", "loadscope"
    )
    
    # ==================== 重试配置 ====================
    
    # 最大重试次数
    # 环境变量：MAX_RETRIES
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    
    # 重试延迟时间（秒）
    # 环境变量：RETRY_DELAY
    RETRY_DELAY: int = int(os.getenv("RETRY_DELAY", "1"))
    
    # 是否启用失败重试
    # 环境变量：ENABLE_RETRY (true/false)
    ENABLE_RETRY: bool = os.getenv("ENABLE_RETRY", "false").lower() == "true"
    
    # ==================== Allure 报告配置 ====================
    
    # Allure 结果目录
    # 环境变量：ALLURE_RESULTS_DIR
    ALLURE_RESULTS_DIR: str = os.getenv("ALLURE_RESULTS_DIR", "report/allure-results")
    
    # Allure 报告目录
    # 环境变量：ALLURE_REPORT_DIR
    ALLURE_REPORT_DIR: str = os.getenv("ALLURE_REPORT_DIR", "report/allure-report")
    
    # 是否清理旧的 Allure 结果
    # 环境变量：ALLURE_CLEAN_RESULTS (true/false)
    ALLURE_CLEAN_RESULTS: bool = os.getenv("ALLURE_CLEAN_RESULTS", "true").lower() == "true"
    
    # ==================== 截图配置 ====================
    
    # 截图保存目录
    # 环境变量：SCREENSHOT_DIR
    SCREENSHOT_DIR: str = os.getenv("SCREENSHOT_DIR", "screenshots")
    
    # 是否在失败时自动截图
    # 环境变量：SCREENSHOT_ON_FAILURE (true/false)
    SCREENSHOT_ON_FAILURE: bool = os.getenv("SCREENSHOT_ON_FAILURE", "true").lower() == "true"
    
    # 截图格式：png, jpeg
    # 环境变量：SCREENSHOT_FORMAT
    SCREENSHOT_FORMAT: Literal["png", "jpeg"] = os.getenv("SCREENSHOT_FORMAT", "png")
    
    # 截图质量（仅对 jpeg 有效，1-100）
    # 环境变量：SCREENSHOT_QUALITY
    SCREENSHOT_QUALITY: int = int(os.getenv("SCREENSHOT_QUALITY", "80"))
    
    # ==================== 测试环境配置 ====================
    
    # 测试环境：dev, test, staging, prod
    # 环境变量：TEST_ENV
    TEST_ENV: str = os.getenv("TEST_ENV", "test")
    
    # 项目根目录
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    
    # ==================== 数据配置 ====================
    
    # 测试数据目录
    # 环境变量：TEST_DATA_DIR
    TEST_DATA_DIR: str = os.getenv("TEST_DATA_DIR", "test_data")
    
    # ==================== 配置验证方法 ====================
    
    @classmethod
    def validate(cls) -> tuple[bool, list[str]]:
        """
        验证配置的有效性
        
        Returns:
            tuple[bool, list[str]]: (是否有效, 错误信息列表)
        """
        errors = []
        
        # 验证浏览器类型
        if cls.BROWSER_TYPE not in ["chromium", "firefox", "webkit"]:
            errors.append(f"Invalid BROWSER_TYPE: {cls.BROWSER_TYPE}. Must be one of: chromium, firefox, webkit")
        
        # 验证超时时间
        if cls.BROWSER_TIMEOUT <= 0:
            errors.append(f"BROWSER_TIMEOUT must be positive, got: {cls.BROWSER_TIMEOUT}")
        
        if cls.API_TIMEOUT <= 0:
            errors.append(f"API_TIMEOUT must be positive, got: {cls.API_TIMEOUT}")
        
        # 验证日志级别
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if cls.LOG_LEVEL not in valid_log_levels:
            errors.append(f"Invalid LOG_LEVEL: {cls.LOG_LEVEL}. Must be one of: {', '.join(valid_log_levels)}")
        
        # 验证并行 worker 配置
        if cls.PARALLEL_WORKERS != "auto":
            try:
                workers = int(cls.PARALLEL_WORKERS)
                if workers <= 0:
                    errors.append(f"PARALLEL_WORKERS must be 'auto' or a positive integer, got: {cls.PARALLEL_WORKERS}")
            except ValueError:
                errors.append(f"PARALLEL_WORKERS must be 'auto' or a valid integer, got: {cls.PARALLEL_WORKERS}")
        
        # 验证重试配置
        if cls.MAX_RETRIES < 0:
            errors.append(f"MAX_RETRIES must be non-negative, got: {cls.MAX_RETRIES}")
        
        if cls.RETRY_DELAY < 0:
            errors.append(f"RETRY_DELAY must be non-negative, got: {cls.RETRY_DELAY}")
        
        # 验证截图质量
        if not (1 <= cls.SCREENSHOT_QUALITY <= 100):
            errors.append(f"SCREENSHOT_QUALITY must be between 1 and 100, got: {cls.SCREENSHOT_QUALITY}")
        
        # 验证视口大小
        if cls.VIEWPORT_WIDTH <= 0 or cls.VIEWPORT_HEIGHT <= 0:
            errors.append(f"Viewport dimensions must be positive, got: {cls.VIEWPORT_WIDTH}x{cls.VIEWPORT_HEIGHT}")
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_config_summary(cls) -> dict:
        """
        获取配置摘要（用于日志记录和调试）
        
        Returns:
            dict: 配置摘要字典（敏感信息已脱敏）
        """
        return {
            "browser": {
                "type": cls.BROWSER_TYPE,
                "headless": cls.HEADLESS,
                "timeout": cls.BROWSER_TIMEOUT,
                "viewport": f"{cls.VIEWPORT_WIDTH}x{cls.VIEWPORT_HEIGHT}",
            },
            "api": {
                "base_url": cls.API_BASE_URL or "Not configured",
                "timeout": cls.API_TIMEOUT,
                "verify_ssl": cls.VERIFY_SSL,
            },
            "logging": {
                "level": cls.LOG_LEVEL,
                "directory": cls.LOG_DIR,
                "console": cls.LOG_TO_CONSOLE,
                "file": cls.LOG_TO_FILE,
            },
            "parallel": {
                "enabled": cls.ENABLE_PARALLEL,
                "workers": cls.PARALLEL_WORKERS,
                "dist_mode": cls.PARALLEL_DIST_MODE,
            },
            "retry": {
                "enabled": cls.ENABLE_RETRY,
                "max_retries": cls.MAX_RETRIES,
                "delay": cls.RETRY_DELAY,
            },
            "allure": {
                "results_dir": cls.ALLURE_RESULTS_DIR,
                "report_dir": cls.ALLURE_REPORT_DIR,
            },
            "environment": cls.TEST_ENV,
        }
    
    @classmethod
    def create_directories(cls) -> None:
        """
        创建必要的目录结构
        """
        directories = [
            cls.LOG_DIR,
            cls.ALLURE_RESULTS_DIR,
            cls.ALLURE_REPORT_DIR,
            cls.SCREENSHOT_DIR,
            cls.TEST_DATA_DIR,
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)


# 创建全局配置实例
settings = Settings()

# 在模块加载时验证配置
is_valid, validation_errors = settings.validate()
if not is_valid:
    import warnings
    for error in validation_errors:
        warnings.warn(f"Configuration validation error: {error}")
