"""
海龟交易法策略
经典趋势跟踪策略

策略逻辑：
- 价格突破20日最高价买入
- 价格跌破10日最低价卖出
- 使用ATR进行仓位管理
"""

import backtrader as bt


class TurtleStrategy(bt.Strategy):
    """
    海龟交易法策略
    
    参数：
    - entry_period: 入场周期（默认20日）
    - exit_period: 出场周期（默认10日）
    - atr_period: ATR周期（默认20日）
    - risk_factor: 风险因子（默认0.5）
    """
    
    params = (
        ('entry_period', 20),    # 入场周期
        ('exit_period', 10),     # 出场周期
        ('atr_period', 20),      # ATR周期
        ('risk_factor', 0.5),    # 风险因子
        ('max_position', 0.30),  # 最大仓位30%
        ('printlog', False),
    )
    
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        
        # 计算指标
        self.highest = bt.indicators.Highest(self.datahigh, period=self.params.entry_period)
        self.lowest = bt.indicators.Lowest(self.datalow, period=self.params.exit_period)
        self.atr = bt.indicators.ATR(self.datas[0], period=self.params.atr_period)
        
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
                # 设置止损价：买入价 - 2*ATR
                self.stop_price = self.buy_price - 2 * self.atr[0]
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
            # 止损检查
            if current_price <= self.stop_price:
                self.log(f'触发止损: {current_price:.2f} <= {self.stop_price:.2f}')
                self.order = self.sell()
                return
            
            # 跌破10日最低价卖出
            if current_price < self.lowest[0]:
                self.log(f'跌破最低价: {current_price:.2f} < {self.lowest[0]:.2f}')
                self.order = self.sell()
                return
        
        # 空仓检查：突破20日最高价买入
        else:
            if current_price > self.highest[-1]:  # 突破前一日的最高价
                # 计算仓位大小（基于ATR）
                atr_value = self.atr[0]
                if atr_value > 0:
                    # 海龟公式：仓位 = 账户价值 * 风险因子 / ATR
                    account_value = self.broker.getvalue()
                    risk_amount = account_value * self.params.risk_factor
                    position_size = int(risk_amount / atr_value / 100) * 100
                    
                    # 限制最大仓位
                    max_size = int(account_value * self.params.max_position / current_price / 100) * 100
                    position_size = min(position_size, max_size)
                    
                    if position_size >= 100:
                        self.log(f'突破买入: {current_price:.2f} > {self.highest[-1]:.2f}')
                        self.order = self.buy(size=position_size)


# 测试海龟策略
if __name__ == '__main__':
    print("海龟交易法策略已创建")
    print("参数:")
    print("  入场周期: 20日")
    print("  出场周期: 10日")
    print("  ATR周期: 20日")
    print("  风险因子: 0.5")
