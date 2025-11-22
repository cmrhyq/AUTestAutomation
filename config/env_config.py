"""
环境适配配置模块

该模块提供环境特定的配置管理，支持多环境配置切换和从环境变量加载配置。
支持的环境：dev, test, staging, prod
"""

import os
import json
from typing import Dict, Any, Optional, Literal
from pathlib import Path
from dataclasses import dataclass, field, asdict


EnvironmentType = Literal["dev", "test", "staging", "prod"]


@dataclass
class EnvironmentConfig:
    """
    环境特定配置类
    
    每个环境可以有自己的配置，包括 API URL、数据库连接、超时设置等。
    """
    
    # 环境名称
    name: EnvironmentType
    
    # API 配置
    api_base_url: str = ""
    api_timeout: int = 30
    api_verify_ssl: bool = True
    
    # 浏览器配置
    browser_type: Literal["chromium", "firefox", "webkit"] = "chromium"
    headless: bool = False
    browser_timeout: int = 30000
    
    # 认证配置
    bearer_token: Optional[str] = None
    api_key: Optional[str] = None
    basic_auth_username: Optional[str] = None
    basic_auth_password: Optional[str] = None
    
    # 日志配置
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    
    # 重试配置
    max_retries: int = 3
    retry_delay: int = 1
    enable_retry: bool = False
    
    # 并行配置
    parallel_workers: str = "auto"
    enable_parallel: bool = True
    
    # 自定义配置（用于扩展）
    custom_config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnvironmentConfig':
        """从字典创建配置"""
        # 过滤掉不在 dataclass 中的字段
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)


