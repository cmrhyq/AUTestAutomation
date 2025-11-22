"""
API 测试示例演示

该文件演示了如何使用测试框架进行 API 测试，包括：
- 创建自定义 API 服务类
- 使用数据提取和缓存功能
- 集成 Allure 报告
- 处理认证和错误

这是一个独立的示例文件，可以直接运行：
    python examples/api_test_example.py

或作为 pytest 测试运行：
    pytest examples/api_test_example.py -v
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from base.api.services.jsonplaceholder_service import JSONPlaceholderService
from core.log.logger import TestLogger
from core.cache.data_cache import DataCache


def example_basic_api_calls():
    """示例 1: 基本的 API 调用"""
    print("\n" + "="*80)
    print("示例 1: 基本的 API 调用")
    print("="*80)
    
    # 创建日志记录器
    logger = TestLogger.get_logger("APIExample")
    
    # 创建服务实例
    service = JSONPlaceholderService(logger=logger)
    
    try:
        # 获取所有用户
        logger.info("获取所有用户列表...")
        users = service.get_all_users()
        print(f"\n✓ 成功获取 {len(users)} 个用户")
        print(f"  第一个用户: {users[0]['name']} ({users[0]['email']})")
        
        # 获取特定用户
        logger.info("获取用户 ID 1 的详细信息...")
        user = service.get_user_by_id(1)
        print(f"\n✓ 用户详情:")
        print(f"  姓名: {user['name']}")
        print(f"  用户名: {user['username']}")
        print(f"  邮箱: {user['email']}")
        print(f"  公司: {user['company']['name']}")
        
        # 获取用户的文章
        logger.info("获取用户的文章列表...")
        posts = service.get_user_posts(1)
        print(f"\n✓ 用户共有 {len(posts)} 篇文章")
        print(f"  第一篇文章标题: {posts[0]['title']}")
        
    finally:
        service.close()
    
    print("\n" + "="*80)


def example_create_and_update():
    """示例 2: 创建和更新资源"""
    print("\n" + "="*80)
    print("示例 2: 创建和更新资源")
    print("="*80)
    
    logger = TestLogger.get_logger("APIExample")
    service = JSONPlaceholderService(logger=logger)
    
    try:
        # 创建新文章
        logger.info("创建新文章...")
        new_post = service.create_post(
            user_id=1,
            title="我的测试文章",
            body="这是一篇用于演示 API 测试框架的文章内容。"
        )
        print(f"\n✓ 成功创建文章 ID: {new_post['id']}")
        print(f"  标题: {new_post['title']}")
        print(f"  内容: {new_post['body']}")
        
        # 更新文章
        logger.info("更新文章...")
        updated_post = service.update_post(
            post_id=1,
            title="更新后的标题",
            body="更新后的内容"
        )
        print(f"\n✓ 成功更新文章 ID: {updated_post['id']}")
        print(f"  新标题: {updated_post['title']}")
        
        # 部分更新
        logger.info("部分更新文章...")
        patched_post = service.patch_post(
            post_id=1,
            title="通过 PATCH 更新的标题"
        )
        print(f"\n✓ 成功部分更新文章")
        print(f"  新标题: {patched_post['title']}")
        
        # 删除文章
        logger.info("删除文章...")
        result = service.delete_post(1)
        print(f"\n✓ 删除操作结果: {'成功' if result else '失败'}")
        
    finally:
        service.close()
    
    print("\n" + "="*80)


def example_data_extraction_and_caching():
    """示例 3: 数据提取和缓存"""
    print("\n" + "="*80)
    print("示例 3: 数据提取和缓存")
    print("="*80)
    
    logger = TestLogger.get_logger("APIExample")
    service = JSONPlaceholderService(logger=logger)
    cache = DataCache.get_instance()
    
    try:
        # 清理缓存
        cache.clear()
        
        # 获取并缓存用户 ID
        logger.info("获取并缓存用户 ID...")
        user_id = service.get_and_cache_user_id(5)
        print(f"\n✓ 已缓存用户 ID: {user_id}")
        
        # 从缓存中获取
        cached_id = cache.get("user_id")
        print(f"  从缓存获取: {cached_id}")
        
        # 获取并缓存完整用户对象
        logger.info("获取并缓存完整用户对象...")
        user_data = service.get_and_cache_user(3, "full_user")
        print(f"\n✓ 已缓存用户对象: {user_data['name']}")
        
        # 从缓存中获取
        cached_user = cache.get("full_user")
        print(f"  从缓存获取用户名: {cached_user['name']}")
        print(f"  从缓存获取邮箱: {cached_user['email']}")
        
        # 创建并缓存文章
        logger.info("创建并缓存文章...")
        post_data = service.create_and_cache_post(
            user_id=1,
            title="缓存测试文章",
            body="这是用于测试缓存功能的文章",
            cache_key="test_post"
        )
        print(f"\n✓ 已缓存文章 ID: {post_data.get('id')}")
        
        # 演示数据共享
        logger.info("演示跨操作的数据共享...")
        
        # 步骤 1: 获取用户并缓存
        user_id = service.get_and_cache_user_id(2)
        cache.set("shared_user_id", user_id)
        print(f"\n✓ 步骤 1: 缓存用户 ID {user_id}")
        
        # 步骤 2: 使用缓存的用户 ID 获取文章
        cached_user_id = cache.get("shared_user_id")
        posts = service.get_user_posts(cached_user_id)
        print(f"  步骤 2: 使用缓存的用户 ID 获取到 {len(posts)} 篇文章")
        
        # 步骤 3: 缓存第一篇文章的 ID
        first_post_id = posts[0]["id"]
        cache.set("shared_post_id", first_post_id)
        print(f"  步骤 3: 缓存文章 ID {first_post_id}")
        
        # 步骤 4: 使用缓存的文章 ID 获取评论
        cached_post_id = cache.get("shared_post_id")
        comments = service.get_post_comments(cached_post_id)
        print(f"  步骤 4: 使用缓存的文章 ID 获取到 {len(comments)} 条评论")
        
        print(f"\n✓ 数据共享流程完成: 用户 {user_id} -> 文章 {first_post_id} -> {len(comments)} 条评论")
        
    finally:
        service.close()
        cache.clear()
    
    print("\n" + "="*80)


def example_error_handling():
    """示例 4: 错误处理"""
    print("\n" + "="*80)
    print("示例 4: 错误处理")
    print("="*80)
    
    logger = TestLogger.get_logger("APIExample")
    service = JSONPlaceholderService(logger=logger)
    
    try:
        # 测试状态码验证
        logger.info("测试状态码验证...")
        response = service.get("/users/1")
        
        is_200 = service.validate_status_code(response, 200)
        print(f"\n✓ 状态码 200 验证: {'通过' if is_200 else '失败'}")
        
        is_404 = service.validate_status_code(response, 404)
        print(f"  状态码 404 验证: {'通过' if is_404 else '失败'}")
        
        is_in_list = service.validate_status_code(response, [200, 201, 204])
        print(f"  状态码在 [200, 201, 204] 中: {'是' if is_in_list else '否'}")
        
        # 测试处理不存在的资源
        logger.info("测试处理 404 错误...")
        try:
            service.get_user_by_id(99999)
            print("\n✗ 应该抛出异常但没有")
        except Exception as e:
            print(f"\n✓ 成功捕获异常: {type(e).__name__}")
            print(f"  错误信息: {str(e)[:100]}...")
        
        # 测试数据提取错误处理
        logger.info("测试无效路径的数据提取...")
        response = service.get("/users/1")
        invalid_value = service._extract_by_path(response.json(), "invalid.path.here")
        print(f"\n✓ 无效路径返回: {invalid_value}")
        
    finally:
        service.close()
    
    print("\n" + "="*80)


def example_with_comments():
    """示例 5: 获取和处理评论"""
    print("\n" + "="*80)
    print("示例 5: 获取和处理评论")
    print("="*80)
    
    logger = TestLogger.get_logger("APIExample")
    service = JSONPlaceholderService(logger=logger)
    
    try:
        # 获取文章的评论
        logger.info("获取文章的评论...")
        comments = service.get_post_comments(1)
        print(f"\n✓ 文章 1 共有 {len(comments)} 条评论")
        
        if comments:
            first_comment = comments[0]
            print(f"\n  第一条评论:")
            print(f"    评论者: {first_comment['name']}")
            print(f"    邮箱: {first_comment['email']}")
            print(f"    内容: {first_comment['body'][:50]}...")
        
        # 使用查询参数获取评论
        logger.info("使用查询参数获取评论...")
        comments_by_query = service.get_comments_by_post(1)
        print(f"\n✓ 通过查询参数获取到 {len(comments_by_query)} 条评论")
        
        # 获取所有评论
        logger.info("获取所有评论...")
        all_comments = service.get_all_comments()
        print(f"\n✓ 系统共有 {len(all_comments)} 条评论")
        
    finally:
        service.close()
    
    print("\n" + "="*80)


def example_todos():
    """示例 6: 待办事项管理"""
    print("\n" + "="*80)
    print("示例 6: 待办事项管理")
    print("="*80)
    
    logger = TestLogger.get_logger("APIExample")
    service = JSONPlaceholderService(logger=logger)
    
    try:
        # 获取用户的待办事项
        logger.info("获取用户的待办事项...")
        todos = service.get_user_todos(1)
        
        # 统计完成情况
        completed = sum(1 for todo in todos if todo["completed"])
        incomplete = len(todos) - completed
        
        print(f"\n✓ 用户 1 的待办事项统计:")
        print(f"  总数: {len(todos)}")
        print(f"  已完成: {completed}")
        print(f"  未完成: {incomplete}")
        print(f"  完成率: {completed/len(todos)*100:.1f}%")
        
        # 显示前 3 个待办事项
        print(f"\n  前 3 个待办事项:")
        for i, todo in enumerate(todos[:3], 1):
            status = "✓" if todo["completed"] else "○"
            print(f"    {i}. [{status}] {todo['title']}")
        
        # 创建新待办事项
        logger.info("创建新待办事项...")
        new_todo = service.create_todo(
            user_id=1,
            title="测试框架演示待办事项",
            completed=False
        )
        print(f"\n✓ 成功创建待办事项 ID: {new_todo.get('id')}")
        print(f"  标题: {new_todo['title']}")
        print(f"  状态: {'已完成' if new_todo['completed'] else '未完成'}")
        
    finally:
        service.close()
    
    print("\n" + "="*80)


def main():
    """运行所有示例"""
    print("\n" + "="*80)
    print("API 测试框架示例演示")
    print("="*80)
    print("\n本示例演示了如何使用测试框架进行 API 测试")
    print("使用 JSONPlaceholder 公共 API (https://jsonplaceholder.typicode.com/)")
    
    try:
        # 运行所有示例
        example_basic_api_calls()
        example_create_and_update()
        example_data_extraction_and_caching()
        example_error_handling()
        example_with_comments()
        example_todos()
        
        print("\n" + "="*80)
        print("✓ 所有示例运行完成！")
        print("="*80)
        print("\n提示:")
        print("  - 查看 tests/api/test_jsonplaceholder_example.py 了解完整的测试用例")
        print("  - 查看 tests/api/README.md 了解详细的使用文档")
        print("  - 查看 api/services/jsonplaceholder_service.py 了解服务类实现")
        print("  - 运行 'pytest tests/api/ --alluredir=allure-results' 生成测试报告")
        print("  - 运行 'allure serve allure-results' 查看 Allure 报告")
        print("\n" + "="*80 + "\n")
        
    except Exception as e:
        print(f"\n✗ 示例运行出错: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
