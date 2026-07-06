"""
代码复用模块
提取公共函数，减少代码重复

使用方法：
    from utils.common import CommonUtils
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd


class CommonUtils:
    """公共工具类"""
    
    @staticmethod
    def calculate_returns(prices: pd.Series) -> pd.Series:
        """
        计算收益率
        
        Args:
            prices: 价格序列
            
        Returns:
            Series: 收益率序列
        """
        return prices.pct_change()
        
    @staticmethod
    def calculate_log_returns(prices: pd.Series) -> pd.Series:
        """
        计算对数收益率
        
        Args:
            prices: 价格序列
            
        Returns:
            Series: 对数收益率序列
        """
        return np.log(prices / prices.shift(1))
        
    @staticmethod
    def calculate_moving_average(prices: pd.Series, window: int) -> pd.Series:
        """
        计算移动平均
        
        Args:
            prices: 价格序列
            window: 窗口大小
            
        Returns:
            Series: 移动平均序列
        """
        return prices.rolling(window=window).mean()
        
    @staticmethod
    def calculate_ema(prices: pd.Series, span: int) -> pd.Series:
        """
        计算指数移动平均
        
        Args:
            prices: 价格序列
            span: 跨度
            
        Returns:
            Series: EMA序列
        """
        return prices.ewm(span=span).mean()
        
    @staticmethod
    def calculate_volatility(returns: pd.Series, window: int = 20) -> pd.Series:
        """
        计算波动率
        
        Args:
            returns: 收益率序列
            window: 窗口大小
            
        Returns:
            Series: 波动率序列
        """
        return returns.rolling(window=window).std() * np.sqrt(252)
        
    @staticmethod
    def calculate_sharpe_ratio(returns: pd.Series, 
                              risk_free_rate: float = 0.001) -> float:
        """
        计算夏普比率
        
        Args:
            returns: 收益率序列
            risk_free_rate: 无风险利率
            
        Returns:
            float: 夏普比率
        """
        excess_returns = returns - risk_free_rate / 252
        return excess_returns.mean() / returns.std() * np.sqrt(252)
        
    @staticmethod
    def calculate_max_drawdown(values: pd.Series) -> float:
        """
        计算最大回撤
        
        Args:
            values: 净值序列
            
        Returns:
            float: 最大回撤
        """
        peak = values.cummax()
        drawdown = (values - peak) / peak
        return drawdown.min()
        
    @staticmethod
    def calculate_calmar_ratio(returns: pd.Series, 
                              risk_free_rate: float = 0.001) -> float:
        """
        计算卡尔玛比率
        
        Args:
            returns: 收益率序列
            risk_free_rate: 无风险利率
            
        Returns:
            float: 卡尔玛比率
        """
        annual_return = returns.mean() * 252
        max_drawdown = abs(CommonUtils.calculate_max_drawdown(
            (1 + returns).cumprod()
        ))
        
        if max_drawdown > 0:
            return (annual_return - risk_free_rate) / max_drawdown
        return 0
        
    @staticmethod
    def calculate_win_rate(returns: pd.Series) -> float:
        """
        计算胜率
        
        Args:
            returns: 收益率序列
            
        Returns:
            float: 胜率
        """
        if len(returns) == 0:
            return 0
        return (returns > 0).sum() / len(returns)
        
    @staticmethod
    def calculate_profit_factor(returns: pd.Series) -> float:
        """
        计算盈亏比
        
        Args:
            returns: 收益率序列
            
        Returns:
            float: 盈亏比
        """
        gains = returns[returns > 0].sum()
        losses = abs(returns[returns < 0].sum())
        
        if losses > 0:
            return gains / losses
        return float('inf')
        
    @staticmethod
    def normalize_data(data: pd.Series) -> pd.Series:
        """
        数据标准化
        
        Args:
            data: 数据序列
            
        Returns:
            Series: 标准化后的数据
        """
        return (data - data.mean()) / data.std()
        
    @staticmethod
    def min_max_normalize(data: pd.Series) -> pd.Series:
        """
        最小最大标准化
        
        Args:
            data: 数据序列
            
        Returns:
            Series: 标准化后的数据
        """
        return (data - data.min()) / (data.max() - data.min())
        
    @staticmethod
    def handle_missing_values(df: pd.DataFrame, 
                             method: str = 'ffill') -> pd.DataFrame:
        """
        处理缺失值
        
        Args:
            df: DataFrame
            method: 处理方法（ffill/bfill/drop）
            
        Returns:
            DataFrame: 处理后的数据
        """
        if method == 'ffill':
            return df.fillna(method='ffill')
        elif method == 'bfill':
            return df.fillna(method='bfill')
        elif method == 'drop':
            return df.dropna()
        else:
            return df
            
    @staticmethod
    def resample_data(df: pd.DataFrame, 
                     freq: str = 'D') -> pd.DataFrame:
        """
        数据重采样
        
        Args:
            df: DataFrame
            freq: 频率（D/W/M）
            
        Returns:
            DataFrame: 重采样后的数据
        """
        return df.resample(freq).last()
        
    @staticmethod
    def calculate_correlation_matrix(returns_dict: Dict[str, pd.Series]) -> pd.DataFrame:
        """
        计算相关性矩阵
        
        Args:
            returns_dict: 收益率字典
            
        Returns:
            DataFrame: 相关性矩阵
        """
        df = pd.DataFrame(returns_dict)
        return df.corr()
