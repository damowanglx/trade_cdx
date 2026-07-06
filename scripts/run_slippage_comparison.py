"""
全量股票滑点测试
对比有滑点和无滑点的回测结果

使用方法：
    python scripts/run_slippage_comparison.py
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


def backtest_single_stock(data_file, slippage_pct=0.0, initial_cash=200000):
    """回测单只股票"""
    try:
        df = pd.read_csv(data_file, index_col='date', parse_dates=True)
        if len(df) < 100:
            return None
        
        cerebro = bt.Cerebro()
        data = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data)
        cerebro.addstrategy(RSIStrategy)
        cerebro.broker.setcash(initial_cash)
        cerebro.broker.setcommission(commission=0.001)
        
        # 设置滑点
        if slippage_pct > 0:
            cerebro.broker.set_slippage_perc(slippage_pct)
        
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


def main():
    """主函数"""
    print("="*60)
    print("全量股票滑点对比测试")
    print("="*60)
    print()
    print("对比：无滑点 vs 滑点0.2%")
    print()
    
    data_dir = 'data/all_stocks'
    data_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    print(f"股票总数: {len(data_files)}")
    print()
    
    # 测试无滑点
    print("测试无滑点...")
    results_no_slippage = []
    for i, filename in enumerate(data_files):
        if i % 500 == 0:
            print(f"进度: {i}/{len(data_files)}")
        data_file = os.path.join(data_dir, filename)
        result = backtest_single_stock(data_file, slippage_pct=0.0)
        if result:
            results_no_slippage.append(result)
    
    # 测试有滑点
    print("\n测试滑点0.2%...")
    results_with_slippage = []
    for i, filename in enumerate(data_files):
        if i % 500 == 0:
            print(f"进度: {i}/{len(data_files)}")
        data_file = os.path.join(data_dir, filename)
        result = backtest_single_stock(data_file, slippage_pct=0.002)
        if result:
            results_with_slippage.append(result)
    
    # 计算统计
    df_no_slippage = pd.DataFrame(results_no_slippage)
    df_with_slippage = pd.DataFrame(results_with_slippage)
    
    # 打印结果
    print("\n" + "="*60)
    print("滑点对比结果")
    print("="*60)
    
    print(f"\n{'指标':<15} {'无滑点':<15} {'滑点0.2%':<15} {'差异':<15}")
    print("-"*60)
    
    avg_return_no = df_no_slippage['total_return'].mean() * 100
    avg_return_with = df_with_slippage['total_return'].mean() * 100
    diff_return = avg_return_no - avg_return_with
    
    win_rate_no = len(df_no_slippage[df_no_slippage['total_return'] > 0]) / len(df_no_slippage) * 100
    win_rate_with = len(df_with_slippage[df_with_slippage['total_return'] > 0]) / len(df_with_slippage) * 100
    diff_win_rate = win_rate_no - win_rate_with
    
    print(f"{'平均收益率':<15} {avg_return_no:.2f}%{'':<8} {avg_return_with:.2f}%{'':<8} -{diff_return:.2f}%")
    print(f"{'盈利比例':<15} {win_rate_no:.1f}%{'':<9} {win_rate_with:.1f}%{'':<9} -{diff_win_rate:.1f}%")
    
    print(f"\n结论：滑点0.2%导致收益下降约{diff_return:.2f}%")
    print("="*60)
    
    # 保存结果
    os.makedirs('reports', exist_ok=True)
    df_no_slippage.to_csv('reports/slippage_no.csv', index=False, encoding='utf-8-sig')
    df_with_slippage.to_csv('reports/slippage_with.csv', index=False, encoding='utf-8-sig')
    print(f"\n结果已保存到 reports/ 目录")


if __name__ == '__main__':
    main()
