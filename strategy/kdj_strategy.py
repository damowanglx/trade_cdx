"""
KDJ策略
基于KDJ指标进行交易

策略逻辑：
- K线上穿D线买入
- K线下穿D线卖出
"""

import backtrader as bt
import numpy as np


class KDJStrategy(bt.Strategy):
    """KDJ策略"""
    
    params = (
        ('kdj_period', 9),
        ('kdj_signal', 3),
        ('stop_loss', 0.10),
        ('take_profit', 0.30),
        ('max_position', 0.30),
        ('printlog', False),
    )
    
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        
        self.highest = bt.indicators.Highest(self.datahigh, period=self.params.kdj_period)
        self.lowest = bt.indicators.Lowest(self.datalow, period=self.params.kdj_period)
        
        self.order = None
        self.buy_price = 0
        self.k_value = 50
        self.d_value = 50
        
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
        
        # 计算RSV
        highest = self.highest[0]
        lowest = self.lowest[0]
        
        if highest != lowest:
            rsv = (current_price - lowest) / (highest - lowest) * 100
        else:
            rsv = 50
        
        # 计算K值和D值
        self.k_value = 2/3 * self.k_value + 1/3 * rsv
        self.d_value = 2/3 * self.d_value + 1/3 * self.k_value
        j_value = 3 * self.k_value - 2 * self.d_value
        
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
            
            # K线下穿D线卖出
            if self.k_value < self.d_value and j_value > 80:
                self.log(f'KDJ卖出信号: K={self.k_value:.2f}, D={self.d_value:.2f}, J={j_value:.2f}')
                self.order = self.sell()
                return
        else:
            # K线上穿D线买入
            if self.k_value > self.d_value and j_value < 20:
                cash = self.broker.getcash()
                size = int(cash * 0.9 / current_price / 100) * 100
                max_size = int(self.broker.getvalue() * self.params.max_position / current_price / 100) * 100
                size = min(size, max_size)
                
                if size >= 100:
                    self.log(f'KDJ买入信号: K={self.k_value:.2f}, D={self.d_value:.2f}, J={j_value:.2f}')
                    self.order = self.buy(size=size)
