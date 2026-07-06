"""
极简参数优化
只测试几个关键参数组合，快速得出结论

使用方法：
    python scripts/run_simple_optimization.py
"""

import os
import random
import sys

import backtrader as bt
import pandas as pd

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


def backtest_stock(data_file, params):
    """回测单只股票"""
    try:
        df = pd.read_csv(data_file, index_col='date', parse_dates=True)
        if len(df) < 100:
            return None
        
        cerebro = bt.Cerebro()
        data = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data)
        cerebro.addstrategy(RSIStrategy, **params)
        cerebro.broker.setcash(200000)
        cerebro.broker.setcommission(commission=0.001)
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        
        results = cerebro.run()
        strat = results[0]
        
        final_value = cerebro.broker.getvalue()
        total_return = (final_value - 200000) / 200000
        sharpe = strat.analyzers.sharpe.get_analysis()
        
        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe.get('sharperatio', None),
        }
    except:
        return None


def main():
    """主函数"""
    print("="*60)
    print("极简参数优化 - RSI策略")
    print("="*60)
    
    # 获取数据文件
    data_dir = 'data/all_stocks'
    data_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    # 随机抽样10只股票
    random.seed(42)
    sample_files = random.sample(data_files, 10)
    
    print(f"抽样股票: {len(sample_files)} 只")
    
    # 只测试几个关键参数组合
    param_combinations = [
        {'rsi_period': 7, 'rsi_oversold': 25, 'rsi_overbought': 75},
        {'rsi_period': 7, 'rsi_oversold': 30, 'rsi_overbought': 70},
        {'rsi_period': 14, 'rsi_oversold': 25, 'rsi_overbought': 75},
        {'rsi_period': 14, 'rsi_oversold': 30, 'rsi_overbought': 70},
        {'rsi_period': 14, 'rsi_oversold': 35, 'rsi_overbought': 65},
        {'rsi_period': 21, 'rsi_oversold': 30, 'rsi_overbought': 70},
    ]
    
    print(f"参数组合: {len(param_combinations)} 种")
    print(f"预计时间: {len(param_combinations) * len(sample_files) * 0.1:.0f} 秒")
    print()
    
    # 测试每个参数组合
    results = []
    
    for i, params in enumerate(param_combinations):
        print(f"[{i+1}/{len(param_combinations)}] 测试参数: {params}")
        
        returns = []
        sharpes = []
        
        for filename in sample_files:
            data_file = os.path.join(data_dir, filename)
            result = backtest_stock(data_file, params)
            
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
            
            print(f"  -> 平均收益率: {avg_return*100:.2f}%, 夏普: {avg_sharpe:.2f}, 盈利: {win_rate*100:.1f}%")
    
    # 按平均收益率排序
    results.sort(key=lambda x: x['avg_return'], reverse=True)
    
    # 打印结果
    print(f"\n{'='*60}")
    print(f"RSI策略优化结果")
    print(f"{'='*60}")
    print(f"\n{'排名':<4} {'平均收益率':<12} {'夏普比率':<10} {'盈利比例':<10} {'参数'}")
    print("-"*80)
    
    for i, result in enumerate(results):
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
    
    # 保存结果
    os.makedirs('reports', exist_ok=True)
    df = pd.DataFrame(results)
    df.to_csv('reports/rsi_optimization_simple.csv', index=False, encoding='utf-8-sig')
    print(f"\n结果已保存到: reports/rsi_optimization_simple.csv")


if __name__ == '__main__':
    main()
