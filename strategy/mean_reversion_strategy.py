"""
均值回归策略
当价格偏离均值过多时，预期回归均值

策略逻辑：
- 价格低于均值-2倍标准差时买入
- 价格高于均值+2倍标准差时卖出
- 适用于震荡市场
"""

import backtrader as bt
import numpy as np


class MeanReversionStrategy(bt.Strategy):
    """
    均值回归策略
    
    参数：
    - ma_period: 均线周期（默认20日）
    - std_period: 标准差周期（默认20日）
    - entry_std: 入场标准差倍数（默认2.0）
    - exit_std: 出场标准差倍数（默认0.5）
    """
    
    params = (
        ('ma_period', 20),       # 均线周期
        ('std_period', 20),      # 标准差周期
        ('entry_std', 2.0),      # 入场标准差倍数
        ('exit_std', 0.5),       # 出场标准差倍数
        ('stop_loss', 0.10),     # 止损10%
        ('max_position', 0.30),  # 最大仓位30%
        ('printlog', False),
    )
    
    def __init__(self):
        self.dataclose = self.datas[0].close
        
        # 计算指标
        self.ma = bt.indicators.SimpleMovingAverage(self.dataclose, period=self.params.ma_period)
        self.std = bt.indicators.StdDev(self.dataclose, period=self.params.std_period)
        
        # 计算布林带
        self.upper_band = self.ma + self.params.entry_std * self.std
        self.lower_band = self.ma - self.params.entry_std * self.std
        self.exit_upper = self.ma + self.params.exit_std * self.std
        self.exit_lower = self.ma - self.params.exit_std * self.std
        
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
            # 计算收益率
            profit_pct = (current_price - self.buy_price) / self.buy_price
            
            # 止损检查
            if profit_pct <= -self.params.stop_loss:
                self.log(f'触发止损: {profit_pct*100:.2f}%')
                self.order = self.sell()
                return
            
            # 回归均值附近卖出
            if current_price >= self.exit_lower[0] and current_price <= self.exit_upper[0]:
                self.log(f'回归均值卖出: {current_price:.2f}')
                self.order = self.sell()
                return
            
            # 突破上轨卖出（止盈）
            if current_price >= self.upper_band[0]:
                self.log(f'突破上轨卖出: {current_price:.2f} >= {self.upper_band[0]:.2f}')
                self.order = self.sell()
                return
        
        # 空仓检查：跌破下轨买入
        else:
            if current_price <= self.lower_band[0]:
                # 计算仓位
                cash = self.broker.getcash()
                size = int(cash * 0.9 / current_price / 100) * 100
                
                # 限制最大仓位
                max_size = int(self.broker.getvalue() * self.params.max_position / current_price / 100) * 100
                size = min(size, max_size)
                
                if size >= 100:
                    self.log(f'跌破下轨买入: {current_price:.2f} <= {self.lower_band[0]:.2f}')
                    self.order = self.buy(size=size)


# 测试均值回归策略
if __name__ == '__main__':
    print("均值回归策略已创建")
    print("参数:")
    print("  均线周期: 20日")
    print("  标准差周期: 20日")
    print("  入场标准差: 2.0倍")
    print("  出场标准差: 0.5倍")
    print("  止损: 10%")
