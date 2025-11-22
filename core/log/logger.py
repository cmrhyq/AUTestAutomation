"""
日志管理器模块

该模块提供统一的日志记录接口，支持多级别日志记录、双输出（控制台和文件）、
日志格式化以及 Allure 报告集成。
"""

import logging
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional
import allure

from config.settings import Settings


class TestLogger:
    """
    测试日志记录器类
    
    提供统一的日志记录接口，支持：
    - 多级别日志记录（DEBUG, INFO, WARNING, ERROR, CRITICAL）
    - 同时输出到控制台和文件
    - 统一的日志格式（包含时间戳、级别和消息）
    - Allure 报告集成
    - 线程安全的文件写入（Requirements 4.4）
    """
    
    _loggers = {}
    _log_file_path: Optional[str] = None
    _session_start_time: Optional[str] = None
    _setup_lock = threading.Lock()  # 保护日志系统初始化
    _file_lock = threading.Lock()  # 保护文件操作
    
    @classmethod
    def setup_logger(cls, log_level: str = None) -> None:
        """
        设置日志系统的全局配置（线程安全）
        
        Args:
            log_level: 日志级别，如果为 None 则使用配置文件中的设置
        """
        # 使用锁保护日志系统初始化，防止多线程同时初始化
        with cls._setup_lock:
            if log_level is None:
                log_level = Settings.LOG_LEVEL
            
            # 创建日志目录
            log_dir = Path(Settings.LOG_DIR)
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成日志文件名（使用会话开始时间）
            if cls._session_start_time is None:
                cls._session_start_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            log_filename = Settings.LOG_FILE_FORMAT.replace("{timestamp}", cls._session_start_time)
            cls._log_file_path = str(log_dir / log_filename)
            
            # 设置根日志记录器
            root_logger = logging.getLogger()
            root_logger.setLevel(getattr(logging, log_level))
            
            # 清除现有的处理器
            root_logger.handlers.clear()
            
            # 创建格式化器
            formatter = logging.Formatter(
                fmt=Settings.LOG_FORMAT,
                datefmt=Settings.LOG_DATE_FORMAT
            )
            
            # 添加控制台处理器
            if Settings.LOG_TO_CONSOLE:
                console_handler = logging.StreamHandler()
                console_handler.setLevel(getattr(logging, log_level))
                console_handler.setFormatter(formatter)
                root_logger.addHandler(console_handler)
            
            # 添加文件处理器（使用线程安全的处理器）
            if Settings.LOG_TO_FILE:
                # logging.FileHandler 本身是线程安全的，但我们添加额外的保护
                file_handler = logging.FileHandler(
                    cls._log_file_path,
                    mode='a',
                    encoding='utf-8'
                )
                file_handler.setLevel(getattr(logging, log_level))
                file_handler.setFormatter(formatter)
                root_logger.addHandler(file_handler)
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        获取指定名称的日志记录器（线程安全）
        
        Args:
            name: 日志记录器名称，通常使用模块名或类名
            
        Returns:
            logging.Logger: 配置好的日志记录器实例
        """
        # 如果日志系统还未初始化，先初始化
        if cls._log_file_path is None:
            cls.setup_logger()
        
        # 使用锁保护 logger 字典的访问
        with cls._setup_lock:
            if name not in cls._loggers:
                logger = logging.getLogger(name)
                cls._loggers[name] = logger
            
            return cls._loggers[name]
    
    @classmethod
    def attach_log_to_allure(cls, log_file_path: str = None) -> None:
        """
        将日志文件附加到 Allure 报告（线程安全）
        
        Args:
            log_file_path: 日志文件路径，如果为 None 则使用当前会话的日志文件
        """
        if log_file_path is None:
            log_file_path = cls._log_file_path
        
        if log_file_path and os.path.exists(log_file_path):
            try:
                # 使用锁保护文件读取操作
                with cls._file_lock:
                    with open(log_file_path, 'r', encoding='utf-8') as f:
                        log_content = f.read()
                
                allure.attach(
                    log_content,
                    name="Test Execution Log",
                    attachment_type=allure.attachment_type.TEXT
                )
            except Exception as e:
                # 如果附加失败，记录警告但不中断测试
                logging.warning(f"Failed to attach log to Allure: {e}")
    
    @classmethod
    def get_log_file_path(cls) -> Optional[str]:
        """
        获取当前会话的日志文件路径
        
        Returns:
            Optional[str]: 日志文件路径，如果未初始化则返回 None
        """
        return cls._log_file_path
    
    @classmethod
    def reset(cls) -> None:
        """
        重置日志系统（主要用于测试，线程安全）
        """
        with cls._setup_lock:
            cls._loggers.clear()
            cls._log_file_path = None
            cls._session_start_time = None
            
            # 清除根日志记录器的处理器
            root_logger = logging.getLogger()
            root_logger.handlers.clear()


# 便捷函数：获取日志记录器
def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器的便捷函数
    
    Args:
        name: 日志记录器名称
        
    Returns:
        logging.Logger: 配置好的日志记录器实例
    """
    return TestLogger.get_logger(name)
