"""
错误处理工具模块
提供统一的错误处理和异常管理

使用方法：
    from utils.error_handler import ErrorHandler, TradingError, DataError
"""

import logging
import traceback
from typing import Any, Callable, Optional
from functools import wraps


class TradingError(Exception):
    """交易错误基类"""
    pass


class DataError(TradingError):
    """数据错误"""
    pass


class StrategyError(TradingError):
    """策略错误"""
    pass


class BacktestError(TradingError):
    """回测错误"""
    pass


class RiskError(TradingError):
    """风险错误"""
    pass


class ErrorHandler:
    """错误处理器"""
    
    def __init__(self, logger_name: str = 'quant_trading'):
        """
        初始化错误处理器
        
        Args:
            logger_name: 日志记录器名称
        """
        self.logger = logging.getLogger(logger_name)
    
    def handle_error(self, error: Exception, context: str = "") -> None:
        """
        处理错误
        
        Args:
            error: 异常对象
            context: 错误上下文
        """
        error_msg = f"{context}: {str(error)}" if context else str(error)
        
        # 记录错误日志
        self.logger.error(error_msg)
        self.logger.error(traceback.format_exc())
        
        # 根据错误类型处理
        if isinstance(error, DataError):
            self._handle_data_error(error)
        elif isinstance(error, StrategyError):
            self._handle_strategy_error(error)
        elif isinstance(error, RiskError):
            self._handle_risk_error(error)
        else:
            self._handle_generic_error(error)
    
    def _handle_data_error(self, error: DataError) -> None:
        """处理数据错误"""
        self.logger.warning(f"数据错误: {error}")
        # 可以添加数据修复逻辑
    
    def _handle_strategy_error(self, error: StrategyError) -> None:
        """处理策略错误"""
        self.logger.warning(f"策略错误: {error}")
        # 可以添加策略切换逻辑
    
    def _handle_risk_error(self, error: RiskError) -> None:
        """处理风险错误"""
        self.logger.error(f"风险错误: {error}")
        # 可以添加紧急止损逻辑
    
    def _handle_generic_error(self, error: Exception) -> None:
        """处理通用错误"""
        self.logger.error(f"未知错误: {error}")


def error_handler(context: str = "") -> Callable:
    """
    错误处理装饰器
    
    Args:
        context: 错误上下文
        
    Returns:
        Callable: 装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handler = ErrorHandler()
                handler.handle_error(e, context or func.__name__)
                raise
        return wrapper
    return decorator


def safe_execute(func: Callable, *args, default: Any = None, **kwargs) -> Any:
    """
    安全执行函数
    
    Args:
        func: 要执行的函数
        *args: 位置参数
        default: 默认返回值
        **kwargs: 关键字参数
        
    Returns:
        Any: 函数返回值或默认值
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        handler = ErrorHandler()
        handler.handle_error(e, func.__name__)
        return default
