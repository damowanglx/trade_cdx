"""
日志模块
提供结构化日志、日志轮转、日志分析

使用方法：
    from utils.logger import TradingLogger
"""

import os
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler


class TradingLogger:
    """交易日志记录器"""
    
    def __init__(self, name='quant_trading', log_dir='logs', 
                 max_bytes=10*1024*1024, backup_count=5):
        """
        初始化
        
        Args:
            name: 日志记录器名称
            log_dir: 日志目录
            max_bytes: 单个日志文件最大大小
            backup_count: 备份文件数量
        """
        self.name = name
        self.log_dir = log_dir
        
        os.makedirs(log_dir, exist_ok=True)
        
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        if not self.logger.handlers:
            self._setup_handlers(max_bytes, backup_count)
            
    def _setup_handlers(self, max_bytes, backup_count):
        """设置日志处理器"""
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # 文件处理器
        file_handler = RotatingFileHandler(
            os.path.join(self.log_dir, f'{self.name}.log'),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)
        
        # 错误日志处理器
        error_handler = RotatingFileHandler(
            os.path.join(self.log_dir, f'{self.name}_error.log'),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_format)
        self.logger.addHandler(error_handler)
        
    def info(self, message):
        """记录信息日志"""
        self.logger.info(message)
        
    def error(self, message):
        """记录错误日志"""
        self.logger.error(message)
        
    def warning(self, message):
        """记录警告日志"""
        self.logger.warning(message)
        
    def debug(self, message):
        """记录调试日志"""
        self.logger.debug(message)
        
    def log_trade(self, trade_info):
        """记录交易日志"""
        self.logger.info(f"交易: {trade_info}")
        
    def log_signal(self, signal_info):
        """记录信号日志"""
        self.logger.info(f"信号: {signal_info}")
        
    def log_risk(self, risk_info):
        """记录风险日志"""
        self.logger.warning(f"风险: {risk_info}")
