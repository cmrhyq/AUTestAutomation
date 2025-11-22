# 环境配置模块 (Environment Configuration Module)

## 概述

环境配置模块提供了强大的多环境配置管理功能，支持在不同环境（dev、test、staging、prod）之间无缝切换。

## 主要特性

### 1. 多环境支持
- **dev**: 开发环境
- **test**: 测试环境（默认）
- **staging**: 预发布环境
- **prod**: 生产环境

### 2. 配置来源优先级
1. 环境变量（最高优先级）
2. 配置文件（JSON）
3. 默认配置（最低优先级）

### 3. 核心功能
- ✅ 环境切换
- ✅ 配置验证
- ✅ 配置更新
- ✅ 配置持久化（保存到文件）
- ✅ 配置摘要（敏感信息脱敏）
- ✅ 自定义配置扩展

## 快速开始

### 基本使用

```python
from config import get_current_env, get_config, switch_env

# 获取当前环境
current_env = get_current_env()  # 返回: "test"

# 获取当前环境配置
config = get_config()
print(config.api_base_url)
print(config.browser_type)
print(config.log_level)

# 切换环境
switch_env("prod")
config = get_config()
```

### 使用环境变量

```bash
# 设置环境
export TEST_ENV=staging

# 覆盖特定配置
export API_BASE_URL=https://custom-api.example.com
export HEADLESS=true
export LOG_LEVEL=DEBUG
export MAX_RETRIES=5

# 运行测试
pytest
```

### 配置验证

```python
from config import validate_config

# 验证当前环境配置
is_valid, errors = validate_config()
if not is_valid:
    for error in errors:
        print(f"错误: {error}")

# 验证特定环境配置
is_valid, errors = validate_config("prod")
```

### 更新配置

```python
from config import env_manager

# 更新当前环境配置
env_manager.update_config(
    api_base_url="http://localhost:8080",
    max_retries=5,
    custom_setting="value"
)

# 更新特定环境配置
env_manager.update_config(
    env="dev",
    headless=False,
    log_level="DEBUG"
)
```

### 保存和加载配置

```python
from config import env_manager

# 保存所有环境配置到文件
env_manager.save_to_file("my_config.json")

# 从文件加载配置
from config.env_config import EnvironmentManager
manager = EnvironmentManager(config_file="my_config.json")
```

## 配置项说明

### EnvironmentConfig 数据类

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | str | - | 环境名称 (dev/test/staging/prod) |
| `api_base_url` | str | "" | API 基础 URL |
| `api_timeout` | int | 30 | API 请求超时（秒） |
| `api_verify_ssl` | bool | True | 是否验证 SSL 证书 |
| `browser_type` | str | "chromium" | 浏览器类型 (chromium/firefox/webkit) |
| `headless` | bool | False | 是否无头模式 |
| `browser_timeout` | int | 30000 | 浏览器超时（毫秒） |
| `bearer_token` | str | None | Bearer Token |
| `api_key` | str | None | API Key |
| `basic_auth_username` | str | None | Basic Auth 用户名 |
| `basic_auth_password` | str | None | Basic Auth 密码 |
| `log_level` | str | "INFO" | 日志级别 |
| `max_retries` | int | 3 | 最大重试次数 |
| `retry_delay` | int | 1 | 重试延迟（秒） |
| `enable_retry` | bool | False | 是否启用重试 |
| `parallel_workers` | str | "auto" | 并行 worker 数量 |
| `enable_parallel` | bool | True | 是否启用并行 |
| `custom_config` | dict | {} | 自定义配置 |

## 默认环境配置

### Dev 环境
```python
{
    "api_base_url": "http://localhost:3000",
    "headless": False,
    "log_level": "DEBUG",
    "enable_retry": False,
    "enable_parallel": False
}
```

### Test 环境
```python
{
    "api_base_url": "https://test-api.example.com",
    "headless": True,
    "log_level": "INFO",
    "enable_retry": True,
    "enable_parallel": True
}
```

### Staging 环境
```python
{
    "api_base_url": "https://staging-api.example.com",
    "headless": True,
    "log_level": "INFO",
    "enable_retry": True,
    "enable_parallel": True,
    "api_verify_ssl": True
}
```

### Prod 环境
```python
{
    "api_base_url": "https://api.example.com",
    "headless": True,
    "log_level": "WARNING",
    "enable_retry": True,
    "enable_parallel": True,
    "api_verify_ssl": True,
    "max_retries": 5
}
```

## API 参考

### 便捷函数

#### `get_current_env() -> EnvironmentType`
获取当前环境名称。

#### `get_config(env: Optional[EnvironmentType] = None) -> EnvironmentConfig`
获取指定环境的配置，如果 env 为 None 则返回当前环境配置。

