"""
全量策略回测测试（优化版）
抽样测试500只股票，5个策略

使用方法：
    python scripts/run_full_strategy_backtest_optimized.py
"""

import sys
import os
import pandas as pd
import backtrader as bt
import numpy as np
from datetime import datetime
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ========== 策略定义 ==========

class RSIStrategy(bt.Strategy):
    """RSI策略"""
    params = (('rsi_period', 21), ('rsi_oversold', 30), ('rsi_overbought', 70), 
              ('stop_loss', 0.10), ('take_profit', 0.30), ('printlog', False))
    
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
            if profit_pct <= -self.params.stop_loss or profit_pct >= self.params.take_profit:
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


class MACDStrategy(bt.Strategy):
    """MACD策略"""
    params = (('fast_period', 12), ('slow_period', 20), ('signal_period', 7),
              ('stop_loss', 0.10), ('take_profit', 0.30), ('printlog', False))
    
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.macd = bt.indicators.MACD(self.datas[0].close, period_me1=self.params.fast_period,
                                       period_me2=self.params.slow_period, period_signal=self.params.signal_period)
        self.crossover = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
        self.order = None
        self.buy_price = 0
        
    def next(self):
        if self.order:
            return
        current_price = self.dataclose[0]
        if self.position:
            profit_pct = (current_price - self.buy_price) / self.buy_price
            if profit_pct <= -self.params.stop_loss or profit_pct >= self.params.take_profit:
                self.order = self.sell()
                return
        else:
            if self.crossover > 0:
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


class MAStrategy(bt.Strategy):
    """均线策略"""
    params = (('fast_period', 5), ('slow_period', 20), ('stop_loss', 0.10), ('take_profit', 0.30), ('printlog', False))
    
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.fast_ma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.fast_period)
        self.slow_ma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.slow_period)
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)
        self.order = None
        self.buy_price = 0
        
    def next(self):
        if self.order:
            return
        current_price = self.dataclose[0]
        if self.position:
            profit_pct = (current_price - self.buy_price) / self.buy_price
            if profit_pct <= -self.params.stop_loss or profit_pct >= self.params.take_profit:
                self.order = self.sell()
                return
        else:
            if self.crossover > 0:
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


class BollingerStrategy(bt.Strategy):
    """布林带策略"""
    params = (('bb_period', 20), ('bb_std', 2.0), ('stop_loss', 0.10), ('take_profit', 0.30), ('printlog', False))
    
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.bb = bt.indicators.BollingerBands(self.dataclose, period=self.params.bb_period, devfactor=self.params.bb_std)
        self.order = None
        self.buy_price = 0
        
    def next(self):
        if self.order:
            return
        current_price = self.dataclose[0]
        if self.position:
            profit_pct = (current_price - self.buy_price) / self.buy_price
            if profit_pct <= -self.params.stop_loss or profit_pct >= self.params.take_profit:
                self.order = self.sell()
                return
            if current_price >= self.bb.lines.top[0]:
                self.order = self.sell()
                return
        else:
            if current_price <= self.bb.lines.bot[0]:
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


class TurtleStrategy(bt.Strategy):
    """海龟策略"""
    params = (('entry_period', 20), ('exit_period', 10), ('stop_loss', 0.10), ('printlog', False))
    
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.highest = bt.indicators.Highest(self.datas[0].high, period=self.params.entry_period)
        self.lowest = bt.indicators.Lowest(self.datas[0].low, period=self.params.exit_period)
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
            if current_price < self.lowest[0]:
                self.order = self.sell()
                return
        else:
            if current_price > self.highest[-1]:
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


# ========== 回测函数 ==========

def backtest_single_stock(data_file, strategy_class, initial_cash=100000):
    """回测单只股票"""
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
        cerebro.broker.set_slippage_perc(0.002)
        
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
            'final_value': final_value,
        }
    except:
        return None


def main():
    """主函数"""
    print("="*60)
    print("全量策略回测测试（抽样500只）")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 定义策略
    strategies = {
        'RSI策略': RSIStrategy,
        'MACD策略': MACDStrategy,
        '均线策略': MAStrategy,
        '布林带策略': BollingerStrategy,
        '海龟策略': TurtleStrategy,
    }
    
    # 获取数据文件并抽样
    data_dir = 'data/all_stocks'
    all_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    # 随机抽样500只
    random.seed(42)
    sample_files = random.sample(all_files, min(500, len(all_files)))
    
    print(f"总股票数: {len(all_files)}")
    print(f"抽样数量: {len(sample_files)}")
    print(f"策略数量: {len(strategies)}")
    print(f"初始资金: 100,000")
    print()
    
    # 测试每个策略
    all_results = {}
    
    for strategy_name, strategy_class in strategies.items():
        print(f"\n{'='*60}")
        print(f"测试策略: {strategy_name}")
        print(f"{'='*60}")
        
        results = []
        
        for i, filename in enumerate(sample_files):
            if i % 100 == 0:
                print(f"进度: {i}/{len(sample_files)} ({i/len(sample_files)*100:.1f}%)")
            
            data_file = os.path.join(data_dir, filename)
            result = backtest_single_stock(data_file, strategy_class)
            
            if result:
                result['symbol'] = filename.replace('.csv', '').replace('_', '.')
                results.append(result)
        
        df_results = pd.DataFrame(results)
        all_results[strategy_name] = df_results
        
        print(f"\n{strategy_name}结果:")
        print(f"  成功回测: {len(results)}只")
        print(f"  平均收益率: {df_results['total_return'].mean()*100:.2f}%")
        print(f"  盈利比例: {len(df_results[df_results['total_return'] > 0])/len(df_results)*100:.1f}%")
    
    # 打印比较结果
    print("\n" + "="*60)
    print("策略比较结果（抽样500只股票）")
    print("="*60)
    print(f"\n{'策略':<15} {'平均收益率':<12} {'盈利比例':<10} {'夏普比率':<10}")
    print("-"*50)
    
    for strategy_name, df in all_results.items():
        avg_return = df['total_return'].mean() * 100
        win_rate = len(df[df['total_return'] > 0]) / len(df) * 100
        valid_sharpe = df[df['sharpe_ratio'].notna()]
        avg_sharpe = valid_sharpe['sharpe_ratio'].mean() if len(valid_sharpe) > 0 else 0
        
        print(f"{strategy_name:<15} {avg_return:<12.2f} {win_rate:<10.1f} {avg_sharpe:<10.2f}")
    
    # 保存结果
    os.makedirs('reports', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 合并所有结果
    all_data = []
    for strategy_name, df in all_results.items():
        df['strategy'] = strategy_name
        all_data.append(df)
    
    combined_df = pd.concat(all_data)
    combined_df.to_csv(f'reports/full_strategy_backtest_{timestamp}.csv', index=False, encoding='utf-8-sig')
    
    print(f"\n结果已保存到: reports/full_strategy_backtest_{timestamp}.csv")
    print("="*60)


if __name__ == '__main__':
    main()
