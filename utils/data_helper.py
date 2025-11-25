"""
数据处理工具模块

该模块提供数据处理和转换的实用工具函数，包括 JSON 解析、数据提取、
数据验证、数据转换等功能。
"""

import json
import re
from typing import Any, Optional, Union, List, Dict
from datetime import datetime, date
from decimal import Decimal


class DataHelper:
    """
    数据处理辅助类
    
    提供常用的数据处理方法，包括：
    - JSON 解析和提取
    - JSONPath 查询
    - 数据类型转换
    - 数据验证
    - 字符串处理
    """
    
    @staticmethod
    def parse_json(json_string: str) -> Any:
        """
        解析 JSON 字符串
        
        Args:
            json_string: JSON 格式的字符串
            
        Returns:
            Any: 解析后的 Python 对象
            
        Raises:
            json.JSONDecodeError: JSON 解析失败
        """
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Failed to parse JSON: {e.msg}",
                e.doc,
                e.pos
            )
    
    @staticmethod
    def to_json_string(data: Any, indent: Optional[int] = None, ensure_ascii: bool = False) -> str:
        """
        将 Python 对象转换为 JSON 字符串
        
        Args:
            data: 要转换的 Python 对象
            indent: JSON 缩进空格数，None 表示紧凑格式
            ensure_ascii: 是否确保 ASCII 编码，默认为 False（支持中文）
            
        Returns:
            str: JSON 格式的字符串
            
        Raises:
            TypeError: 对象无法序列化为 JSON
        """
        try:
            return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii, default=str)
        except TypeError as e:
            raise TypeError(f"Failed to serialize to JSON: {e}")
    
    @staticmethod
    def extract_value(data: Any, path: str, default: Any = None) -> Any:
        """
        使用点号路径从嵌套数据结构中提取值
        
        支持的路径格式：
        - "key" - 字典键
        - "key.subkey" - 嵌套字典
        - "key[0]" - 列表索引
        - "key[0].subkey" - 混合访问
        
        Args:
            data: 数据源（字典或列表）
            path: 点号分隔的路径字符串
            default: 如果路径不存在时返回的默认值
            
        Returns:
            Any: 提取的值，如果路径不存在则返回 default
            
        Examples:
            >>> data = {"user": {"name": "Alice", "scores": [90, 85, 95]}}
            >>> extract_value(data, "user.name")
            'Alice'
            >>> extract_value(data, "user.scores[0]")
            90
        """
        if not path:
            return data
        
        try:
            current = data
            
            # 分割路径并处理每个部分
            parts = re.split(r'\.|\[', path)
            
            for part in parts:
                if not part:
                    continue
                
                # 处理数组索引 (例如: "0]")
                if part.endswith(']'):
                    index = int(part[:-1])
                    current = current[index]
                else:
                    # 处理字典键
                    current = current[part]
            
            return current
        except (KeyError, IndexError, TypeError, ValueError):
            return default
    
    @staticmethod
    def extract_multiple(data: Any, paths: Dict[str, str]) -> Dict[str, Any]:
        """
        从数据中提取多个值
        
        Args:
            data: 数据源
            paths: 字典，键为结果键名，值为提取路径
            
        Returns:
            Dict[str, Any]: 提取结果字典
            
        Examples:
            >>> data = {"user": {"name": "Alice", "age": 30}}
            >>> paths = {"username": "user.name", "user_age": "user.age"}
            >>> extract_multiple(data, paths)
            {'username': 'Alice', 'user_age': 30}
        """
        result = {}
        for key, path in paths.items():
            result[key] = DataHelper.extract_value(data, path)
        return result
    
    @staticmethod
    def flatten_dict(data: Dict, parent_key: str = '', separator: str = '.') -> Dict:
        """
        将嵌套字典扁平化
        
        Args:
            data: 嵌套字典
            parent_key: 父键名（用于递归）
            separator: 键名分隔符，默认为 '.'
            
        Returns:
            Dict: 扁平化后的字典
            
        Examples:
            >>> data = {"user": {"name": "Alice", "address": {"city": "NYC"}}}
            >>> flatten_dict(data)
            {'user.name': 'Alice', 'user.address.city': 'NYC'}
        """
        items = []
        
        for key, value in data.items():
            new_key = f"{parent_key}{separator}{key}" if parent_key else key
            
            if isinstance(value, dict):
                items.extend(DataHelper.flatten_dict(value, new_key, separator).items())
            else:
                items.append((new_key, value))
        
        return dict(items)
    
    @staticmethod
    def unflatten_dict(data: Dict, separator: str = '.') -> Dict:
        """
        将扁平化的字典还原为嵌套结构
        
        Args:
            data: 扁平化的字典
            separator: 键名分隔符，默认为 '.'
            
        Returns:
            Dict: 嵌套字典
            
        Examples:
            >>> data = {'user.name': 'Alice', 'user.address.city': 'NYC'}
            >>> unflatten_dict(data)
            {'user': {'name': 'Alice', 'address': {'city': 'NYC'}}}
        """
        result = {}
        
        for key, value in data.items():
            parts = key.split(separator)
            current = result
            
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            current[parts[-1]] = value
        
        return result
    
    @staticmethod
    def filter_dict(data: Dict, keys: List[str], include: bool = True) -> Dict:
        """
        过滤字典的键
        
        Args:
            data: 源字典
            keys: 要包含或排除的键列表
            include: True 表示只包含指定的键，False 表示排除指定的键
            
        Returns:
            Dict: 过滤后的字典
        """
        if include:
            return {k: v for k, v in data.items() if k in keys}
        else:
            return {k: v for k, v in data.items() if k not in keys}
    
    @staticmethod
    def merge_dicts(*dicts: Dict, deep: bool = False) -> Dict:
        """
        合并多个字典
        
        Args:
            *dicts: 要合并的字典
            deep: 是否深度合并（递归合并嵌套字典），默认为 False
            
        Returns:
            Dict: 合并后的字典
        """
        if not dicts:
            return {}
        
        result = {}
        
        for d in dicts:
            if not deep:
                result.update(d)
            else:
                for key, value in d.items():
                    if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                        result[key] = DataHelper.merge_dicts(result[key], value, deep=True)
                    else:
                        result[key] = value
        
        return result
    
    @staticmethod
    def is_valid_json(json_string: str) -> bool:
        """
        检查字符串是否为有效的 JSON
        
        Args:
            json_string: 要检查的字符串
            
        Returns:
            bool: 有效返回 True，否则返回 False
        """
        try:
            json.loads(json_string)
            return True
        except (json.JSONDecodeError, TypeError):
            return False
    
    @staticmethod
    def convert_to_type(value: Any, target_type: type, default: Any = None) -> Any:
        """
        将值转换为指定类型
        
        Args:
            value: 要转换的值
            target_type: 目标类型
            default: 转换失败时返回的默认值
            
        Returns:
            Any: 转换后的值，失败则返回 default
        """
        try:
            if target_type == bool:
                # 特殊处理布尔类型
                if isinstance(value, str):
                    return value.lower() in ('true', '1', 'yes', 'on')
                return bool(value)
            elif target_type == datetime:
                # 特殊处理日期时间
                if isinstance(value, str):
                    return datetime.fromisoformat(value)
                return target_type(value)
            else:
                return target_type(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def sanitize_string(text: str, remove_special_chars: bool = False) -> str:
        """
        清理字符串
        
        Args:
            text: 要清理的字符串
            remove_special_chars: 是否移除特殊字符，默认为 False
            
        Returns:
            str: 清理后的字符串
        """
        # 移除首尾空白
        text = text.strip()
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除特殊字符（如果需要）
        if remove_special_chars:
            text = re.sub(r'[^\w\s-]', '', text)
        
        return text
    
    @staticmethod
    def extract_numbers(text: str) -> List[Union[int, float]]:
        """
        从字符串中提取所有数字
        
        Args:
            text: 源字符串
            
        Returns:
            List[Union[int, float]]: 提取的数字列表
        """
        # 匹配整数和浮点数
        pattern = r'-?\d+\.?\d*'
        matches = re.findall(pattern, text)
        
        numbers = []
        for match in matches:
            if '.' in match:
                numbers.append(float(match))
            else:
                numbers.append(int(match))
        
        return numbers
    
    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """
        从字符串中提取所有电子邮件地址
        
        Args:
            text: 源字符串
            
        Returns:
            List[str]: 提取的电子邮件地址列表
        """
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(pattern, text)
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """
        从字符串中提取所有 URL
        
        Args:
            text: 源字符串
            
        Returns:
            List[str]: 提取的 URL 列表
        """
        pattern = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)'
        return re.findall(pattern, text)
    
    @staticmethod
    def compare_dicts(dict1: Dict, dict2: Dict, ignore_keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        比较两个字典的差异
        
        Args:
            dict1: 第一个字典
            dict2: 第二个字典
            ignore_keys: 要忽略的键列表
            
        Returns:
            Dict[str, Any]: 差异信息，包含 'added', 'removed', 'modified', 'unchanged'
        """
        ignore_keys = ignore_keys or []
        
        keys1 = set(dict1.keys()) - set(ignore_keys)
        keys2 = set(dict2.keys()) - set(ignore_keys)
        
        result = {
            'added': {},
            'removed': {},
            'modified': {},
            'unchanged': {}
        }
        
        # 新增的键
        for key in keys2 - keys1:
            result['added'][key] = dict2[key]
        
        # 删除的键
        for key in keys1 - keys2:
            result['removed'][key] = dict1[key]
        
        # 共同的键
        for key in keys1 & keys2:
            if dict1[key] != dict2[key]:
                result['modified'][key] = {
                    'old': dict1[key],
                    'new': dict2[key]
                }
            else:
                result['unchanged'][key] = dict1[key]
        
        return result
    
    @staticmethod
    def generate_test_data(template: Dict, count: int = 1) -> List[Dict]:
        """
        根据模板生成测试数据
        
        Args:
            template: 数据模板字典
            count: 生成数据的数量
            
        Returns:
            List[Dict]: 生成的测试数据列表
        """
        import copy
        
        result = []
        for i in range(count):
            data = copy.deepcopy(template)
            # 可以在这里添加更复杂的数据生成逻辑
            result.append(data)
        
        return result
    
    @staticmethod
    def validate_schema(data: Dict, schema: Dict) -> tuple[bool, List[str]]:
        """
        简单的数据结构验证
        
        Args:
            data: 要验证的数据
            schema: 验证模式，格式为 {key: type}
            
        Returns:
            tuple[bool, List[str]]: (是否有效, 错误信息列表)
        """
        errors = []
        
        for key, expected_type in schema.items():
            if key not in data:
                errors.append(f"Missing required key: {key}")
            elif not isinstance(data[key], expected_type):
                errors.append(
                    f"Invalid type for key '{key}': expected {expected_type.__name__}, "
                    f"got {type(data[key]).__name__}"
                )
        
        return len(errors) == 0, errors
    
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """
        格式化字节大小为人类可读的格式
        
        Args:
            size_bytes: 字节数
            
        Returns:
            str: 格式化后的大小字符串（如 "1.5 MB"）
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """
        格式化时长为人类可读的格式
        
        Args:
            seconds: 秒数
            
        Returns:
            str: 格式化后的时长字符串（如 "1h 30m 45s"）
        """
        if seconds < 60:
            return f"{seconds:.2f}s"
        
        minutes = int(seconds // 60)
        seconds = seconds % 60
        
        if minutes < 60:
            return f"{minutes}m {seconds:.2f}s"
        
        hours = minutes // 60
        minutes = minutes % 60
        
        return f"{hours}h {minutes}m {seconds:.2f}s"
    
    @staticmethod
    def chunk_list(data: List, chunk_size: int) -> List[List]:
        """
        将列表分割成指定大小的块
        
        Args:
            data: 源列表
            chunk_size: 每块的大小
            
        Returns:
            List[List]: 分割后的列表
        """
        return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
    
    @staticmethod
    def remove_duplicates(data: List, key: Optional[str] = None) -> List:
        """
        移除列表中的重复项
        
        Args:
            data: 源列表
            key: 如果列表元素是字典，指定用于判断重复的键
            
        Returns:
            List: 去重后的列表
        """
        if not data:
            return []
        
        if key is None:
            # 简单类型去重
            seen = set()
            result = []
            for item in data:
                if item not in seen:
                    seen.add(item)
                    result.append(item)
            return result
        else:
            # 字典列表去重
            seen = set()
            result = []
            for item in data:
                value = item.get(key)
                if value not in seen:
                    seen.add(value)
                    result.append(item)
            return result


# 便捷函数
def parse_json(json_string: str) -> Any:
    """解析 JSON 字符串的便捷函数"""
    return DataHelper.parse_json(json_string)


def to_json(data: Any, indent: Optional[int] = None) -> str:
    """转换为 JSON 字符串的便捷函数"""
    return DataHelper.to_json_string(data, indent)


def extract_value(data: Any, path: str, default: Any = None) -> Any:
    """提取嵌套值的便捷函数"""
    return DataHelper.extract_value(data, path, default)


def flatten_dict(data: Dict, separator: str = '.') -> Dict:
    """扁平化字典的便捷函数"""
    return DataHelper.flatten_dict(data, '', separator)


def merge_dicts(*dicts: Dict, deep: bool = False) -> Dict:
    """合并字典的便捷函数"""
    return DataHelper.merge_dicts(*dicts, deep=deep)

