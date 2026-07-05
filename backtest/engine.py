"""
回测引擎
整合数据、策略、风控、监控的完整回测框架
"""

import backtrader as bt
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, initial_cash=200000, commission=0.001, slippage=0.002):
        """
        初始化回测引擎
        
        Args:
            initial_cash: 初始资金
            commission: 手续费率
            slippage: 滑点率（默认0.2%）
        """
        self.initial_cash = initial_cash
        self.commission = commission
        self.slippage = slippage
        self.initial_cash = initial_cash
        self.commission = commission
        self.cerebro = None
        self.results = None
        
    def setup(self, data_file, strategy_class, strategy_params=None):
        self.cerebro = bt.Cerebro()
        
        if not os.path.exists(data_file):
            raise FileNotFoundError(f"数据文件不存在: {data_file}")
        
        dataframe = pd.read_csv(data_file, index_col='date', parse_dates=True)
        data = bt.feeds.PandasData(dataname=dataframe)
        self.cerebro.adddata(data)
        
        if strategy_params:
            self.cerebro.addstrategy(strategy_class, **strategy_params)
        else:
            self.cerebro.addstrategy(strategy_class)
        
        self.cerebro.broker.setcash(self.initial_cash)
        self.cerebro.broker.setcommission(commission=self.commission)
        
        # 设置滑点
        if self.slippage > 0:
            cerebro.broker.set_slippage_perc(self.slippage)
        
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        
        print(f"回测设置完成:")
        print(f"  数据文件: {data_file}")
        print(f"  策略: {strategy_class.__name__}")
        print(f"  初始资金: {self.initial_cash:,.2f}")
        print(f"  手续费: {self.commission*100}%")
        
    def run(self, print_log=True):
        if self.cerebro is None:
            raise ValueError("请先调用 setup() 设置回测")
        
        print("\n开始回测...")
        print("-" * 60)
        
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
        }
        
        if result['total_trades'] > 0:
            won = trades.get('won', {}).get('total', 0)
            result['win_rate'] = won / result['total_trades']
        else:
            result['win_rate'] = 0
        
        if print_log:
            self.print_results(result)
        
        return result
    
    def print_results(self, result):
        print("-" * 60)
        print("\n回测结果:")
        print("=" * 60)
        print(f"初始资金: {result['initial_cash']:,.2f}")
        print(f"最终资金: {result['final_value']:,.2f}")
        print(f"总收益: {result['total_profit']:,.2f}")
        print(f"总收益率: {result['total_return']:.2%}")
        
        print(f"\n详细指标:")
        print("-" * 60)
        
        if result['sharpe_ratio'] is not None:
            print(f"夏普比率: {result['sharpe_ratio']:.2f}")
        else:
            print("夏普比率: N/A")
        
        if result['max_drawdown'] is not None:
            print(f"最大回撤: {result['max_drawdown']:.2%}")
        else:
            print("最大回撤: N/A")
        
        if result['annual_return'] is not None:
            print(f"年化收益率: {result['annual_return']:.2f}%")
        else:
            print("年化收益率: N/A")
        
        print(f"总交易次数: {result['total_trades']}")
        print(f"胜率: {result['win_rate']:.2%}")
        
        print("\n" + "=" * 60)
    
    def plot(self, style='candle'):
        if self.cerebro:
            self.cerebro.plot(style=style)
    
    def compare_strategies(self, data_file, strategies):
        results = {}
        
        for name, (strategy_class, params) in strategies.items():
            print(f"\n{'='*60}")
            print(f"测试策略: {name}")
            print(f"{'='*60}")
            
            self.setup(data_file, strategy_class, params)
            result = self.run(print_log=False)
            results[name] = result
            
            sharpe_str = f"{result['sharpe_ratio']:.2f}" if result['sharpe_ratio'] else "N/A"
            dd_str = f"{result['max_drawdown']:.2%}" if result['max_drawdown'] else "N/A"
            print(f"{name}: 收益率 {result['total_return']:.2%}, 夏普 {sharpe_str}, 最大回撤 {dd_str}")
        
        print("\n" + "="*60)
        print("策略比较结果")
        print("="*60)
        print(f"{'策略名称':<15} {'收益率':<10} {'夏普比率':<10} {'最大回撤':<10} {'胜率':<10}")
        print("-"*60)
        
        for name, result in results.items():
            sharpe_str = f"{result['sharpe_ratio']:.2f}" if result['sharpe_ratio'] else "N/A"
            dd_str = f"{result['max_drawdown']:.2%}" if result['max_drawdown'] else "N/A"
            wr_str = f"{result['win_rate']:.2%}"
            print(f"{name:<15} {result['total_return']:<10.2%} {sharpe_str:<10} {dd_str:<10} {wr_str:<10}")
        
        return results

