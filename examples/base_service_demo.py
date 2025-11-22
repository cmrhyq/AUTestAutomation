"""
BaseService 使用示例

演示如何使用 BaseService 进行 API 测试
"""

from base.api.services.base_service import BaseService
from core.log.logger import TestLogger


def demo_basic_requests():
    """演示基本的 HTTP 请求"""
    print("\n=== 基本 HTTP 请求示例 ===\n")
    
    # 初始化日志
    TestLogger.setup_logger()
    
    # 创建服务实例（使用 JSONPlaceholder 公共 API）
    service = BaseService(base_url="https://jsonplaceholder.typicode.com")
    
    try:
        # GET 请求
        print("1. 发送 GET 请求获取用户信息...")
        response = service.get("/users/1")
        print(f"   状态码: {response.status_code}")
        print(f"   响应数据: {response.json()}")
        
        # POST 请求
        print("\n2. 发送 POST 请求创建新帖子...")
        new_post = {
            "title": "Test Post",
            "body": "This is a test post",
            "userId": 1
        }
        response = service.post("/posts", json=new_post)
        print(f"   状态码: {response.status_code}")
        print(f"   创建的帖子: {response.json()}")
        
        # PUT 请求
        print("\n3. 发送 PUT 请求更新帖子...")
        updated_post = {
            "id": 1,
            "title": "Updated Title",
            "body": "Updated body",
            "userId": 1
        }
        response = service.put("/posts/1", json=updated_post)
        print(f"   状态码: {response.status_code}")
        print(f"   更新后的帖子: {response.json()}")
        
        # DELETE 请求
        print("\n4. 发送 DELETE 请求删除帖子...")
        response = service.delete("/posts/1")
        print(f"   状态码: {response.status_code}")
        
    finally:
        service.close()


def demo_data_extraction_and_caching():
    """演示数据提取和缓存功能"""
    print("\n=== 数据提取和缓存示例 ===\n")
    
    # 初始化日志
    TestLogger.setup_logger()
    
    service = BaseService(base_url="https://jsonplaceholder.typicode.com")
    
    try:
        # 获取用户信息
        print("1. 获取用户信息并提取数据...")
        response = service.get("/users/1")
        
        # 提取并缓存用户 ID
        user_id = service.extract_and_cache(response, "user_id", "id")
        print(f"   提取的用户 ID: {user_id}")
        
        # 提取并缓存用户名
        username = service.extract_and_cache(response, "username", "username")
        print(f"   提取的用户名: {username}")
        
        # 提取并缓存邮箱
        email = service.extract_and_cache(response, "email", "email")
        print(f"   提取的邮箱: {email}")
        
        # 从缓存中读取数据
        print("\n2. 从缓存中读取数据...")
        cached_user_id = service.get_cached_value("user_id")
        cached_username = service.get_cached_value("username")
        cached_email = service.get_cached_value("email")
        
        print(f"   缓存的用户 ID: {cached_user_id}")
        print(f"   缓存的用户名: {cached_username}")
        print(f"   缓存的邮箱: {cached_email}")
        
        # 使用缓存的数据创建新帖子
        print("\n3. 使用缓存的用户 ID 创建帖子...")
        new_post = {
            "title": "Post by cached user",
            "body": f"This post is created by user {cached_username}",
            "userId": cached_user_id
        }
        response = service.post("/posts", json=new_post)
        print(f"   状态码: {response.status_code}")
        print(f"   创建的帖子: {response.json()}")
        
    finally:
        service.close()


def demo_authentication():
    """演示认证功能"""
    print("\n=== 认证功能示例 ===\n")
    
    # 初始化日志
    TestLogger.setup_logger()
    
    # Bearer Token 认证
    print("1. Bearer Token 认证...")
    service_bearer = BaseService(
        base_url="https://api.example.com",
        auth_type='bearer',
        auth_credentials={'token': 'your_token_here'}
    )
    print(f"   Authorization Header: {service_bearer.session.headers.get('Authorization')}")
    service_bearer.close()
    
    # API Key 认证
    print("\n2. API Key 认证...")
    service_api_key = BaseService(
        base_url="https://api.example.com",
        auth_type='api_key',
        auth_credentials={'api_key': 'your_api_key', 'header_name': 'X-API-Key'}
    )
    print(f"   X-API-Key Header: {service_api_key.session.headers.get('X-API-Key')}")
    service_api_key.close()
    
    # Basic Auth 认证
    print("\n3. Basic Auth 认证...")
    service_basic = BaseService(
        base_url="https://api.example.com",
        auth_type='basic',
        auth_credentials={'username': 'user', 'password': 'pass'}
    )
    print(f"   Auth 配置: {service_basic.session.auth}")
    service_basic.close()


def demo_status_code_validation():
    """演示状态码验证"""
    print("\n=== 状态码验证示例 ===\n")
    
    # 初始化日志
    TestLogger.setup_logger()
    
    service = BaseService(base_url="https://jsonplaceholder.typicode.com")
    
    try:
        # 获取数据并验证状态码
        print("1. 验证 GET 请求状态码...")
        response = service.get("/users/1")
        is_valid = service.validate_status_code(response, 200)
        print(f"   状态码 200 验证: {is_valid}")
        
        # 验证多个可接受的状态码
        print("\n2. 验证多个可接受的状态码...")
        response = service.post("/posts", json={"title": "Test", "body": "Test", "userId": 1})
        is_valid = service.validate_status_code(response, [200, 201])
        print(f"   状态码 200 或 201 验证: {is_valid}")
        
    finally:
        service.close()


def demo_context_manager():
    """演示上下文管理器用法"""
    print("\n=== 上下文管理器示例 ===\n")
    
    # 初始化日志
    TestLogger.setup_logger()
    
    # 使用 with 语句自动管理资源
    print("使用 with 语句自动管理 session...")
    with BaseService(base_url="https://jsonplaceholder.typicode.com") as service:
        response = service.get("/users/1")
        print(f"状态码: {response.status_code}")
        print(f"用户名: {response.json()['username']}")
    
    print("退出 with 块后，session 自动关闭")


if __name__ == "__main__":
    # 运行所有示例
    demo_basic_requests()
    demo_data_extraction_and_caching()
    demo_authentication()
    demo_status_code_validation()
    demo_context_manager()
    
    print("\n=== 所有示例运行完成 ===\n")
