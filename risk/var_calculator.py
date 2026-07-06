"""
VaR风险价值模块
计算投资组合的风险价值

使用方法：
    from risk.var_calculator import VaRCalculator
"""

from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd


class VaRCalculator:
    """VaR风险价值计算器"""
    
    def __init__(self, confidence_level: float = 0.95):
        """
        初始化VaR计算器
        
        Args:
            confidence_level: 置信水平（默认95%）
        """
        self.confidence_level = confidence_level
        
    def calculate_var(self, returns: pd.Series, 
                     method: str = 'historical',
                     holding_period: int = 1) -> float:
        """
        计算VaR
        
        Args:
            returns: 收益率序列
            method: 计算方法（historical/parametric）
            holding_period: 持有期（天）
            
        Returns:
            float: VaR值
        """
        if method == 'historical':
            return self._historical_var(returns, holding_period)
        elif method == 'parametric':
            return self._parametric_var(returns, holding_period)
        else:
            raise ValueError(f"不支持的VaR计算方法: {method}")
            
    def _historical_var(self, returns: pd.Series, holding_period: int) -> float:
        """
        历史模拟法计算VaR
        
        Args:
            returns: 收益率序列
            holding_period: 持有期
            
        Returns:
            float: VaR值
        """
        # 调整持有期
        if holding_period > 1:
            returns = returns.rolling(holding_period).sum().dropna()
            
        # 计算分位数
        var = np.percentile(returns, (1 - self.confidence_level) * 100)
        return abs(var)
        
    def _parametric_var(self, returns: pd.Series, holding_period: int) -> float:
        """
        参数法计算VaR（假设正态分布）
        
        Args:
            returns: 收益率序列
            holding_period: 持有期
            
        Returns:
            float: VaR值
        """
        mu = returns.mean()
        sigma = returns.std()
        
        # 调整持有期
        mu_adj = mu * holding_period
        sigma_adj = sigma * np.sqrt(holding_period)
        
        # 计算VaR（使用正态分布分位数）
        from scipy import stats
        z_score = stats.norm.ppf(1 - self.confidence_level)
        var = -(mu_adj + z_score * sigma_adj)
        
        return var
        
    def calculate_cvar(self, returns: pd.Series) -> float:
        """
        计算条件VaR（Expected Shortfall）
        
        Args:
            returns: 收益率序列
            
        Returns:
            float: CVaR值
        """
        var = self._historical_var(returns, holding_period=1)
        # CVaR是超过VaR的平均损失
        cvar = returns[returns <= -var].mean()
        return abs(cvar)
        
    def stress_test(self, returns: pd.Series, 
                   scenarios: Dict[str, float]) -> Dict[str, float]:
        """
        压力测试
        
        Args:
            returns: 历史收益率
            scenarios: 压力情景（情景名称 -> 收益率调整）
            
        Returns:
            Dict: 各情景下的VaR
        """
        results = {}
        
        for scenario_name, adjustment in scenarios.items():
            # 调整收益率
            stressed_returns = returns * (1 + adjustment)
            
            # 计算VaR
            var = self.calculate_var(stressed_returns)
            results[scenario_name] = var
            
        return results


class RiskMetrics:
    """风险指标计算器"""
    
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
    def calculate_max_drawdown(returns: pd.Series) -> float:
        """
        计算最大回撤
        
        Args:
            returns: 收益率序列
            
        Returns:
            float: 最大回撤
        """
        cumulative = (1 + returns).cumprod()
        peak = cumulative.cummax()
        drawdown = (cumulative - peak) / peak
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
        max_drawdown = abs(RiskMetrics.calculate_max_drawdown(returns))
        
        if max_drawdown > 0:
            return (annual_return - risk_free_rate) / max_drawdown
        return 0
