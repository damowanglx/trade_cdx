"""
全量股票综合测试脚本
测试所有股票，生成详细报告

使用方法：
    python scripts/run_full_stock_test.py
"""

import os
import sys
from datetime import datetime

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
        ('slippage', 0.002),
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


def backtest_single_stock(data_file, initial_cash=100000):
    """回测单只股票（10万资金）"""
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
        cerebro.broker.set_slippage_perc(0.002)  # 滑点0.2%
        
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        
        results = cerebro.run()
        strat = results[0]
        
        final_value = cerebro.broker.getvalue()
        total_return = (final_value - initial_cash) / initial_cash
        sharpe = strat.analyzers.sharpe.get_analysis()
        drawdown = strat.analyzers.drawdown.get_analysis()
        trades = strat.analyzers.trades.get_analysis()
        
        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe.get('sharperatio', None),
            'max_drawdown': drawdown.get('max', {}).get('drawdown', None),
            'total_trades': trades.get('total', {}).get('total', 0),
            'final_value': final_value,
        }
    except:
        return None


def main():
    """主函数"""
    print("="*60)
    print("全量股票综合测试")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"初始资金: 100,000")
    print(f"滑点: 0.2%")
    print(f"止损: 10%")
    print(f"止盈: 30%")
    print()
    
    data_dir = 'data/all_stocks'
    data_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    print(f"股票总数: {len(data_files)}")
    print()
    
    results = []
    success_count = 0
    
    for i, filename in enumerate(data_files):
        if i % 500 == 0:
            print(f"进度: {i}/{len(data_files)} ({i/len(data_files)*100:.1f}%)")
        
        data_file = os.path.join(data_dir, filename)
        result = backtest_single_stock(data_file, initial_cash=100000)
        
        if result:
            result['symbol'] = filename.replace('.csv', '').replace('_', '.')
            results.append(result)
            success_count += 1
    
    df_results = pd.DataFrame(results)
    
    # 保存结果
    os.makedirs('reports', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    df_results.to_csv(f'reports/full_test_{timestamp}.csv', index=False, encoding='utf-8-sig')
    
    # 打印统计
    print("\n" + "="*60)
    print("全量测试结果统计")
    print("="*60)
    print(f"成功回测: {success_count} 只")
    print(f"初始资金: 100,000")
    print()
    
    print(f"=== 收益率分布 ===")
    print(f"平均收益率: {df_results['total_return'].mean()*100:.2f}%")
    print(f"中位数收益率: {df_results['total_return'].median()*100:.2f}%")
    print(f"最高收益率: {df_results['total_return'].max()*100:.2f}%")
    print(f"最低收益率: {df_results['total_return'].min()*100:.2f}%")
    print(f"标准差: {df_results['total_return'].std()*100:.2f}%")
    
    print(f"\n=== 盈利统计 ===")
    profitable = df_results[df_results['total_return'] > 0]
    print(f"盈利股票: {len(profitable)} ({len(profitable)/len(df_results)*100:.1f}%)")
    print(f"亏损股票: {len(df_results) - len(profitable)} ({(len(df_results) - len(profitable))/len(df_results)*100:.1f}%)")
    
    print(f"\n=== 风险指标 ===")
    valid_sharpe = df_results[df_results['sharpe_ratio'].notna()]
    if len(valid_sharpe) > 0:
        print(f"平均夏普比率: {valid_sharpe['sharpe_ratio'].mean():.2f}")
    
    valid_dd = df_results[df_results['max_drawdown'].notna()]
    if len(valid_dd) > 0:
        print(f"平均最大回撤: {valid_dd['max_drawdown'].mean()*100:.2f}%")
    
    print(f"\n=== 收益率最高的10只股票 ===")
    top10 = df_results.nlargest(10, 'total_return')
    for _, row in top10.iterrows():
        print(f"{row['symbol']}: {row['total_return']*100:.2f}%")
    
    print(f"\n=== 收益率最低的10只股票 ===")
    bottom10 = df_results.nsmallest(10, 'total_return')
    for _, row in bottom10.iterrows():
        print(f"{row['symbol']}: {row['total_return']*100:.2f}%")
    
    print(f"\n结果已保存到: reports/full_test_{timestamp}.csv")
    print("="*60)


if __name__ == '__main__':
    main()
