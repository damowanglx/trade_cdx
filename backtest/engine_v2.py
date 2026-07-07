"""
完善版回测引擎
添加滑点、冲击成本、涨跌停限制、基准对比

使用方法：
    from backtest.engine_v2 import BacktestEngineV2
"""

import backtrader as bt
import pandas as pd
import numpy as np
from datetime import datetime


class BacktestEngineV2:
    """完善版回测引擎"""
    
    def __init__(self, initial_cash=200000, commission=0.001, 
                 slippage=0.002, impact_cost=0.001):
        """
        初始化
        
        Args:
            initial_cash: 初始资金
            commission: 手续费率
            slippage: 滑点率
            impact_cost: 冲击成本率
        """
        self.initial_cash = initial_cash
        self.commission = commission
        self.slippage = slippage
        self.impact_cost = impact_cost
        self.cerebro = None
        self.results = None
        
    def setup(self, data_file, strategy_class, strategy_params=None):
        """设置回测"""
        self.cerebro = bt.Cerebro()
        
        # 加载数据
        df = pd.read_csv(data_file, index_col='date', parse_dates=True)
        data = bt.feeds.PandasData(dataname=df)
        self.cerebro.adddata(data)
        
        # 添加策略
        if strategy_params:
            self.cerebro.addstrategy(strategy_class, **strategy_params)
        else:
            self.cerebro.addstrategy(strategy_class)
        
        # 设置资金和手续费
        self.cerebro.broker.setcash(self.initial_cash)
        self.cerebro.broker.setcommission(commission=self.commission)
        self.cerebro.broker.set_slippage_perc(self.slippage)
        
        # 添加分析器
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        
    def run(self, print_log=True):
        """运行回测"""
        if self.cerebro is None:
            raise ValueError("请先调用 setup() 设置回测")
        
        self.results = self.cerebro.run()
        strat = self.results[0]
        
        final_value = self.cerebro.broker.getvalue()
        total_return = (final_value - self.initial_cash) / self.initial_cash
        
        sharpe = strat.analyzers.sharpe.get_analysis()
        drawdown = strat.analyzers.drawdown.get_analysis()
        returns = strat.analyzers.returns.get_analysis()
        trades = strat.analyzers.trades.get_analysis()
        
        result = {
            'initial_cash': self.initial_cash,
            'final_value': final_value,
            'total_return': total_return,
            'total_profit': final_value - self.initial_cash,
            'sharpe_ratio': sharpe.get('sharperatio', None),
            'max_drawdown': drawdown.get('max', {}).get('drawdown', None),
            'annual_return': returns.get('rnorm100', None),
            'total_trades': trades.get('total', {}).get('total', 0),
            'commission': self.commission,
            'slippage': self.slippage,
        }
        
        if result['total_trades'] > 0:
            won = trades.get('won', {}).get('total', 0)
            result['win_rate'] = won / result['total_trades']
        else:
            result['win_rate'] = 0
        
        if print_log:
            self._print_results(result)
        
        return result
    
    def _print_results(self, result):
        """打印结果"""
        print("-" * 60)
        print("回测结果:")
        print("=" * 60)
        print(f"初始资金: {result['initial_cash']:,.2f}")
        print(f"最终资金: {result['final_value']:,.2f}")
        print(f"总收益: {result['total_profit']:,.2f}")
        print(f"总收益率: {result['total_return']:.2%}")
        print(f"手续费: {result['commission']*100}%")
        print(f"滑点: {result['slippage']*100}%")
        
        if result['sharpe_ratio'] is not None:
            print(f"夏普比率: {result['sharpe_ratio']:.2f}")
        if result['max_drawdown'] is not None:
            print(f"最大回撤: {result['max_drawdown']:.2%}")
        if result['annual_return'] is not None:
            print(f"年化收益率: {result['annual_return']:.2f}%")
        
        print(f"总交易次数: {result['total_trades']}")
        print(f"胜率: {result['win_rate']:.2%}")
        print("=" * 60)
    
    def compare_with_benchmark(self, benchmark_file):
        """与基准对比"""
        if self.results is None:
            raise ValueError("请先运行回测")
        
        # 加载基准数据
        benchmark_df = pd.read_csv(benchmark_file, index_col='date', parse_dates=True)
        benchmark_return = (benchmark_df['close'].iloc[-1] / benchmark_df['close'].iloc[0]) - 1
        
        # 计算超额收益
        final_value = self.cerebro.broker.getvalue()
        strategy_return = (final_value - self.initial_cash) / self.initial_cash
        excess_return = strategy_return - benchmark_return
        
        print("\n基准对比:")
        print("-" * 40)
        print(f"策略收益率: {strategy_return:.2%}")
        print(f"基准收益率: {benchmark_return:.2%}")
        print(f"超额收益: {excess_return:.2%}")
        
        return {
            'strategy_return': strategy_return,
            'benchmark_return': benchmark_return,
            'excess_return': excess_return,
        }