#### `switch_env(env: EnvironmentType) -> None`
切换到指定环境。

#### `validate_config(env: Optional[EnvironmentType] = None) -> tuple[bool, list[str]]`
验证指定环境的配置，返回 (是否有效, 错误列表)。

### EnvironmentManager 类

#### `__init__(config_file: Optional[str] = None)`
初始化环境管理器，可选择从配置文件加载。

#### `get_current_env() -> EnvironmentType`
获取当前环境名称。

#### `get_config(env: Optional[EnvironmentType] = None) -> EnvironmentConfig`
获取环境配置。

#### `switch_env(env: EnvironmentType) -> None`
切换环境。

#### `set_config(env: EnvironmentType, config: EnvironmentConfig) -> None`
设置环境配置。

#### `update_config(env: Optional[EnvironmentType] = None, **kwargs) -> None`
更新环境配置。

#### `validate_config(env: Optional[EnvironmentType] = None) -> tuple[bool, list[str]]`
验证环境配置。

#### `get_all_configs() -> Dict[EnvironmentType, EnvironmentConfig]`
获取所有环境的配置。

#### `save_to_file(config_file: str) -> None`
保存配置到文件。

#### `get_config_summary(env: Optional[EnvironmentType] = None) -> Dict[str, Any]`
获取配置摘要（敏感信息已脱敏）。

## 配置文件格式

### JSON 格式示例

```json
{
  "dev": {
    "api_base_url": "http://localhost:3000",
    "headless": false,
    "log_level": "DEBUG",
    "enable_retry": false,
    "max_retries": 3
  },
  "test": {
    "api_base_url": "https://test-api.example.com",
    "headless": true,
    "log_level": "INFO",
    "enable_retry": true,
    "max_retries": 3
  },
  "staging": {
    "api_base_url": "https://staging-api.example.com",
    "headless": true,
    "log_level": "INFO",
    "enable_retry": true,
    "api_verify_ssl": true
  },
  "prod": {
    "api_base_url": "https://api.example.com",
    "headless": true,
    "log_level": "WARNING",
    "enable_retry": true,
    "api_verify_ssl": true,
    "max_retries": 5
  }
}
```

## 最佳实践

### 1. 使用环境变量进行敏感信息配置
```bash
export BEARER_TOKEN=your_secret_token
export API_KEY=your_api_key
export BASIC_AUTH_PASSWORD=your_password
```

### 2. 为不同环境创建配置文件
```
configs/
├── dev.json
├── test.json
├── staging.json
└── prod.json
```

### 3. 在 CI/CD 中使用环境变量
```yaml
# GitHub Actions 示例
env:
  TEST_ENV: staging
  API_BASE_URL: ${{ secrets.STAGING_API_URL }}
  BEARER_TOKEN: ${{ secrets.STAGING_TOKEN }}
```

### 4. 验证配置后再运行测试
```python
from config import validate_config

is_valid, errors = validate_config()
if not is_valid:
    raise ValueError(f"Invalid configuration: {errors}")

# 继续运行测试
```

### 5. 使用配置摘要进行调试
```python
from config import env_manager

# 在测试开始时打印配置摘要
summary = env_manager.get_config_summary()
print(f"Running tests with configuration: {summary}")
```

## 示例

完整的使用示例请参考：
- `examples/env_config_demo.py` - 环境配置模块演示

## 注意事项

1. **敏感信息**: 不要在配置文件中存储敏感信息（如密码、token），使用环境变量代替
2. **生产环境**: 生产环境必须配置 `api_base_url` 并启用 `api_verify_ssl`
3. **配置验证**: 框架会在加载时自动验证配置，无效配置会产生警告
4. **环境变量优先级**: 环境变量会覆盖配置文件和默认配置
5. **线程安全**: 环境管理器是线程安全的，可以在并行测试中使用

## 故障排除

### 问题：环境变量不生效
**解决方案**: 确保在运行测试前设置环境变量，并检查变量名是否正确。

### 问题：配置文件加载失败
**解决方案**: 检查 JSON 文件格式是否正确，确保文件路径存在。

### 问题：配置验证失败
**解决方案**: 查看错误信息，修正无效的配置项。

### 问题：切换环境后配置未更新
**解决方案**: 确保在切换环境后重新获取配置对象。

## 更新日志

### v1.0.0 (2025-11-21)
- ✅ 初始版本发布
- ✅ 支持 4 个环境（dev、test、staging、prod）
- ✅ 支持从环境变量和配置文件加载
- ✅ 配置验证功能
- ✅ 配置持久化功能
- ✅ 敏感信息脱敏
- ✅ 自定义配置扩展
