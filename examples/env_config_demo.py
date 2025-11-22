"""
环境配置模块使用示例

演示如何使用环境配置模块进行多环境配置管理。
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import env_manager, get_current_env, get_config, switch_env, validate_config


def demo_basic_usage():
    """演示基本使用"""
    print("=" * 60)
    print("1. 基本使用示例")
    print("=" * 60)
    
    # 获取当前环境
    current_env = get_current_env()
    print(f"\n当前环境: {current_env}")
    
    # 获取当前环境配置
    config = get_config()
    print(f"API Base URL: {config.api_base_url}")
    print(f"Browser Type: {config.browser_type}")
    print(f"Headless: {config.headless}")
    print(f"Log Level: {config.log_level}")
    print(f"Enable Parallel: {config.enable_parallel}")
    print(f"Parallel Workers: {config.parallel_workers}")


def demo_switch_environment():
    """演示环境切换"""
    print("\n" + "=" * 60)
    print("2. 环境切换示例")
    print("=" * 60)
    
    environments = ["dev", "test", "staging", "prod"]
    
    for env in environments:
        switch_env(env)
        config = get_config()
        print(f"\n环境: {env}")
        print(f"  API URL: {config.api_base_url}")
        print(f"  Headless: {config.headless}")
        print(f"  Log Level: {config.log_level}")
        print(f"  Enable Retry: {config.enable_retry}")
        print(f"  Max Retries: {config.max_retries}")


def demo_config_validation():
    """演示配置验证"""
    print("\n" + "=" * 60)
    print("3. 配置验证示例")
    print("=" * 60)
    
    for env in ["dev", "test", "staging", "prod"]:
        is_valid, errors = validate_config(env)
        print(f"\n环境 '{env}' 配置验证:")
        print(f"  有效: {is_valid}")
        if errors:
            print(f"  错误:")
            for error in errors:
                print(f"    - {error}")
        else:
            print(f"  ✓ 配置有效")


def demo_config_summary():
    """演示配置摘要"""
    print("\n" + "=" * 60)
    print("4. 配置摘要示例")
    print("=" * 60)
    
    summary = env_manager.get_config_summary()
    print(f"\n当前环境配置摘要:")
    print(f"  环境: {summary['environment']}")
    print(f"  API:")
    print(f"    Base URL: {summary['api']['base_url']}")
    print(f"    Timeout: {summary['api']['timeout']}s")
    print(f"    Verify SSL: {summary['api']['verify_ssl']}")
    print(f"  浏览器:")
    print(f"    Type: {summary['browser']['type']}")
    print(f"    Headless: {summary['browser']['headless']}")
    print(f"    Timeout: {summary['browser']['timeout']}ms")
    print(f"  认证:")
    print(f"    Bearer Token: {summary['authentication']['bearer_token']}")
    print(f"    API Key: {summary['authentication']['api_key']}")
    print(f"  日志:")
    print(f"    Level: {summary['logging']['level']}")
    print(f"  重试:")
    print(f"    Enabled: {summary['retry']['enabled']}")
    print(f"    Max Retries: {summary['retry']['max_retries']}")
    print(f"    Delay: {summary['retry']['delay']}s")
    print(f"  并行:")
    print(f"    Enabled: {summary['parallel']['enabled']}")
    print(f"    Workers: {summary['parallel']['workers']}")


def demo_update_config():
    """演示配置更新"""
    print("\n" + "=" * 60)
    print("5. 配置更新示例")
    print("=" * 60)
    
    # 切换到 dev 环境
    switch_env("dev")
    print("\n更新前的配置:")
    config = get_config()
    print(f"  API Base URL: {config.api_base_url}")
    print(f"  Max Retries: {config.max_retries}")
    
    # 更新配置
    env_manager.update_config(
        api_base_url="http://localhost:8080",
        max_retries=5,
        custom_setting="custom_value"
    )
    
    print("\n更新后的配置:")
    config = get_config()
    print(f"  API Base URL: {config.api_base_url}")
    print(f"  Max Retries: {config.max_retries}")
    print(f"  Custom Setting: {config.custom_config.get('custom_setting')}")


def demo_all_configs():
    """演示获取所有环境配置"""
    print("\n" + "=" * 60)
    print("6. 所有环境配置概览")
    print("=" * 60)
    
    all_configs = env_manager.get_all_configs()
    
    for env_name, config in all_configs.items():
        print(f"\n{env_name.upper()}:")
        print(f"  API URL: {config.api_base_url}")
        print(f"  Headless: {config.headless}")
        print(f"  Log Level: {config.log_level}")
        print(f"  Parallel: {config.enable_parallel}")


def demo_save_and_load():
    """演示保存和加载配置"""
    print("\n" + "=" * 60)
    print("7. 保存和加载配置示例")
    print("=" * 60)
    
    # 保存当前配置到文件
    config_file = "test_data/env_config.json"
    print(f"\n保存配置到: {config_file}")
    
    try:
        env_manager.save_to_file(config_file)
        print("✓ 配置已保存")
        
        # 显示文件内容
        import json
        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\n配置文件包含 {len(data)} 个环境:")
        for env_name in data.keys():
            print(f"  - {env_name}")
    
    except Exception as e:
        print(f"✗ 保存失败: {e}")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("环境配置模块演示")
    print("=" * 60)
    
    # 运行所有演示
    demo_basic_usage()
    demo_switch_environment()
    demo_config_validation()
    demo_config_summary()
    demo_update_config()
    demo_all_configs()
    demo_save_and_load()
    
    print("\n" + "=" * 60)
    print("演示完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
