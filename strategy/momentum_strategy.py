"""
动量策略
基于价格动量进行交易

策略逻辑：
- 过去N天收益率为正则买入
- 过去N天收益率为负则卖出
- 适用于趋势市场
"""

import backtrader as bt
import numpy as np


class MomentumStrategy(bt.Strategy):
    """
    动量策略
    
    参数：
    - momentum_period: 动量周期（默认20日）
    - stop_loss: 止损比例（默认10%）
    - take_profit: 止盈比例（默认30%）
    """
    
    params = (
        ('momentum_period', 20),  # 动量周期
        ('stop_loss', 0.10),      # 止损10%
        ('take_profit', 0.30),    # 止盈30%
        ('max_position', 0.30),   # 最大仓位30%
        ('printlog', False),
    )
    
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.buy_price = 0
        
    def log(self, txt, dt=None):
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt}: {txt}')
    
    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buy_price = order.executed.price
                self.log(f'买入 @ {order.executed.price:.2f}')
            else:
                self.log(f'卖出 @ {order.executed.price:.2f}')
        self.order = None
    
    def next(self):
        if self.order:
            return
        
        current_price = self.dataclose[0]
        
        # 计算动量（过去N天收益率）
        if len(self.dataclose) > self.params.momentum_period:
            momentum = (current_price - self.dataclose[-self.params.momentum_period]) / self.dataclose[-self.params.momentum_period]
        else:
            momentum = 0
        
        # 持仓检查
        if self.position:
            profit_pct = (current_price - self.buy_price) / self.buy_price
            
            # 止损检查
            if profit_pct <= -self.params.stop_loss:
                self.log(f'触发止损: {profit_pct*100:.2f}%')
                self.order = self.sell()
                return
            
            # 止盈检查
            if profit_pct >= self.params.take_profit:
                self.log(f'触发止盈: {profit_pct*100:.2f}%')
                self.order = self.sell()
                return
            
            # 动量转负卖出
            if momentum < 0:
                self.log(f'动量转负卖出: {momentum:.4f}')
                self.order = self.sell()
                return
        
        # 空仓检查
        else:
            # 动量为正买入
            if momentum > 0.05:  # 5%以上动量
                cash = self.broker.getcash()
                size = int(cash * 0.9 / current_price / 100) * 100
                max_size = int(self.broker.getvalue() * self.params.max_position / current_price / 100) * 100
                size = min(size, max_size)
                
                if size >= 100:
                    self.log(f'动量买入: {momentum:.4f}')
                    self.order = self.buy(size=size)


if __name__ == '__main__':
    print("动量策略已创建")
    print("参数:")
    print("  动量周期: 20日")
    print("  动量阈值: 5%")
    print("  止损: 10%")
    print("  止盈: 30%")
