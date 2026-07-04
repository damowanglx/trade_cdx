"""
MACD策略
移动平均收敛/发散指标策略

策略逻辑：
- MACD线上穿信号线 → 买入信号（金叉）
- MACD线下穿信号线 → 卖出信号（死叉）
"""

import backtrader as bt


class MACDStrategy(bt.Strategy):
    """
    MACD策略
    
    参数：
    - fast_period: 快速EMA周期（默认12）
    - slow_period: 慢速EMA周期（默认26）
    - signal_period: 信号线周期（默认9）
    """
    
    params = (
        ('fast_period', 12),
        ('slow_period', 26),
        ('signal_period', 9),
        ('printlog', True),
    )
    
    def __init__(self):
        """初始化"""
        self.dataclose = self.datas[0].close
        
        # 计算MACD指标
        self.macd = bt.indicators.MACD(
            self.datas[0].close,
            period_me1=self.params.fast_period,
            period_me2=self.params.slow_period,
            period_signal=self.params.signal_period
        )
        
        # 计算交叉信号
        self.crossover = bt.indicators.CrossOver(
            self.macd.macd,
            self.macd.signal
        )
        
        self.order = None
        
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
            # MACD金叉，买入
            if self.crossover > 0:
                self.log(f'MACD金叉 - 买入')
                # 计算仓位
                cash = self.broker.getcash()
                size = int(cash * 0.9 / self.dataclose[0] / 100) * 100
                if size >= 100:
                    self.order = self.buy(size=size)
        else:
            # MACD死叉，卖出
            if self.crossover < 0:
                self.log(f'MACD死叉 - 卖出')
                self.order = self.sell()
    
    def stop(self):
        """结束"""
        self.log(f'(MACD: {self.params.fast_period}/{self.params.slow_period}/{self.params.signal_period}) '
                f'最终资金: {self.broker.getvalue():.2f}')

