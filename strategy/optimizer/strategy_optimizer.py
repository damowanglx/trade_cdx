"""
策略参数优化模块
支持动态参数、仓位管理、止损止盈
"""

import numpy as np
import pandas as pd


class StrategyOptimizer:
    """策略参数优化器"""
    
    def __init__(self):
        self.market_regime = 'neutral'
        
    def detect_market_regime(self, prices, window=60):
        """检测市场环境"""
        if len(prices) < window:
            return 'neutral'
        
        ma = prices.rolling(window).mean()
        current_price = prices.iloc[-1]
        current_ma = ma.iloc[-1]
        trend = (current_price - current_ma) / current_ma
        
        if trend > 0.05:
            return 'bull'
        elif trend < -0.05:
            return 'bear'
        else:
            return 'neutral'
    
    def optimize_rsi_params(self, market_regime):
        """根据市场环境优化RSI参数"""
        if market_regime == 'bull':
            return {'rsi_period': 14, 'rsi_oversold': 35, 'rsi_overbought': 75}
        elif market_regime == 'bear':
            return {'rsi_period': 21, 'rsi_oversold': 25, 'rsi_overbought': 65}
        else:
            return {'rsi_period': 21, 'rsi_oversold': 30, 'rsi_overbought': 70}
    
    def calculate_position_size(self, capital, price, volatility, method='kelly'):
        """计算仓位大小"""
        if method == 'kelly':
            win_rate = 0.6
            win_loss_ratio = 2.0
            kelly = win_rate - (1 - win_rate) / win_loss_ratio
            kelly = kelly * 0.5
            position_pct = max(0.1, min(kelly, 0.3))
        elif method == 'atr':
            if volatility > 0:
                risk_amount = capital * 0.02
                position_size = risk_amount / volatility
                position_pct = position_size * price / capital
                position_pct = max(0.1, min(position_pct, 0.3))
            else:
                position_pct = 0.2
        else:
            position_pct = 0.2
        
        invest_amount = capital * position_pct
        buy_quantity = int(invest_amount / price / 100) * 100
        
        return {
            'position_pct': position_pct,
            'invest_amount': invest_amount,
            'buy_quantity': buy_quantity,
        }
    
    def calculate_dynamic_stop_loss(self, price, atr, method='atr'):
        """计算动态止损"""
        if method == 'fixed':
            stop_loss_pct = 0.10
            stop_price = price * (1 - stop_loss_pct)
        elif method == 'atr':
            stop_price = price - 2 * atr
            stop_loss_pct = (price - stop_price) / price
        else:
            stop_loss_pct = 0.10
            stop_price = price * (1 - stop_loss_pct)
        
        return {'stop_price': stop_price, 'stop_loss_pct': stop_loss_pct}
    
    def calculate_dynamic_take_profit(self, price, atr, method='atr'):
        """计算动态止盈"""
        if method == 'fixed':
            take_profit_pct = 0.30
            take_profit_price = price * (1 + take_profit_pct)
        elif method == 'atr':
            take_profit_price = price + 3 * atr
            take_profit_pct = (take_profit_price - price) / price
        else:
            take_profit_pct = 0.30
            take_profit_price = price * (1 + take_profit_pct)
        
        return {'take_profit_price': take_profit_price, 'take_profit_pct': take_profit_pct}
