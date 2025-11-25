"""
数据缓存模块测试

验证 DataCache 的基本功能和线程安全性
"""

import threading
import pytest
from core.cache.data_cache import DataCache, get_cache


class TestDataCache:
    """DataCache 基本功能测试"""
    
    def setup_method(self):
        """每个测试前清理缓存"""
        cache = DataCache.get_instance()
        cache.clear()
    
    def test_singleton_pattern(self):
        """测试单例模式：多次获取应返回同一实例"""
        cache1 = DataCache.get_instance()
        cache2 = DataCache.get_instance()
        cache3 = get_cache()
        
        assert cache1 is cache2
        assert cache2 is cache3
        assert id(cache1) == id(cache2) == id(cache3)
    
    def test_set_and_get(self):
        """测试基本的存储和获取功能"""
        cache = DataCache.get_instance()
        
        # 存储不同类型的数据
        cache.set("string_key", "test_value")
        cache.set("int_key", 12345)
        cache.set("list_key", [1, 2, 3])
        cache.set("dict_key", {"name": "test", "age": 30})
        
        # 验证获取的值正确
        assert cache.get("string_key") == "test_value"
        assert cache.get("int_key") == 12345
        assert cache.get("list_key") == [1, 2, 3]
        assert cache.get("dict_key") == {"name": "test", "age": 30}
    
    def test_get_with_default(self):
        """测试获取不存在的键时返回默认值"""
        cache = DataCache.get_instance()
        
        # 不存在的键应返回 None
        assert cache.get("nonexistent") is None
        
        # 使用自定义默认值
        assert cache.get("nonexistent", "default") == "default"
        assert cache.get("nonexistent", 0) == 0
    
    def test_has_key(self):
        """测试检查键是否存在"""
        cache = DataCache.get_instance()
        
        # 初始状态键不存在
        assert not cache.has("test_key")
        
        # 存储后键应存在
        cache.set("test_key", "value")
        assert cache.has("test_key")
        
        # 清空后键不存在
        cache.clear()
        assert not cache.has("test_key")
    
    def test_update_existing_key(self):
        """测试更新已存在的键"""
        cache = DataCache.get_instance()
        
        # 首次存储
        cache.set("key", "old_value")
        assert cache.get("key") == "old_value"
        
        # 更新值
        cache.set("key", "new_value")
        assert cache.get("key") == "new_value"
        
        # 多次更新
        cache.set("key", 100)
        assert cache.get("key") == 100
        
        cache.set("key", [1, 2, 3])
        assert cache.get("key") == [1, 2, 3]
    
    def test_clear(self):
        """测试清空缓存"""
        cache = DataCache.get_instance()
        
        # 存储多个键值对
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        assert cache.size() == 3
        
        # 清空缓存
        cache.clear()
        
        # 验证所有数据已清除
        assert cache.size() == 0
        assert not cache.has("key1")
        assert not cache.has("key2")
        assert not cache.has("key3")
    
    def test_get_all_keys(self):
        """测试获取所有键"""
        cache = DataCache.get_instance()
        
        # 空缓存
        assert cache.get_all_keys() == []
        
        # 添加数据
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        keys = cache.get_all_keys()
        assert len(keys) == 3
        assert set(keys) == {"key1", "key2", "key3"}
    
    def test_size(self):
        """测试获取缓存大小"""
        cache = DataCache.get_instance()
        
        assert cache.size() == 0
        
        cache.set("key1", "value1")
        assert cache.size() == 1
        
        cache.set("key2", "value2")
        assert cache.size() == 2
        
        # 更新不改变大小
        cache.set("key1", "new_value")
        assert cache.size() == 2
        
        cache.clear()
        assert cache.size() == 0
    
    def test_thread_safety(self):
        """测试线程安全性"""
        cache = DataCache.get_instance()
        cache.clear()
        
        num_threads = 10
        operations_per_thread = 100
        
        def worker(thread_id):
            """每个线程执行的工作"""
            for i in range(operations_per_thread):
                key = f"thread_{thread_id}_key_{i}"
                value = f"thread_{thread_id}_value_{i}"
                
                # 写入
                cache.set(key, value)
                
                # 读取验证
                assert cache.get(key) == value
                assert cache.has(key)
        
        # 创建并启动多个线程
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证所有数据都正确存储
        expected_size = num_threads * operations_per_thread
        assert cache.size() == expected_size
    
    def test_concurrent_updates(self):
        """测试并发更新同一键的线程安全性"""
        cache = DataCache.get_instance()
        cache.clear()
        
        key = "shared_key"
        num_threads = 20
        updates_per_thread = 50
        
        def updater(thread_id):
            """每个线程更新同一个键"""
            for i in range(updates_per_thread):
                cache.set(key, f"thread_{thread_id}_update_{i}")
        
        # 创建并启动多个线程
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=updater, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证键存在且有值（具体值取决于线程调度）
        assert cache.has(key)
        assert cache.get(key) is not None
        assert cache.size() == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
