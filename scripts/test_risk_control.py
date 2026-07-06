"""
带止损止盈的RSI策略
止损：-10%
止盈：+30%

使用方法：
    python scripts/test_risk_control.py
"""

import os
import sys

import backtrader as bt
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class RSIStrategyWithRiskControl(bt.Strategy):
    """
    带止损止盈的RSI策略
    
    参数：
    - rsi_period: RSI周期
    - rsi_oversold: 超卖阈值
    - rsi_overbought: 超买阈值
    - stop_loss: 止损比例（默认10%）
    - take_profit: 止盈比例（默认30%）
    """
    
    params = (
        ('rsi_period', 21),
        ('rsi_oversold', 30),
        ('rsi_overbought', 70),
        ('stop_loss', 0.10),      # 止损10%
        ('take_profit', 0.30),    # 止盈30%
        ('printlog', True),
    )
    
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.rsi = bt.indicators.RSI(self.datas[0].close, period=self.params.rsi_period)
        self.order = None
        self.buy_price = 0
        self.buy_date = None
        
    def log(self, txt, dt=None):
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt}: {txt}')
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buy_price = order.executed.price
                self.buy_date = self.datas[0].datetime.date(0)
                self.log(f'买入 - 价格: {order.executed.price:.2f}, 数量: {order.executed.size}')
            else:
                self.log(f'卖出 - 价格: {order.executed.price:.2f}, 数量: {order.executed.size}')
                self.buy_price = 0
                self.buy_date = None
        
        self.order = None
    
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(f'交易利润: {trade.pnlcomm:.2f}')
    
    def next(self):
        if self.order:
            return
        
        current_price = self.dataclose[0]
        
        # 持仓检查：止损止盈
        if self.position:
            # 计算收益率
            profit_pct = (current_price - self.buy_price) / self.buy_price
            
            # 止损检查
            if profit_pct <= -self.params.stop_loss:
                self.log(f'触发止损: {profit_pct*100:.2f}% <= -{self.params.stop_loss*100}%')
                self.order = self.sell()
                return
            
            # 止盈检查
            if profit_pct >= self.params.take_profit:
                self.log(f'触发止盈: {profit_pct*100:.2f}% >= {self.params.take_profit*100}%')
                self.order = self.sell()
                return
            
            # RSI超买卖出
            if self.rsi[0] > self.params.rsi_overbought:
                self.log(f'RSI超买: {self.rsi[0]:.2f} > {self.params.rsi_overbought}')
                self.order = self.sell()
                return
        
        # 空仓检查：买入信号
        else:
            if self.rsi[0] < self.params.rsi_oversold:
                # 计算仓位
                cash = self.broker.getcash()
                size = int(cash * 0.9 / current_price / 100) * 100
                if size >= 100:
                    self.log(f'RSI超卖买入: RSI={self.rsi[0]:.2f}, 价格={current_price:.2f}')
                    self.order = self.buy(size=size)


def run_backtest():
    """运行回测"""
    print("="*60)
    print("RSI策略 - 带止损止盈")
    print("="*60)
    print(f"止损: 10%")
    print(f"止盈: 30%")
    print()
    
    # 加载数据
    data_file = 'data/cache/000001_real_data.csv'
    if not os.path.exists(data_file):
        print(f"数据文件不存在: {data_file}")
        return
    
    df = pd.read_csv(data_file, index_col='date', parse_dates=True)
    
    # 创建引擎
    cerebro = bt.Cerebro()
    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)
    cerebro.addstrategy(RSIStrategyWithRiskControl)
    cerebro.broker.setcash(200000)
    cerebro.broker.setcommission(commission=0.001)
    
    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    
    # 运行回测
    print(f"初始资金: {200000:,.2f}")
    results = cerebro.run()
    strat = results[0]
    
    # 获取结果
    final_value = cerebro.broker.getvalue()
    total_return = (final_value - 200000) / 200000
    
    sharpe = strat.analyzers.sharpe.get_analysis()
    drawdown = strat.analyzers.drawdown.get_analysis()
    trades = strat.analyzers.trades.get_analysis()
    
    # 打印结果
    print("\n" + "="*60)
    print("回测结果")
    print("="*60)
    print(f"最终资金: {final_value:,.2f}")
    print(f"总收益: {final_value - 200000:,.2f}")
    print(f"总收益率: {total_return*100:.2f}%")
    sharpe_ratio = sharpe.get('sharperatio', None)
    print(f"夏普比率: {sharpe_ratio:.2f}" if sharpe_ratio else "夏普比率: N/A")
    print(f"最大回撤: {drawdown.get('max', {}).get('drawdown', 0):.2f}%")
    
    if 'total' in trades:
        total_trades = trades['total'].get('total', 0)
        won = trades.get('won', {}).get('total', 0)
        print(f"总交易次数: {total_trades}")
        print(f"盈利次数: {won}")
        print(f"胜率: {won/total_trades*100:.1f}%" if total_trades > 0 else "胜率: N/A")
    
    print("="*60)
    
    return results


if __name__ == '__main__':
    run_backtest()


