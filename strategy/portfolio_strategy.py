"""
策略组合模块
支持多策略组合、权重分配、信号聚合

使用方法：
    from strategy.portfolio_strategy import PortfolioStrategyManager
"""

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd


class StrategySignal:
    """策略信号"""
    
    def __init__(self, strategy_name: str, signal_type: str, 
                 strength: float, timestamp: pd.Timestamp):
        """
        初始化策略信号
        
        Args:
            strategy_name: 策略名称
            signal_type: 信号类型（buy/sell/hold）
            strength: 信号强度（0-1）
            timestamp: 时间戳
        """
        self.strategy_name = strategy_name
        self.signal_type = signal_type
        self.strength = strength
        self.timestamp = timestamp


class PortfolioStrategyManager:
    """策略组合管理器"""
    
    def __init__(self):
        """初始化策略组合管理器"""
        self.strategies = {}
        self.weights = {}
        self.signals_history = []
        
    def add_strategy(self, name: str, strategy_class: type, 
                    weight: float = 1.0, params: Optional[Dict] = None):
        """
        添加策略
        
        Args:
            name: 策略名称
            strategy_class: 策略类
            weight: 策略权重
            params: 策略参数
        """
        self.strategies[name] = {
            'class': strategy_class,
            'params': params or {},
            'weight': weight
        }
        self.weights[name] = weight
        
    def remove_strategy(self, name: str):
        """
        移除策略
        
        Args:
            name: 策略名称
        """
        if name in self.strategies:
            del self.strategies[name]
            del self.weights[name]
            
    def normalize_weights(self):
        """归一化权重"""
        total_weight = sum(self.weights.values())
        if total_weight > 0:
            self.weights = {k: v/total_weight for k, v in self.weights.items()}
            
    def aggregate_signals(self, signals: Dict[str, StrategySignal]) -> StrategySignal:
        """
        聚合多个策略信号
        
        Args:
            signals: 策略信号字典
            
        Returns:
            StrategySignal: 聚合后的信号
        """
        if not signals:
            return None
            
        # 计算加权信号
        buy_strength = 0
        sell_strength = 0
        total_weight = 0
        
        for name, signal in signals.items():
            weight = self.weights.get(name, 1.0)
            
            if signal.signal_type == 'buy':
                buy_strength += signal.strength * weight
            elif signal.signal_type == 'sell':
                sell_strength += signal.strength * weight
                
            total_weight += weight
            
        # 归一化
        if total_weight > 0:
            buy_strength /= total_weight
            sell_strength /= total_weight
            
        # 确定最终信号
        if buy_strength > sell_strength and buy_strength > 0.3:
            return StrategySignal(
                strategy_name='portfolio',
                signal_type='buy',
                strength=buy_strength,
                timestamp=signals[list(signals.keys())[0]].timestamp
            )
        elif sell_strength > buy_strength and sell_strength > 0.3:
            return StrategySignal(
                strategy_name='portfolio',
                signal_type='sell',
                strength=sell_strength,
                timestamp=signals[list(signals.keys())[0]].timestamp
            )
        else:
            return StrategySignal(
                strategy_name='portfolio',
                signal_type='hold',
                strength=0,
                timestamp=signals[list(signals.keys())[0]].timestamp
            )
            
    def calculate_portfolio_metrics(self, returns: pd.Series) -> Dict[str, float]:
        """
        计算组合指标
        
        Args:
            returns: 收益率序列
            
        Returns:
            Dict: 组合指标
        """
        metrics = {
            'total_return': (1 + returns).prod() - 1,
            'annual_return': returns.mean() * 252,
            'volatility': returns.std() * np.sqrt(252),
            'sharpe_ratio': (returns.mean() * 252) / (returns.std() * np.sqrt(252)) if returns.std() > 0 else 0,
            'max_drawdown': self._calculate_max_drawdown(returns),
            'win_rate': (returns > 0).sum() / len(returns) if len(returns) > 0 else 0
        }
        return metrics
        
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """计算最大回撤"""
        cumulative = (1 + returns).cumprod()
        peak = cumulative.cummax()
        drawdown = (cumulative - peak) / peak
        return drawdown.min()
        
    def get_strategy_count(self) -> int:
        """获取策略数量"""
        return len(self.strategies)
        
    def get_total_weight(self) -> float:
        """获取总权重"""
        return sum(self.weights.values())


class EqualWeightStrategy(PortfolioStrategyManager):
    """等权重策略组合"""
    
    def __init__(self):
        super().__init__()
        
    def add_strategy(self, name: str, strategy_class: type, params: Optional[Dict] = None):
        """添加策略（等权重）"""
        super().add_strategy(name, strategy_class, weight=1.0, params=params)
        self.normalize_weights()


class RiskParityStrategy(PortfolioStrategyManager):
    """风险平价策略组合"""
    
    def __init__(self):
        super().__init__()
        
    def add_strategy(self, name: str, strategy_class: type, 
                    volatility: float = 0.2, params: Optional[Dict] = None):
        """
        添加策略（基于波动率分配权重）
        
        Args:
            name: 策略名称
            strategy_class: 策略类
            volatility: 策略波动率
            params: 策略参数
        """
        # 权重与波动率成反比
        weight = 1.0 / volatility if volatility > 0 else 1.0
        super().add_strategy(name, strategy_class, weight=weight, params=params)
        self.normalize_weights()


class MomentumStrategy(PortfolioStrategyManager):
    """动量策略组合"""
    
    def __init__(self, lookback_period: int = 20):
        """
        初始化动量策略组合
        
        Args:
            lookback_period: 回看周期
        """
        super().__init__()
        self.lookback_period = lookback_period
        self.strategy_returns = {}
        
    def update_returns(self, name: str, returns: pd.Series):
        """
        更新策略收益率
        
        Args:
            name: 策略名称
            returns: 收益率序列
        """
        self.strategy_returns[name] = returns
        
    def calculate_momentum_weights(self) -> Dict[str, float]:
        """
        计算动量权重
        
        Returns:
            Dict: 策略权重
        """
        if not self.strategy_returns:
            return {}
            
        # 计算每个策略的动量得分
        momentum_scores = {}
        for name, returns in self.strategy_returns.items():
            if len(returns) >= self.lookback_period:
                recent_returns = returns.tail(self.lookback_period)
                momentum_scores[name] = recent_returns.mean()
                
        if not momentum_scores:
            return {}
            
        # 归一化权重（动量越高权重越大）
        total_score = sum(max(0, score) for score in momentum_scores.values())
        if total_score > 0:
            weights = {name: max(0, score)/total_score 
                      for name, score in momentum_scores.items()}
        else:
            # 等权重
            weights = {name: 1.0/len(momentum_scores) 
                      for name in momentum_scores.keys()}
            
        self.weights = weights
        return weights
