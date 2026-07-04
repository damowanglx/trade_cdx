"""
快速参数优化
减少抽样数量，快速找到近似最优参数

使用方法：
    python scripts/run_quick_optimization.py
"""

import sys
import os
import pandas as pd
import backtrader as bt
import itertools
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ========== RSI策略 ==========
class RSIStrategy(bt.Strategy):
    params = (
        ('rsi_period', 14),
        ('rsi_oversold', 30),
        ('rsi_overbought', 70),
        ('printlog', False),
    )
    
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.rsi = bt.indicators.RSI(self.datas[0].close, period=self.params.rsi_period)
        self.order = None
        
    def next(self):
        if self.order:
            return
        if not self.position:
            if self.rsi[0] < self.params.rsi_oversold:
                cash = self.broker.getcash()
                size = int(cash * 0.9 / self.dataclose[0] / 100) * 100
                if size >= 100:
                    self.order = self.buy(size=size)
        else:
            if self.rsi[0] > self.params.rsi_overbought:
                self.order = self.sell()
    
    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin, order.Rejected]:
            self.order = None


# ========== MACD策略 ==========
class MACDStrategy(bt.Strategy):
    params = (
        ('fast_period', 12),
        ('slow_period', 26),
        ('signal_period', 9),
        ('printlog', False),
    )
    
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.macd = bt.indicators.MACD(
            self.datas[0].close,
            period_me1=self.params.fast_period,
            period_me2=self.params.slow_period,
            period_signal=self.params.signal_period
        )
        self.crossover = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
        self.order = None
        
    def next(self):
        if self.order:
            return
        if not self.position:
            if self.crossover > 0:
                cash = self.broker.getcash()
                size = int(cash * 0.9 / self.dataclose[0] / 100) * 100
                if size >= 100:
                    self.order = self.buy(size=size)
        else:
            if self.crossover < 0:
                self.order = self.sell()
    
    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin, order.Rejected]:
            self.order = None


def backtest_single_stock(data_file, strategy_class, params, initial_cash=200000):
    """对单只股票进行回测"""
    try:
        df = pd.read_csv(data_file, index_col='date', parse_dates=True)
        if len(df) < 100:
            return None
        
        cerebro = bt.Cerebro()
        data = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data)
        cerebro.addstrategy(strategy_class, **params)
        cerebro.broker.setcash(initial_cash)
        cerebro.broker.setcommission(commission=0.001)
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        
        results = cerebro.run()
        strat = results[0]
        
        final_value = cerebro.broker.getvalue()
        total_return = (final_value - initial_cash) / initial_cash
        sharpe = strat.analyzers.sharpe.get_analysis()
        
        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe.get('sharperatio', None),
        }
    except:
        return None


def optimize_strategy(strategy_class, param_grid, strategy_name, sample_size=20):
    """优化策略参数"""
    print(f"\n{'='*60}")
    print(f"优化策略: {strategy_name}")
    print(f"{'='*60}")
    
    # 获取数据文件
    data_dir = 'data/all_stocks'
    data_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    # 随机抽样
    random.seed(42)
    sample_files = random.sample(data_files, min(sample_size, len(data_files)))
    
    print(f"股票总数: {len(data_files)}")
    print(f"抽样数量: {len(sample_files)}")
    
    # 生成参数组合
    param_names = list(param_grid.keys())
    param_values = list(param_grid.values())
    param_combinations = list(itertools.product(*param_values))
    
    print(f"参数组合数: {len(param_combinations)}")
    print(f"预计时间: {len(param_combinations) * len(sample_files) * 0.1 / 60:.1f} 分钟")
    
    # 测试每个参数组合
    results = []
    
    for i, values in enumerate(param_combinations):
        params = dict(zip(param_names, values))
        
        if i % 5 == 0:
            print(f"进度: {i}/{len(param_combinations)} ({i/len(param_combinations)*100:.1f}%)")
        
        # 测试当前参数组合
        returns = []
        sharpes = []
        
        for filename in sample_files:
            data_file = os.path.join(data_dir, filename)
            result = backtest_single_stock(data_file, strategy_class, params)
            
            if result:
                returns.append(result['total_return'])
                if result['sharpe_ratio'] is not None:
                    sharpes.append(result['sharpe_ratio'])
        
        if returns:
            avg_return = sum(returns) / len(returns)
            avg_sharpe = sum(sharpes) / len(sharpes) if sharpes else 0
            win_rate = len([r for r in returns if r > 0]) / len(returns)
            
            results.append({
                'params': str(params),
                'avg_return': avg_return,
                'avg_sharpe': avg_sharpe,
                'win_rate': win_rate,
            })
    
    # 按平均收益率排序
    results.sort(key=lambda x: x['avg_return'], reverse=True)
    
    # 打印结果
    print(f"\n{'='*60}")
    print(f"{strategy_name}策略优化结果")
    print(f"{'='*60}")
    print(f"\n{'排名':<4} {'平均收益率':<12} {'夏普比率':<10} {'盈利比例':<10} {'参数'}")
    print("-"*80)
    
    for i, result in enumerate(results[:10]):
        print(f"{i+1:<4} {result['avg_return']*100:<12.2f} {result['avg_sharpe']:<10.2f} {result['win_rate']*100:<10.1f} {result['params']}")
    
    # 最优参数
    if results:
        best = results[0]
        print(f"\n{'='*60}")
        print(f"最优参数推荐")
        print(f"{'='*60}")
        print(f"参数: {best['params']}")
        print(f"平均收益率: {best['avg_return']*100:.2f}%")
        print(f"夏普比率: {best['avg_sharpe']:.2f}")
        print(f"盈利比例: {best['win_rate']*100:.1f}%")
    
    return results


def main():
    """主函数"""
    print("="*60)
    print("快速参数优化")
    print("="*60)
    
    # RSI策略参数网格
    rsi_param_grid = {
        'rsi_period': [7, 14, 21],
        'rsi_oversold': [20, 25, 30, 35],
        'rsi_overbought': [65, 70, 75, 80],
    }
    
    # MACD策略参数网格
    macd_param_grid = {
        'fast_period': [8, 12, 16],
        'slow_period': [20, 26, 30],
        'signal_period': [7, 9, 11],
    }
    
    # 优化RSI策略
    rsi_results = optimize_strategy(RSIStrategy, rsi_param_grid, 'RSI', sample_size=20)
    
    # 优化MACD策略
    macd_results = optimize_strategy(MACDStrategy, macd_param_grid, 'MACD', sample_size=20)
    
    # 保存结果
    os.makedirs('reports', exist_ok=True)
    
    rsi_df = pd.DataFrame(rsi_results)
    rsi_df.to_csv('reports/rsi_optimization_quick.csv', index=False, encoding='utf-8-sig')
    
    macd_df = pd.DataFrame(macd_results)
    macd_df.to_csv('reports/macd_optimization_quick.csv', index=False, encoding='utf-8-sig')
    
    print("\n" + "="*60)
    print("参数优化完成！")
    print("="*60)
    print(f"\n结果文件:")
    print(f"  - reports/rsi_optimization_quick.csv")
    print(f"  - reports/macd_optimization_quick.csv")


if __name__ == '__main__':
    main()

