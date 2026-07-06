"""
带基准对比的回测脚本
对比策略与沪深300的表现

使用方法：
    python scripts/run_backtest_with_benchmark.py
"""

import os
import sys

import backtrader as bt
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class RSIStrategy(bt.Strategy):
    """RSI策略"""
    
    params = (
        ('rsi_period', 21),
        ('rsi_oversold', 30),
        ('rsi_overbought', 70),
        ('stop_loss', 0.10),
        ('take_profit', 0.30),
        ('printlog', False),
    )
    
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.rsi = bt.indicators.RSI(self.datas[0].close, period=self.params.rsi_period)
        self.order = None
        self.buy_price = 0
        
    def next(self):
        if self.order:
            return
        
        current_price = self.dataclose[0]
        
        if self.position:
            profit_pct = (current_price - self.buy_price) / self.buy_price
            
            if profit_pct <= -self.params.stop_loss:
                self.order = self.sell()
                return
            
            if profit_pct >= self.params.take_profit:
                self.order = self.sell()
                return
            
            if self.rsi[0] > self.params.rsi_overbought:
                self.order = self.sell()
                return
        else:
            if self.rsi[0] < self.params.rsi_oversold:
                cash = self.broker.getcash()
                size = int(cash * 0.9 / current_price / 100) * 100
                if size >= 100:
                    self.order = self.buy(size=size)
                    self.buy_price = current_price
    
    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buy_price = order.executed.price
        self.order = None


def run_backtest_with_benchmark():
    """运行带基准对比的回测"""
    print("="*60)
    print("带基准对比的回测")
    print("="*60)
    print("基准指数: 沪深300")
    print()
    
    # 加载策略数据
    strategy_file = 'data/cache/000001_real_data.csv'
    benchmark_file = 'data/cache/hs300_benchmark.csv'
    
    if not os.path.exists(strategy_file):
        print(f"策略数据文件不存在: {strategy_file}")
        return
    
    if not os.path.exists(benchmark_file):
        print(f"基准数据文件不存在: {benchmark_file}")
        return
    
    strategy_df = pd.read_csv(strategy_file, index_col='date', parse_dates=True)
    benchmark_df = pd.read_csv(benchmark_file, index_col='date', parse_dates=True)
    
    # 创建引擎
    cerebro = bt.Cerebro()
    
    # 添加策略数据
    strategy_data = bt.feeds.PandasData(dataname=strategy_df)
    cerebro.adddata(strategy_data, name='strategy')
    
    # 添加基准数据
    benchmark_data = bt.feeds.PandasData(dataname=benchmark_df)
    cerebro.adddata(benchmark_data, name='benchmark')
    
    # 添加策略
    cerebro.addstrategy(RSIStrategy)
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
    
    # 获取策略结果
    final_value = cerebro.broker.getvalue()
    total_return = (final_value - 200000) / 200000
    
    sharpe = strat.analyzers.sharpe.get_analysis()
    drawdown = strat.analyzers.drawdown.get_analysis()
    trades = strat.analyzers.trades.get_analysis()
    
    # 计算基准收益
    benchmark_start = benchmark_df['close'].iloc[0]
    benchmark_end = benchmark_df['close'].iloc[-1]
    benchmark_return = (benchmark_end - benchmark_start) / benchmark_start
    
    # 计算超额收益
    excess_return = total_return - benchmark_return
    
    # 打印结果
    print("\n" + "="*60)
    print("回测结果")
    print("="*60)
    
    print(f"\n策略表现:")
    print(f"  最终资金: {final_value:,.2f}")
    print(f"  总收益: {final_value - 200000:,.2f}")
    print(f"  总收益率: {total_return*100:.2f}%")
    
    sharpe_ratio = sharpe.get('sharperatio', None)
    print(f"  夏普比率: {sharpe_ratio:.2f}" if sharpe_ratio else "  夏普比率: N/A")
    print(f"  最大回撤: {drawdown.get('max', {}).get('drawdown', 0):.2f}%")
    
    if 'total' in trades:
        total_trades = trades['total'].get('total', 0)
        won = trades.get('won', {}).get('total', 0)
        print(f"  总交易次数: {total_trades}")
        print(f"  胜率: {won/total_trades*100:.1f}%" if total_trades > 0 else "  胜率: N/A")
    
    print(f"\n基准表现（沪深300）:")
    print(f"  起始点位: {benchmark_start:.2f}")
    print(f"  结束点位: {benchmark_end:.2f}")
    print(f"  基准收益率: {benchmark_return*100:.2f}%")
    
    print(f"\n超额收益:")
    print(f"  超额收益率: {excess_return*100:.2f}%")
    
    if excess_return > 0:
        print(f"  评估: 策略跑赢基准")
    else:
        print(f"  评估: 策略跑输基准")
    
    print("="*60)
    
    return {
        'strategy_return': total_return,
        'benchmark_return': benchmark_return,
        'excess_return': excess_return,
    }


if __name__ == '__main__':
    run_backtest_with_benchmark()
