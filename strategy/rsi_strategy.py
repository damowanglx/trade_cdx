"""
RSI策略
相对强弱指标策略

策略逻辑：
- RSI低于30 → 超卖，买入信号
- RSI高于70 → 超买，卖出信号
"""

import backtrader as bt


class RSIStrategy(bt.Strategy):
    """
    RSI策略
    
    参数：
    - rsi_period: RSI计算周期（默认14）
    - rsi_oversold: 超卖阈值（默认30）
    - rsi_overbought: 超买阈值（默认70）
    """
    
    params = (
        ('rsi_period', 14),
        ('rsi_oversold', 30),
        ('rsi_overbought', 70),
        ('printlog', True),
    )
    
    def __init__(self):
        """初始化"""
        self.dataclose = self.datas[0].close
        
        # 计算RSI指标
        self.rsi = bt.indicators.RSI(
            self.datas[0].close,
            period=self.params.rsi_period
        )
        
        self.order = None
        self.buyprice = None
        
    def log(self, txt, dt=None):
        """日志"""
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt}: {txt}')
    
    def notify_order(self, order):
        """订单通知"""
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'买入 - 价格: {order.executed.price:.2f}')
                self.buyprice = order.executed.price
            else:
                self.log(f'卖出 - 价格: {order.executed.price:.2f}')
        
        self.order = None
    
    def notify_trade(self, trade):
        """交易通知"""
        if not trade.isclosed:
            return
        self.log(f'利润: {trade.pnlcomm:.2f}')
    
    def next(self):
        """策略逻辑"""
        if self.order:
            return
        
        if not self.position:
            # RSI低于超卖阈值，买入
            if self.rsi[0] < self.params.rsi_oversold:
                self.log(f'RSI超卖 ({self.rsi[0]:.2f}) - 买入')
                # 计算仓位
                cash = self.broker.getcash()
                size = int(cash * 0.9 / self.dataclose[0] / 100) * 100
                if size >= 100:
                    self.order = self.buy(size=size)
        else:
            # RSI高于超买阈值，卖出
            if self.rsi[0] > self.params.rsi_overbought:
                self.log(f'RSI超买 ({self.rsi[0]:.2f}) - 卖出')
                self.order = self.sell()
    
    def stop(self):
        """结束"""
        self.log(f'(RSI周期:{self.params.rsi_period}, '
                f'超卖:{self.params.rsi_oversold}, '
                f'超买:{self.params.rsi_overbought}) '
                f'最终资金: {self.broker.getvalue():.2f}')