class EnvironmentManager:
    """
    环境管理器
    
    负责加载、切换和验证不同环境的配置。
    支持从环境变量、配置文件和代码中加载配置。
    """
    
    # 默认环境配置
    DEFAULT_CONFIGS: Dict[EnvironmentType, EnvironmentConfig] = {
        "dev": EnvironmentConfig(
            name="dev",
            api_base_url="http://localhost:3000",
            headless=False,
            log_level="DEBUG",
            enable_retry=False,
            enable_parallel=False,
        ),
        "test": EnvironmentConfig(
            name="test",
            api_base_url="https://test-api.example.com",
            headless=True,
            log_level="INFO",
            enable_retry=True,
            enable_parallel=True,
        ),
        "staging": EnvironmentConfig(
            name="staging",
            api_base_url="https://staging-api.example.com",
            headless=True,
            log_level="INFO",
            enable_retry=True,
            enable_parallel=True,
            api_verify_ssl=True,
        ),
        "prod": EnvironmentConfig(
            name="prod",
            api_base_url="https://api.example.com",
            headless=True,
            log_level="WARNING",
            enable_retry=True,
            enable_parallel=True,
            api_verify_ssl=True,
            max_retries=5,
        ),
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化环境管理器
        
        Args:
            config_file: 可选的配置文件路径（JSON 格式）
        """
        self._configs: Dict[EnvironmentType, EnvironmentConfig] = {}
        self._current_env: Optional[EnvironmentType] = None
        self._config_file = config_file
        
        # 加载默认配置
        self._load_default_configs()
        
        # 从配置文件加载（如果提供）
        if config_file and Path(config_file).exists():
            self._load_from_file(config_file)
        
        # 从环境变量加载当前环境
        self._load_from_env()
    
    def _load_default_configs(self) -> None:
        """加载默认配置"""
        self._configs = self.DEFAULT_CONFIGS.copy()

    def _load_from_file(self, config_file: str) -> None:
        """
        从 JSON 配置文件加载环境配置
        
        Args:
            config_file: 配置文件路径
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for env_name, env_data in data.items():
                if env_name in ["dev", "test", "staging", "prod"]:
                    # 合并默认配置和文件配置
                    if env_name in self._configs:
                        current_config = self._configs[env_name].to_dict()
                        current_config.update(env_data)
                        self._configs[env_name] = EnvironmentConfig.from_dict(current_config)
                    else:
                        env_data['name'] = env_name
                        self._configs[env_name] = EnvironmentConfig.from_dict(env_data)
        
        except Exception as e:
            import warnings
            warnings.warn(f"Failed to load config file {config_file}: {e}")

    def _load_from_env(self) -> None:
        """
        从环境变量加载配置
        
        环境变量优先级最高，会覆盖配置文件和默认配置。
        """
        # 获取当前环境
        env_name = os.getenv("TEST_ENV", "test")
        if env_name in ["dev", "test", "staging", "prod"]:
            self._current_env = env_name
        else:
            import warnings
            warnings.warn(f"Invalid TEST_ENV: {env_name}, using 'test' as default")
            self._current_env = "test"
        
        # 确保当前环境配置存在
        if self._current_env not in self._configs:
            self._configs[self._current_env] = EnvironmentConfig(name=self._current_env)
        
        # 从环境变量覆盖配置
        current_config = self._configs[self._current_env]
        
        # API 配置
        if os.getenv("API_BASE_URL"):
            current_config.api_base_url = os.getenv("API_BASE_URL")
        if os.getenv("API_TIMEOUT"):
            current_config.api_timeout = int(os.getenv("API_TIMEOUT"))
        if os.getenv("VERIFY_SSL"):
            current_config.api_verify_ssl = os.getenv("VERIFY_SSL").lower() == "true"
        
        # 浏览器配置
        if os.getenv("BROWSER_TYPE"):
            browser_type = os.getenv("BROWSER_TYPE")
            if browser_type in ["chromium", "firefox", "webkit"]:
                current_config.browser_type = browser_type
        if os.getenv("HEADLESS"):
            current_config.headless = os.getenv("HEADLESS").lower() == "true"
        if os.getenv("BROWSER_TIMEOUT"):
            current_config.browser_timeout = int(os.getenv("BROWSER_TIMEOUT"))
        
        # 认证配置
        if os.getenv("BEARER_TOKEN"):
            current_config.bearer_token = os.getenv("BEARER_TOKEN")
        if os.getenv("API_KEY"):
            current_config.api_key = os.getenv("API_KEY")
        if os.getenv("BASIC_AUTH_USERNAME"):
            current_config.basic_auth_username = os.getenv("BASIC_AUTH_USERNAME")
        if os.getenv("BASIC_AUTH_PASSWORD"):
            current_config.basic_auth_password = os.getenv("BASIC_AUTH_PASSWORD")
        
        # 日志配置
        if os.getenv("LOG_LEVEL"):
            log_level = os.getenv("LOG_LEVEL")
            if log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
                current_config.log_level = log_level
        
        # 重试配置
        if os.getenv("MAX_RETRIES"):
            current_config.max_retries = int(os.getenv("MAX_RETRIES"))
        if os.getenv("RETRY_DELAY"):
            current_config.retry_delay = int(os.getenv("RETRY_DELAY"))
        if os.getenv("ENABLE_RETRY"):
            current_config.enable_retry = os.getenv("ENABLE_RETRY").lower() == "true"
        
        # 并行配置
        if os.getenv("PARALLEL_WORKERS"):
            current_config.parallel_workers = os.getenv("PARALLEL_WORKERS")
        if os.getenv("ENABLE_PARALLEL"):
            current_config.enable_parallel = os.getenv("ENABLE_PARALLEL").lower() == "true"

    def get_current_env(self) -> EnvironmentType:
        """
        获取当前环境名称
        
        Returns:
            当前环境名称
        """
        return self._current_env or "test"
    
    def get_config(self, env: Optional[EnvironmentType] = None) -> EnvironmentConfig:
        """
        获取指定环境的配置
        
        Args:
            env: 环境名称，如果为 None 则返回当前环境配置
        
        Returns:
            环境配置对象
        """
        target_env = env or self._current_env or "test"
        
        if target_env not in self._configs:
            import warnings
            warnings.warn(f"Environment '{target_env}' not found, using default config")
            return EnvironmentConfig(name=target_env)
        
        return self._configs[target_env]
    
    def switch_env(self, env: EnvironmentType) -> None:
        """
        切换到指定环境
        
        Args:
            env: 目标环境名称
        """
        if env not in ["dev", "test", "staging", "prod"]:
            raise ValueError(f"Invalid environment: {env}. Must be one of: dev, test, staging, prod")
        
        if env not in self._configs:
            self._configs[env] = EnvironmentConfig(name=env)
        
        self._current_env = env
    
    def set_config(self, env: EnvironmentType, config: EnvironmentConfig) -> None:
        """
        设置指定环境的配置
        
        Args:
            env: 环境名称
            config: 环境配置对象
        """
        if env not in ["dev", "test", "staging", "prod"]:
            raise ValueError(f"Invalid environment: {env}")
        
        config.name = env
        self._configs[env] = config
    
    def update_config(self, env: Optional[EnvironmentType] = None, **kwargs) -> None:
        """
        更新指定环境的配置
        
        Args:
            env: 环境名称，如果为 None 则更新当前环境
            **kwargs: 要更新的配置项
        """
        target_env = env or self._current_env or "test"
        
        if target_env not in self._configs:
            self._configs[target_env] = EnvironmentConfig(name=target_env)
        
        config = self._configs[target_env]
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                # 存储到自定义配置中
                config.custom_config[key] = value

    def validate_config(self, env: Optional[EnvironmentType] = None) -> tuple[bool, list[str]]:
        """
        验证指定环境的配置
        
        Args:
            env: 环境名称，如果为 None 则验证当前环境
        
        Returns:
            tuple[bool, list[str]]: (是否有效, 错误信息列表)
        """
        config = self.get_config(env)
        errors = []
        
        # 验证浏览器类型
        if config.browser_type not in ["chromium", "firefox", "webkit"]:
            errors.append(f"Invalid browser_type: {config.browser_type}")
        
        # 验证超时时间
        if config.browser_timeout <= 0:
            errors.append(f"browser_timeout must be positive: {config.browser_timeout}")
        
        if config.api_timeout <= 0:
            errors.append(f"api_timeout must be positive: {config.api_timeout}")
        
        # 验证日志级别
        if config.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            errors.append(f"Invalid log_level: {config.log_level}")
        
        # 验证重试配置
        if config.max_retries < 0:
            errors.append(f"max_retries must be non-negative: {config.max_retries}")
        
        if config.retry_delay < 0:
            errors.append(f"retry_delay must be non-negative: {config.retry_delay}")
        
        # 验证并行配置
        if config.parallel_workers != "auto":
            try:
                workers = int(config.parallel_workers)
                if workers <= 0:
                    errors.append(f"parallel_workers must be 'auto' or positive integer: {config.parallel_workers}")
            except ValueError:
                errors.append(f"parallel_workers must be 'auto' or valid integer: {config.parallel_workers}")
        
        # 验证 API URL（生产环境必须配置）
        if config.name == "prod" and not config.api_base_url:
            errors.append("api_base_url is required for production environment")
        
        # 验证 SSL 配置（生产环境建议启用）
        if config.name == "prod" and not config.api_verify_ssl:
            import warnings
            warnings.warn("SSL verification is disabled in production environment")
        
        return len(errors) == 0, errors
    
    def get_all_configs(self) -> Dict[EnvironmentType, EnvironmentConfig]:
        """
        获取所有环境的配置
        
        Returns:
            所有环境配置的字典
        """
        return self._configs.copy()
    
    def save_to_file(self, config_file: str) -> None:
        """
        保存配置到文件
        
        Args:
            config_file: 配置文件路径
        """
        data = {}
        for env_name, config in self._configs.items():
            data[env_name] = config.to_dict()
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_config_summary(self, env: Optional[EnvironmentType] = None) -> Dict[str, Any]:
        """
        获取配置摘要（用于日志和调试，敏感信息已脱敏）
        
        Args:
            env: 环境名称，如果为 None 则返回当前环境摘要
        
        Returns:
            配置摘要字典
        """
        config = self.get_config(env)
        
        return {
            "environment": config.name,
            "api": {
                "base_url": config.api_base_url or "Not configured",
                "timeout": config.api_timeout,
                "verify_ssl": config.api_verify_ssl,
            },
            "browser": {
                "type": config.browser_type,
                "headless": config.headless,
                "timeout": config.browser_timeout,
            },
            "authentication": {
                "bearer_token": "***" if config.bearer_token else "Not configured",
                "api_key": "***" if config.api_key else "Not configured",
                "basic_auth": "***" if config.basic_auth_username else "Not configured",
            },
            "logging": {
                "level": config.log_level,
            },
            "retry": {
                "enabled": config.enable_retry,
                "max_retries": config.max_retries,
                "delay": config.retry_delay,
            },
            "parallel": {
                "enabled": config.enable_parallel,
                "workers": config.parallel_workers,
            },
            "custom": config.custom_config,
        }


# 创建全局环境管理器实例
env_manager = EnvironmentManager()

# 验证当前环境配置
is_valid, validation_errors = env_manager.validate_config()
if not is_valid:
    import warnings
    for error in validation_errors:
        warnings.warn(f"Environment configuration validation error: {error}")


# 便捷函数
def get_current_env() -> EnvironmentType:
    """获取当前环境名称"""
    return env_manager.get_current_env()


def get_config(env: Optional[EnvironmentType] = None) -> EnvironmentConfig:
    """获取环境配置"""
    return env_manager.get_config(env)


def switch_env(env: EnvironmentType) -> None:
    """切换环境"""
    env_manager.switch_env(env)


def validate_config(env: Optional[EnvironmentType] = None) -> tuple[bool, list[str]]:
    """验证环境配置"""
    return env_manager.validate_config(env)
