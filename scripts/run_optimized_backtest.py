"""
用最优参数进行全量回测
测试RSI和MACD策略在所有股票上的表现

使用方法：
    python scripts/run_optimized_backtest.py
"""

import os
import sys

import backtrader as bt
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ========== RSI策略（最优参数） ==========
class RSIOptimized(bt.Strategy):
    params = (
        ('rsi_period', 21),
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


# ========== MACD策略（最优参数） ==========
class MACDOptimized(bt.Strategy):
    params = (
        ('fast_period', 12),
        ('slow_period', 20),
        ('signal_period', 7),
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


def backtest_single_stock(data_file, strategy_class, initial_cash=200000):
    """对单只股票进行回测"""
    try:
        df = pd.read_csv(data_file, index_col='date', parse_dates=True)
        if len(df) < 100:
            return None
        
        cerebro = bt.Cerebro()
        data = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data)
        cerebro.addstrategy(strategy_class)
        cerebro.broker.setcash(initial_cash)
        cerebro.broker.setcommission(commission=0.001)
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        
        results = cerebro.run()
        strat = results[0]
        
        final_value = cerebro.broker.getvalue()
        total_return = (final_value - initial_cash) / initial_cash
        sharpe = strat.analyzers.sharpe.get_analysis()
        returns = strat.analyzers.returns.get_analysis()
        trades = strat.analyzers.trades.get_analysis()
        
        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe.get('sharperatio', None),
            'annual_return': returns.get('rnorm100', None),
            'total_trades': trades.get('total', {}).get('total', 0),
        }
    except:
        return None


def main():
    """主函数"""
    print("="*60)
    print("最优参数全量回测")
    print("="*60)
    
    data_dir = 'data/all_stocks'
    data_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    strategies = {
        'RSI(最优)': RSIOptimized,
        'MACD(最优)': MACDOptimized,
    }
    
    print(f"\n股票总数: {len(data_files)}")
    print(f"策略数量: {len(strategies)}")
    print(f"预计时间: {len(data_files) * len(strategies) * 0.1 / 60:.0f} 分钟")
    print()
    
    all_results = {}
    
    for strategy_name, strategy_class in strategies.items():
        print(f"\n{'='*60}")
        print(f"测试策略: {strategy_name}")
        print(f"{'='*60}")
        
        results = []
        success_count = 0
        
        for i, filename in enumerate(data_files):
            if i % 500 == 0:
                print(f"进度: {i}/{len(data_files)} ({i/len(data_files)*100:.1f}%)")
            
            data_file = os.path.join(data_dir, filename)
            result = backtest_single_stock(data_file, strategy_class)
            
            if result:
                result['symbol'] = filename.replace('.csv', '').replace('_', '.')
                results.append(result)
                success_count += 1
        
        df_results = pd.DataFrame(results)
        all_results[strategy_name] = df_results
        
        # 保存单策略结果
        df_results.to_csv(f'reports/batch_{strategy_name}.csv', index=False, encoding='utf-8-sig')
        
        print(f"\n{strategy_name}策略结果:")
        print(f"  成功回测: {success_count} 只")
        print(f"  平均收益率: {df_results['total_return'].mean()*100:.2f}%")
        print(f"  盈利比例: {len(df_results[df_results['total_return'] > 0])/len(df_results)*100:.1f}%")
    
    # 打印比较结果
    print("\n" + "="*60)
    print("最优参数策略比较结果")
    print("="*60)
    print(f"\n{'策略':<15} {'平均收益率':<12} {'中位数收益率':<14} {'盈利比例':<10} {'夏普比率':<10}")
    print("-"*65)
    
    for strategy_name, df in all_results.items():
        avg_return = df['total_return'].mean() * 100
        median_return = df['total_return'].median() * 100
        win_rate = len(df[df['total_return'] > 0]) / len(df) * 100
        valid_sharpe = df[df['sharpe_ratio'].notna()]
        avg_sharpe = valid_sharpe['sharpe_ratio'].mean() if len(valid_sharpe) > 0 else 0
        
        print(f"{strategy_name:<15} {avg_return:<12.2f} {median_return:<14.2f} {win_rate:<10.1f} {avg_sharpe:<10.2f}")
    
    print("\n" + "="*60)
    print("全量回测完成！")
    print("="*60)


if __name__ == '__main__':
    main()
