"""
配对交易策略
基于两只股票的价格差异进行交易

策略逻辑：
- 计算两只股票的价格比率
- 比率偏离均值时做多/做空
- 比率回归时平仓
"""

import backtrader as bt
import numpy as np


class PairTradingStrategy(bt.Strategy):
    """
    配对交易策略
    
    参数：
    - lookback_period: 回看周期（默认60日）
    - entry_threshold: 入场阈值（默认2倍标准差）
    - exit_threshold: 出场阈值（默认0.5倍标准差）
    """
    
    params = (
        ('lookback_period', 60),   # 回看周期
        ('entry_threshold', 2.0),  # 入场阈值
        ('exit_threshold', 0.5),   # 出场阈值
        ('stop_loss', 0.10),       # 止损10%
        ('printlog', False),
    )
    
    def __init__(self):
        # 需要两个数据源
        self.data0 = self.datas[0].close
        self.data1 = self.datas[1].close
        self.order = None
        self.position_type = None  # 'long' or 'short'
        self.entry_price = 0
        
    def log(self, txt, dt=None):
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt}: {txt}')
    
    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'买入 @ {order.executed.price:.2f}')
            else:
                self.log(f'卖出 @ {order.executed.price:.2f}')
        self.order = None
    
    def next(self):
        if self.order:
            return
        
        # 计算价格比率
        ratio = self.data0[0] / self.data1[0]
        
        # 计算比率统计
        if len(self.data0) > self.params.lookback_period:
            ratios = [self.data0[i] / self.data1[i] for i in range(-self.params.lookback_period, 0)]
            ratio_mean = np.mean(ratios)
            ratio_std = np.std(ratios)
            
            # 计算z-score
            z_score = (ratio - ratio_mean) / ratio_std if ratio_std > 0 else 0
        else:
            z_score = 0
        
        # 持仓检查
        if self.position:
            # 止损检查
            if self.position_type == 'long':
                profit_pct = (self.data0[0] - self.entry_price) / self.entry_price
            else:
                profit_pct = (self.entry_price - self.data0[0]) / self.entry_price
            
            if profit_pct <= -self.params.stop_loss:
                self.log(f'触发止损: {profit_pct*100:.2f}%')
                self.order = self.sell()
                self.position_type = None
                return
            
            # 出场条件
            if abs(z_score) < self.params.exit_threshold:
                self.log(f'出场信号: z-score={z_score:.2f}')
                self.order = self.sell()
                self.position_type = None
                return
        
        # 空仓检查
        else:
            # 做多信号：z-score < -entry_threshold
            if z_score < -self.params.entry_threshold:
                cash = self.broker.getcash()
                size = int(cash * 0.9 / self.data0[0] / 100) * 100
                if size >= 100:
                    self.log(f'做多信号: z-score={z_score:.2f}')
                    self.order = self.buy(size=size)
                    self.position_type = 'long'
                    self.entry_price = self.data0[0]
                    return
            
            # 做空信号：z-score > entry_threshold
            elif z_score > self.params.entry_threshold:
                # 注意：A股不能做空，这里只是逻辑展示
                self.log(f'做空信号（A股不可做空）: z-score={z_score:.2f}')
                return


if __name__ == '__main__':
    print("配对交易策略已创建")
    print("参数:")
    print("  回看周期: 60日")
    print("  入场阈值: 2倍标准差")
    print("  出场阈值: 0.5倍标准差")
    print("  止损: 10%")
