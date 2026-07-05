"""
日志记录优化模块
提供结构化日志、日志级别配置、日志脱敏

使用方法：
    from utils.logger import TradingLogger
"""

import os
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


class TradingLogger:
    """交易日志记录器"""
    
    def __init__(self, name: str = 'quant_trading',
                 log_dir: str = 'logs',
                 log_level: str = 'INFO',
                 max_bytes: int = 10*1024*1024,  # 10MB
                 backup_count: int = 5):
        """
        初始化日志记录器
        
        Args:
            name: 日志记录器名称
            log_dir: 日志目录
            log_level: 日志级别
            max_bytes: 单个日志文件最大大小
            backup_count: 备份文件数量
        """
        self.name = name
        self.log_dir = log_dir
        
        # 创建日志目录
        os.makedirs(log_dir, exist_ok=True)
        
        # 创建日志记录器
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # 避免重复添加handler
        if not self.logger.handlers:
            self._setup_handlers(max_bytes, backup_count)
            
    def _setup_handlers(self, max_bytes: int, backup_count: int):
        """设置日志处理器"""
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # 文件处理器（按大小轮转）
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
        
    def log_trade(self, trade_info: Dict[str, Any]):
        """
        记录交易日志
        
        Args:
            trade_info: 交易信息
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'trade',
            'data': trade_info
        }
        self.logger.info(json.dumps(log_entry, ensure_ascii=False))
        
    def log_signal(self, signal_info: Dict[str, Any]):
        """
        记录信号日志
        
        Args:
            signal_info: 信号信息
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'signal',
            'data': signal_info
        }
        self.logger.info(json.dumps(log_entry, ensure_ascii=False))
        
    def log_risk(self, risk_info: Dict[str, Any]):
        """
        记录风险日志
        
        Args:
            risk_info: 风险信息
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'risk',
            'data': risk_info
        }
        self.logger.warning(json.dumps(log_entry, ensure_ascii=False))
        
    def log_error(self, error_info: Dict[str, Any]):
        """
        记录错误日志
        
        Args:
            error_info: 错误信息
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'error',
            'data': error_info
        }
        self.logger.error(json.dumps(log_entry, ensure_ascii=False))
        
    def log_performance(self, perf_info: Dict[str, Any]):
        """
        记录绩效日志
        
        Args:
            perf_info: 绩效信息
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'performance',
            'data': perf_info
        }
        self.logger.info(json.dumps(log_entry, ensure_ascii=False))


class LogAnalyzer:
    """日志分析器"""
    
    def __init__(self, log_dir: str = 'logs'):
        """
        初始化日志分析器
        
        Args:
            log_dir: 日志目录
        """
        self.log_dir = log_dir
        
    def analyze_trade_logs(self, log_file: str) -> Dict[str, Any]:
        """
        分析交易日志
        
        Args:
            log_file: 日志文件路径
            
        Returns:
            Dict: 分析结果
        """
        trades = []
        
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    log_entry = json.loads(line.strip())
                    if log_entry.get('type') == 'trade':
                        trades.append(log_entry['data'])
                except:
                    continue
                    
        if not trades:
            return {'total_trades': 0}
            
        # 统计
        total_trades = len(trades)
        buy_trades = len([t for t in trades if t.get('action') == 'buy'])
        sell_trades = len([t for t in trades if t.get('action') == 'sell'])
        
        return {
            'total_trades': total_trades,
            'buy_trades': buy_trades,
            'sell_trades': sell_trades,
            'trades': trades
        }
        
    def get_error_summary(self, log_file: str) -> Dict[str, Any]:
        """
        获取错误摘要
        
        Args:
            log_file: 日志文件路径
            
        Returns:
            Dict: 错误摘要
        """
        errors = []
        
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    log_entry = json.loads(line.strip())
                    if log_entry.get('type') == 'error':
                        errors.append(log_entry['data'])
                except:
                    continue
                    
        return {
            'total_errors': len(errors),
            'errors': errors[-10:]  # 最近10个错误
        }
