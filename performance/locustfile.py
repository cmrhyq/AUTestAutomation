from locust import HttpUser, task, between, TaskSet, tag
from locust.contrib.fasthttp import FastHttpUser  # 性能更优，可选替换HttpUser
import random
import json
from datetime import datetime

# -------------------------- 全局配置（根据实际需求修改）--------------------------
# 目标服务基础URL（压测的接口域名）
BASE_URL = "https://api.example.com"
# 思考时间（用户每次请求间隔：最小秒数, 最大秒数）
THINK_TIME = (1, 3)
# 自定义请求头（如Token、Content-Type等）
COMMON_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Locust-Test/1.0",
    # "Authorization": "Bearer your-token-here",  # 如需鉴权请取消注释并填写
}
# 测试数据池（参数化用，可根据接口需求扩展）
TEST_DATA = {
    "user_ids": [f"user_{i:04d}" for i in range(1000)],  # 1000个测试用户ID
    "product_ids": [f"prod_{i:06d}" for i in range(5000)],  # 5000个测试商品ID
    "search_keywords": ["手机", "电脑", "耳机", "平板", "手表"],  # 搜索关键词
}
# 响应断言配置（状态码、响应内容校验）
ASSERT_CONFIG = {
    "success_status_code": 200,  # 期望响应状态码
    "required_response_keys": ["code", "message", "data"],  # 响应体必须包含的字段
    "success_code": 0,  # 业务成功状态码（如接口返回{"code":0}）
}

# -------------------------- 自定义任务集（核心压测逻辑）--------------------------
class ApiTaskSet(TaskSet):
    """接口压测任务集，包含各类接口请求逻辑"""

    def on_start(self):
        """用户启动时执行（如登录获取Token、初始化数据）"""
        print(f"用户 {self.user} 开始压测 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        # 示例：登录获取Token（如需动态Token可取消注释）
        # self.login()

    def on_stop(self):
        """用户结束时执行（如登出、清理资源）"""
        print(f"用户 {self.user} 结束压测 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def login(self):
        """示例：登录接口（获取Token并更新请求头）"""
        login_data = {
            "username": random.choice(["test_user_01", "test_user_02", "test_user_03"]),
            "password": "123456"
        }
        with self.client.post(
            url="/auth/login",
            json=login_data,
            headers=COMMON_HEADERS,
            name="登录接口",  # Locust UI中显示的任务名称
            catch_response=True  # 启用响应捕获（用于自定义断言）
        ) as response:
            # 响应断言
            self.assert_response(response, login_data)
            # 提取Token并更新全局请求头
            try:
                token = response.json()["data"]["token"]
                COMMON_HEADERS["Authorization"] = f"Bearer {token}"
                print(f"用户 {self.user} 登录成功，获取Token: {token[:20]}...")
            except Exception as e:
                response.failure(f"登录失败：{str(e)}")

    def assert_response(self, response, request_data=None):
        """通用响应断言方法（可根据接口特性扩展）"""
        # 1. 校验状态码
        if response.status_code != ASSERT_CONFIG["success_status_code"]:
            response.failure(
                f"状态码错误: 期望{ASSERT_CONFIG['success_status_code']}, 实际{response.status_code}\n"
                f"请求数据: {request_data}\n响应内容: {response.text}"
            )
            return

        # 2. 校验响应格式（JSON）
        try:
            response_json = response.json()
        except json.JSONDecodeError:
            response.failure(f"响应不是JSON格式: {response.text}")
            return

        # 3. 校验必填字段
        for key in ASSERT_CONFIG["required_response_keys"]:
            if key not in response_json:
                response.failure(f"响应缺少必填字段: {key}\n响应内容: {response_json}")
                return

        # 4. 校验业务状态码
        if response_json["code"] != ASSERT_CONFIG["success_code"]:
            response.failure(
                f"业务状态码错误: 期望{ASSERT_CONFIG['success_code']}, 实际{response_json['code']}\n"
                f"错误信息: {response_json.get('message', '无')}"
            )

    @tag("query", "read")  # 标签：用于Locust UI筛选执行特定任务
    @task(3)  # 权重3：执行概率是权重1任务的3倍
    def query_data(self):
        """示例：GET请求（查询数据）"""
        # 从测试数据池随机选择参数
        user_id = random.choice(TEST_DATA["user_ids"])
        product_id = random.choice(TEST_DATA["product_ids"])
        
        # 构造请求参数
        params = {
            "user_id": user_id,
            "product_id": product_id,
            "page": 1,
            "size": 10
        }

        # 发送GET请求
        self.client.get(
            url="/api/data/query",
            params=params,
            headers=COMMON_HEADERS,
            name="查询数据接口",
            catch_response=True
        )

    @tag("create", "write")
    @task(1)  # 权重1：执行概率较低（写操作通常压测强度低于读操作）
    def create_data(self):
        """示例：POST请求（创建数据）"""
        # 构造请求体
        request_body = {
            "user_id": random.choice(TEST_DATA["user_ids"]),
            "product_id": random.choice(TEST_DATA["product_ids"]),
            "keyword": random.choice(TEST_DATA["search_keywords"]),
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # 发送POST请求
        self.client.post(
            url="/api/data/create",
            json=request_body,
            headers=COMMON_HEADERS,
            name="创建数据接口",
            catch_response=True
        )

    @tag("update", "write")
    @task(1)
    def update_data(self):
        """示例：PUT请求（更新数据）"""
        request_body = {
            "user_id": random.choice(TEST_DATA["user_ids"]),
            "product_id": random.choice(TEST_DATA["product_ids"]),
            "status": random.choice([0, 1, 2]),
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.client.put(
            url=f"/api/data/update/{random.choice(TEST_DATA['product_ids'])}",  # 路径参数
            json=request_body,
            headers=COMMON_HEADERS,
            name="更新数据接口",
            catch_response=True
        )

    @tag("delete", "write")
    @task(0.5)  # 权重0.5：最低执行概率
    def delete_data(self):
        """示例：DELETE请求（删除数据）"""
        product_id = random.choice(TEST_DATA["product_ids"])

        self.client.delete(
            url=f"/api/data/delete/{product_id}",
            headers=COMMON_HEADERS,
            name="删除数据接口",
            catch_response=True
        )

# -------------------------- 压测用户类（配置用户行为）--------------------------
class ApiPerformanceUser(FastHttpUser):  # FastHttpUser性能优于HttpUser，建议使用
    """压测用户类：定义用户的任务集和行为参数"""
    # 绑定任务集
    tasks = [ApiTaskSet]
    # 思考时间（用户两次任务之间的间隔）
    wait_time = between(*THINK_TIME)
    # 基础URL（所有请求的前缀）
    base_url = BASE_URL

    # 可选：设置请求超时时间（默认无超时）
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client.timeout = 10  # 超时时间10秒

# -------------------------- 运行入口（支持命令行参数）--------------------------
if __name__ == "__main__":
    """
    运行方式：
    1. 本地UI模式（推荐调试）：
       locust -f locust_common_script.py --host=https://api.example.com
       然后访问 http://localhost:8089 配置并发用户数和每秒启动用户数
    
    2. 无UI模式（正式压测）：
       locust -f locust_common_script.py --host=https://api.example.com \
           -u 100 -r 10 -t 5m --csv=locust_result  # -u并发用户数 -r每秒启动数 -t压测时长 --csv输出结果
    
    3. 筛选标签执行（只执行查询类接口）：
       locust -f locust_common_script.py --host=https://api.example.com --tags=query
    """
    pass