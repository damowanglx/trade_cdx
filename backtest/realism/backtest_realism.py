"""
回测真实性模块
添加滑点、涨跌停限制、冲击成本
"""

import numpy as np


class BacktestRealism:
    """回测真实性增强"""
    
    def __init__(self, slippage_pct=0.002, commission_pct=0.001, impact_cost_pct=0.001):
        self.slippage_pct = slippage_pct
        self.commission_pct = commission_pct
        self.impact_cost_pct = impact_cost_pct
        
    def apply_slippage(self, price, direction='buy'):
        """应用滑点"""
        if direction == 'buy':
            return price * (1 + self.slippage_pct)
        else:
            return price * (1 - self.slippage_pct)
    
    def apply_commission(self, amount):
        """应用手续费"""
        return amount * self.commission_pct
    
    def apply_impact_cost(self, price, volume, avg_volume):
        """应用冲击成本"""
        if avg_volume <= 0:
            return 0
        impact_ratio = volume / avg_volume
        return price * self.impact_cost_pct * impact_ratio
    
    def check_price_limit(self, price, previous_close, limit_pct=0.10):
        """检查涨跌停限制"""
        if previous_close <= 0:
            return True, price
        
        upper_limit = previous_close * (1 + limit_pct)
        lower_limit = previous_close * (1 - limit_pct)
        
        if price > upper_limit:
            return False, upper_limit
        elif price < lower_limit:
            return False, lower_limit
        else:
            return True, price
    
    def calculate_realistic_cost(self, price, quantity, direction='buy', avg_volume=1000000):
        """计算真实交易成本"""
        realistic_price = self.apply_slippage(price, direction)
        trade_amount = realistic_price * quantity
        commission = self.apply_commission(trade_amount)
        impact_cost = self.apply_impact_cost(realistic_price, quantity, avg_volume)
        total_cost = commission + impact_cost
        
        return {
            'original_price': price,
            'realistic_price': realistic_price,
            'quantity': quantity,
            'trade_amount': trade_amount,
            'commission': commission,
            'impact_cost': impact_cost,
            'total_cost': total_cost,
            'cost_pct': total_cost / trade_amount * 100 if trade_amount > 0 else 0,
        }
