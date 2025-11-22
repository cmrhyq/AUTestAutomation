"""
API Fixtures 使用示例

演示如何使用 API fixtures 进行 API 测试
"""

import pytest
from unittest.mock import Mock, patch


class TestAPIFixturesDemo:
    """API Fixtures 使用示例"""
    
    @patch('api.services.base_service.requests.Session.request')
    def test_basic_api_request(self, mock_request, base_service):
        """
        示例 1: 使用 base_service fixture 发送基本 API 请求
        
        base_service fixture 提供了一个配置好的 BaseService 实例
        """
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 1,
            'name': 'John Doe',
            'email': 'john@example.com'
        }
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.elapsed.total_seconds.return_value = 0.5
        mock_response.url = "https://api.example.com/users/1"
        mock_request.return_value = mock_response
        
        # 发送 GET 请求
        response = base_service.get("/users/1")
        
        # 验证响应
        assert response.status_code == 200
        assert response.json()['name'] == 'John Doe'
    
    @patch('api.services.base_service.requests.Session.request')
    def test_data_extraction_and_caching(self, mock_request, base_service, api_cache):
        """
        示例 2: 从 API 响应中提取数据并缓存
        
        演示如何使用 extract_and_cache 方法和 api_cache fixture
        """
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'user': {
                    'id': 12345,
                    'username': 'johndoe',
                    'profile': {
                        'email': 'john@example.com'
                    }
                }
            }
        }
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.elapsed.total_seconds.return_value = 0.3
        mock_response.url = "https://api.example.com/user"
        mock_request.return_value = mock_response
        
        # 发送请求
        response = base_service.get("/user")
        
        # 提取并缓存用户 ID
        user_id = base_service.extract_and_cache(response, 'user_id', 'data.user.id')
        assert user_id == 12345
        
        # 提取并缓存用户邮箱
        email = base_service.extract_and_cache(response, 'user_email', 'data.user.profile.email')
        assert email == 'john@example.com'
        
        # 从缓存中获取数据
        cached_id = api_cache.get('user_id')
        cached_email = api_cache.get('user_email')
        
        assert cached_id == 12345
        assert cached_email == 'john@example.com'
        
        # 清理缓存
        api_cache.clear()
    
    @patch('api.services.base_service.requests.Session.request')
    def test_authenticated_request(self, mock_request, authenticated_service):
        """
        示例 3: 使用 authenticated_service fixture 发送认证请求
        
        authenticated_service 会自动根据环境变量配置认证
        """
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'message': 'Authenticated successfully'}
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.elapsed.total_seconds.return_value = 0.2
        mock_response.url = "https://api.example.com/protected"
        mock_request.return_value = mock_response
        
        # 发送认证请求
        response = authenticated_service.get("/protected")
        
        # 验证响应
        assert response.status_code == 200
        assert response.json()['message'] == 'Authenticated successfully'
    
    @patch('api.services.base_service.requests.Session.request')
    def test_custom_service_with_different_base_url(self, mock_request, custom_service):
        """
        示例 4: 使用 custom_service fixture 创建自定义配置的服务
        
        custom_service 是一个工厂函数，可以创建多个不同配置的服务
        """
        # 创建第一个服务（使用不同的 base_url）
        service1 = custom_service(base_url="https://api1.example.com")
        
        # 模拟第一个 API 的响应
        mock_response1 = Mock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {'api': 'api1'}
        mock_response1.headers = {'Content-Type': 'application/json'}
        mock_response1.elapsed.total_seconds.return_value = 0.1
        mock_response1.url = "https://api1.example.com/data"
        mock_request.return_value = mock_response1
        
        response1 = service1.get("/data")
        assert response1.json()['api'] == 'api1'
        
        # 创建第二个服务（使用不同的认证）
        service2 = custom_service(
            base_url="https://api2.example.com",
            auth_type='bearer',
            auth_credentials={'token': 'custom_token_123'}
        )
        
        # 验证认证配置
        assert 'Authorization' in service2.session.headers
        assert service2.session.headers['Authorization'] == 'Bearer custom_token_123'
    
    @patch('api.services.base_service.requests.Session.request')
    def test_api_test_context(self, mock_request, api_test_context):
        """
        示例 5: 使用 api_test_context fixture 获取完整的测试上下文
        
        api_test_context 提供了日志记录器、缓存和 Allure 附件功能
        """
        # 获取日志记录器
        logger = api_test_context['logger']
        logger.info("Starting API test with context")
        
        # 获取缓存
        cache = api_test_context['cache']
        cache.set('test_data', 'test_value')
        assert cache.get('test_data') == 'test_value'
        
        # 获取 Allure 附件函数
        attach_to_allure = api_test_context['attach_to_allure']
        
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'result': 'success'}
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.elapsed.total_seconds.return_value = 0.3
        mock_response.url = "https://api.example.com/test"
        mock_response.text = '{"result": "success"}'
        mock_response.request = Mock()
        mock_response.request.method = 'GET'
        mock_response.request.url = "https://api.example.com/test"
        mock_response.request.headers = {}
        mock_response.request.body = None
        
        # 附加请求/响应到 Allure
        attach_to_allure(mock_response, "Test API Call")
        
        logger.info("API test with context completed")
        
        # 清理缓存
        cache.clear()
    
    @patch('api.services.base_service.requests.Session.request')
    def test_post_request_with_json_body(self, mock_request, base_service):
        """
        示例 6: 发送 POST 请求并携带 JSON 数据
        """
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'id': 100,
            'name': 'New User',
            'email': 'newuser@example.com'
        }
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.elapsed.total_seconds.return_value = 0.4
        mock_response.url = "https://api.example.com/users"
        mock_request.return_value = mock_response
        
        # 发送 POST 请求
        response = base_service.post(
            "/users",
            json={
                'name': 'New User',
                'email': 'newuser@example.com'
            }
        )
        
        # 验证响应
        assert response.status_code == 201
        assert response.json()['id'] == 100
        assert response.json()['name'] == 'New User'
    
    @patch('api.services.base_service.requests.Session.request')
    def test_status_code_validation(self, mock_request, base_service):
        """
        示例 7: 验证响应状态码
        """
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'ok'}
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.elapsed.total_seconds.return_value = 0.2
        mock_response.url = "https://api.example.com/status"
        mock_request.return_value = mock_response
        
        # 发送请求
        response = base_service.get("/status")
        
        # 验证状态码
        assert base_service.validate_status_code(response, 200) is True
        assert base_service.validate_status_code(response, [200, 201]) is True
        assert base_service.validate_status_code(response, 404) is False
    
    @patch('api.services.base_service.requests.Session.request')
    def test_chained_api_calls_with_cache(self, mock_request, base_service, api_cache):
        """
        示例 8: 链式 API 调用，使用缓存传递数据
        
        演示如何在多个 API 调用之间使用缓存传递数据
        """
        # 第一个 API 调用：获取用户列表
        mock_response1 = Mock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {
            'users': [
                {'id': 1, 'name': 'User 1'},
                {'id': 2, 'name': 'User 2'}
            ]
        }
        mock_response1.headers = {'Content-Type': 'application/json'}
        mock_response1.elapsed.total_seconds.return_value = 0.3
        mock_response1.url = "https://api.example.com/users"
        
        # 第二个 API 调用：获取用户详情
        mock_response2 = Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'id': 1,
            'name': 'User 1',
            'email': 'user1@example.com',
            'profile': {
                'age': 25,
                'city': 'New York'
            }
        }
        mock_response2.headers = {'Content-Type': 'application/json'}
        mock_response2.elapsed.total_seconds.return_value = 0.2
        mock_response2.url = "https://api.example.com/users/1"
        
        mock_request.side_effect = [mock_response1, mock_response2]
        
        # 步骤 1: 获取用户列表
        response1 = base_service.get("/users")
        
        # 提取第一个用户的 ID 并缓存
        first_user_id = base_service.extract_and_cache(
            response1,
            'first_user_id',
            'users.0.id'
        )
        assert first_user_id == 1
        
        # 步骤 2: 使用缓存的 ID 获取用户详情
        cached_user_id = api_cache.get('first_user_id')
        response2 = base_service.get(f"/users/{cached_user_id}")
        
        # 提取并缓存用户邮箱
        user_email = base_service.extract_and_cache(
            response2,
            'user_email',
            'email'
        )
        assert user_email == 'user1@example.com'
        
        # 验证缓存中的数据
        assert api_cache.get('first_user_id') == 1
        assert api_cache.get('user_email') == 'user1@example.com'
        
        # 清理缓存
        api_cache.clear()


# 运行示例
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
