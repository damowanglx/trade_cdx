"""
ATR策略
基于ATR（平均真实波幅）进行交易

策略逻辑：
- 使用ATR进行仓位管理
- ATR突破买入
- ATR回落卖出
"""

import backtrader as bt
import numpy as np


class ATRStrategy(bt.Strategy):
    """
    ATR策略
    
    参数：
    - atr_period: ATR周期（默认14日）
    - atr_multiplier: ATR乘数（默认2.0）
    - stop_loss: 止损比例（默认10%）
    - take_profit: 止盈比例（默认30%）
    """
    
    params = (
        ('atr_period', 14),        # ATR周期
        ('atr_multiplier', 2.0),   # ATR乘数
        ('stop_loss', 0.10),       # 止损10%
        ('take_profit', 0.30),     # 止盈30%
        ('max_position', 0.30),    # 最大仓位30%
        ('printlog', False),
    )
    
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        
        # 计算ATR
        self.atr = bt.indicators.ATR(self.datas[0], period=self.params.atr_period)
        
        # 计算移动平均
        self.ma = bt.indicators.SimpleMovingAverage(self.dataclose, period=20)
        
        self.order = None
        self.buy_price = 0
        self.stop_price = 0
        
    def log(self, txt, dt=None):
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt}: {txt}')
    
    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buy_price = order.executed.price
                # 设置止损价：买入价 - ATR * 乘数
                self.stop_price = self.buy_price - self.atr[0] * self.params.atr_multiplier
                self.log(f'买入 @ {order.executed.price:.2f}, 止损 @ {self.stop_price:.2f}')
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
            if current_price <= self.stop_price:
                self.log(f'触发止损: {current_price:.2f} <= {self.stop_price:.2f}')
                self.order = self.sell()
                return
            
            # 止盈检查
            if profit_pct >= self.params.take_profit:
                self.log(f'触发止盈: {profit_pct*100:.2f}%')
                self.order = self.sell()
                return
            
            # 价格跌破均线卖出
            if current_price < self.ma[0]:
                self.log(f'跌破均线卖出: {current_price:.2f} < {self.ma[0]:.2f}')
                self.order = self.sell()
                return
        
        # 空仓检查
        else:
            # 价格突破均线 + ATR买入
            if current_price > self.ma[0] + self.atr[0]:
                # 计算仓位（基于ATR）
                atr_value = self.atr[0]
                if atr_value > 0:
                    # ATR仓位管理
                    account_value = self.broker.getvalue()
                    risk_amount = account_value * 0.02  # 2%风险
                    position_size = int(risk_amount / atr_value / 100) * 100
                    
                    # 限制最大仓位
                    max_size = int(account_value * self.params.max_position / current_price / 100) * 100
                    size = min(position_size, max_size)
                    
                    if size >= 100:
                        self.log(f'ATR买入: {current_price:.2f} > {self.ma[0] + self.atr[0]:.2f}')
                        self.order = self.buy(size=size)


if __name__ == '__main__':
    print("ATR策略已创建")
    print("参数:")
    print("  ATR周期: 14日")
    print("  ATR乘数: 2.0")
    print("  止损: 10%")
    print("  止盈: 30%")
