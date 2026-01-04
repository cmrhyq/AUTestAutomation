import os
from pathlib import Path
from typing import Any, Optional, Dict

import yaml


class SystemConfig:
    """系统配置类，支持字典式访问和属性访问"""

    def __init__(self, config_dict=None):
        if config_dict is None:
            config_dict = {}
        self.config = config_dict

    def __getattr__(self, key: str) -> Any:
        """支持属性访问：config.api_base_url"""
        if key.startswith('_'):
            return object.__getattribute__(self, key)
        return self._data.get(key)

    def __getitem__(self, key: str) -> Any:
        """支持字典访问：config['api_base_url']"""
        return self._data.get(key)

    def get(self, key, default=None):
        """获取配置项，支持默认值"""
        return self.config.get(key, default)

    def set(self, key, value):
        """设置配置项"""
        self.config[key] = value

    def remove(self, key):
        """移除配置项"""
        if key in self.config:
            del self.config[key]

    def to_dict(self):
        """转换为字典"""
        return self.config

    def __repr__(self) -> str:
        return f"SystemConfig({self._data})"


class SystemConfigManager:
    """系统配置管理器"""

    def __init__(self):
        self.config_dir = Path(os.path.join(Path(__file__).parent.parent.parent, "config"))
        self._config: Optional[SystemConfig] = None
        self._load_config()

    def _load_config(self) -> SystemConfig:
        """
        加载指定环境的配置

        Returns:
            EnvConfig: 配置对象

        Raises:
            FileNotFoundError: 配置文件不存在
            ValueError: 配置文件格式错误
        """
        # 尝试加载 yaml 文件
        yaml_file = self.config_dir / "config_system.yaml"

        config_data = None

        if yaml_file.exists():
            config_data = self._load_yaml(yaml_file)
        else:
            raise FileNotFoundError(
                f"配置文件不存在: {yaml_file}\n"
                f"请在 {self.config_dir} 目录下创建 {yaml_file}"
            )

        self._config = SystemConfig(config_data)

        return self._config

    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """加载 YAML 配置文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"YAML 格式错误 {file_path}: {e}")
        except ImportError:
            raise ImportError("需要安装 PyYAML: pip install pyyaml")

    def get_config(self) -> SystemConfig:
        """
        获取当前环境配置

        Returns:
            EnvConfig: 当前配置对象
        """
        if self._config is None:
            raise RuntimeError("配置未加载，请先调用 load_env()")
        return self._config


system_manager = SystemConfigManager()

# 便捷函数
def get_sys_config() -> SystemConfig:
    """获取当前环境配置"""
    return system_manager.get_config()
