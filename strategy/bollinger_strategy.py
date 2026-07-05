"""
布林带策略
基于布林带指标进行交易

策略逻辑：
- 价格触及下轨买入
- 价格触及上轨卖出
- 适用于震荡市场
"""

import backtrader as bt
import numpy as np


class BollingerBandStrategy(bt.Strategy):
    """
    布林带策略
    
    参数：
    - bb_period: 布林带周期（默认20日）
    - bb_std: 标准差倍数（默认2.0）
    - stop_loss: 止损比例（默认10%）
    - take_profit: 止盈比例（默认30%）
    """
    
    params = (
        ('bb_period', 20),        # 布林带周期
        ('bb_std', 2.0),          # 标准差倍数
        ('stop_loss', 0.10),      # 止损10%
        ('take_profit', 0.30),    # 止盈30%
        ('max_position', 0.30),   # 最大仓位30%
        ('printlog', False),
    )
    
    def __init__(self):
        self.dataclose = self.datas[0].close
        
        # 计算布林带
        self.bb = bt.indicators.BollingerBands(
            self.dataclose, 
            period=self.params.bb_period,
            devfactor=self.params.bb_std
        )
        
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
            
            # 触及上轨卖出
            if current_price >= self.bb.lines.top[0]:
                self.log(f'触及上轨卖出: {current_price:.2f} >= {self.bb.lines.top[0]:.2f}')
                self.order = self.sell()
                return
        
        # 空仓检查：触及下轨买入
        else:
            if current_price <= self.bb.lines.bot[0]:
                # 计算仓位
                cash = self.broker.getcash()
                size = int(cash * 0.9 / current_price / 100) * 100
                
                # 限制最大仓位
                max_size = int(self.broker.getvalue() * self.params.max_position / current_price / 100) * 100
                size = min(size, max_size)
                
                if size >= 100:
                    self.log(f'触及下轨买入: {current_price:.2f} <= {self.bb.lines.bot[0]:.2f}')
                    self.order = self.buy(size=size)


if __name__ == '__main__':
    print("布林带策略已创建")
    print("参数:")
    print("  布林带周期: 20日")
    print("  标准差倍数: 2.0")
    print("  止损: 10%")
    print("  止盈: 30%")
