"""
行业轮动策略
基于行业动量进行轮动

策略逻辑：
- 计算各行业ETF的动量
- 选择动量最强的行业
- 定期轮动调整
"""

import backtrader as bt
import numpy as np


class SectorRotationStrategy(bt.Strategy):
    """
    行业轮动策略
    
    参数：
    - momentum_period: 动量周期（默认20日）
    - rebalance_period: 调仓周期（默认20日）
    - top_n: 选择行业数量（默认3个）
    """
    
    params = (
        ('momentum_period', 20),   # 动量周期
        ('rebalance_period', 20),  # 调仓周期
        ('top_n', 3),              # 选择行业数量
        ('stop_loss', 0.10),       # 止损10%
        ('printlog', False),
    )
    
    def __init__(self):
        self.day_count = 0
        self.order = None
        self.buy_prices = {}
        
    def log(self, txt, dt=None):
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt}: {txt}')
    
    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buy_prices[order.data._name] = order.executed.price
                self.log(f'买入 {order.data._name} @ {order.executed.price:.2f}')
            else:
                self.log(f'卖出 {order.data._name} @ {order.executed.price:.2f}')
        self.order = None
    
    def next(self):
        self.day_count += 1
        
        # 到达调仓周期
        if self.day_count % self.params.rebalance_period == 0:
            self.rebalance()
        
        # 检查止损
        self.check_stop_loss()
    
    def rebalance(self):
        """调仓逻辑"""
        self.log(f'调仓日 - 第{self.day_count}天')
        
        # 计算各股票的动量
        momentum_scores = {}
        for data in self.datas:
            symbol = data._name
            if len(data.close) > self.params.momentum_period:
                momentum = (data.close[0] - data.close[-self.params.momentum_period]) / data.close[-self.params.momentum_period]
                momentum_scores[symbol] = momentum
        
        if not momentum_scores:
            return
        
        # 选择动量最强的股票
        sorted_stocks = sorted(momentum_scores.items(), key=lambda x: x[1], reverse=True)
        selected_stocks = [s[0] for s in sorted_stocks[:self.params.top_n]]
        
        self.log(f'选择股票: {selected_stocks}')
        
        # 卖出不在目标列表中的股票
        for data in self.datas:
            position = self.getposition(data)
            if position.size > 0 and data._name not in selected_stocks:
                self.sell(data, size=position.size)
        
        # 买入目标股票
        portfolio_value = self.broker.getvalue()
        per_stock_value = portfolio_value / self.params.top_n
        
        for data in self.datas:
            if data._name in selected_stocks:
                position = self.getposition(data)
                if position.size == 0:
                    size = int(per_stock_value / data.close[0] / 100) * 100
                    if size >= 100:
                        self.buy(data, size=size)
    
    def check_stop_loss(self):
        """检查止损"""
        for data in self.datas:
            position = self.getposition(data)
            if position.size > 0:
                buy_price = self.buy_prices.get(data._name, 0)
                if buy_price > 0:
                    profit_pct = (data.close[0] - buy_price) / buy_price
                    if profit_pct <= -self.params.stop_loss:
                        self.log(f'止损 {data._name}: {profit_pct*100:.2f}%')
                        self.sell(data, size=position.size)


if __name__ == '__main__':
    print("行业轮动策略已创建")
    print("参数:")
    print("  动量周期: 20日")
    print("  调仓周期: 20日")
    print("  选择行业: 3个")
    print("  止损: 10%")
