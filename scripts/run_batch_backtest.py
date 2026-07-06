"""
全量股票回测
测试策略在所有股票上的表现

使用方法：
    python scripts/run_batch_backtest.py
"""

import os
import sys
from datetime import datetime

import backtrader as bt
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class DualMAStrategy(bt.Strategy):
    """双均线策略"""
    params = (
        ('fast_period', 5),
        ('slow_period', 20),
        ('printlog', False),
    )
    
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.fast_ma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.fast_period)
        self.slow_ma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.slow_period)
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)
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
        if order.status in [order.Completed]:
            self.order = None
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.order = None


def backtest_single_stock(data_file, initial_cash=200000):
    """对单只股票进行回测"""
    try:
        # 加载数据
        df = pd.read_csv(data_file, index_col='date', parse_dates=True)
        
        # 检查数据量
        if len(df) < 100:
            return None
        
        # 创建引擎
        cerebro = bt.Cerebro()
        data = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data)
        cerebro.addstrategy(DualMAStrategy)
        cerebro.broker.setcash(initial_cash)
        cerebro.broker.setcommission(commission=0.001)
        
        # 添加分析器
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        
        # 运行回测
        results = cerebro.run()
        strat = results[0]
        
        # 获取结果
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
            'final_value': final_value,
        }
    except Exception as e:
        return None


def main():
    """主函数"""
    print("="*60)
    print("全量股票回测 - 双均线策略")
    print("="*60)
    
    # 获取所有数据文件
    data_dir = 'data/all_stocks'
    data_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    print(f"\n股票总数: {len(data_files)}")
    print(f"预计时间: {len(data_files) * 0.1 / 60:.0f} 分钟")
    print()
    
    # 回测每只股票
    results = []
    success_count = 0
    fail_count = 0
    
    for i, filename in enumerate(data_files):
        if i % 100 == 0:
            print(f"进度: {i}/{len(data_files)} ({i/len(data_files)*100:.1f}%)")
        
        data_file = os.path.join(data_dir, filename)
        result = backtest_single_stock(data_file)
        
        if result:
            result['symbol'] = filename.replace('.csv', '').replace('_', '.')
            results.append(result)
            success_count += 1
        else:
            fail_count += 1
    
    # 转换为DataFrame
    df_results = pd.DataFrame(results)
    
    # 保存结果
    os.makedirs('reports', exist_ok=True)
    df_results.to_csv('reports/batch_backtest_results.csv', index=False, encoding='utf-8-sig')
    
    # 打印统计信息
    print("\n" + "="*60)
    print("回测结果统计")
    print("="*60)
    print(f"成功回测: {success_count} 只")
    print(f"失败: {fail_count} 只")
    
    print(f"\n=== 收益率分布 ===")
    print(f"平均收益率: {df_results['total_return'].mean()*100:.2f}%")
    print(f"中位数收益率: {df_results['total_return'].median()*100:.2f}%")
    print(f"最高收益率: {df_results['total_return'].max()*100:.2f}%")
    print(f"最低收益率: {df_results['total_return'].min()*100:.2f}%")
    print(f"标准差: {df_results['total_return'].std()*100:.2f}%")
    
    print(f"\n=== 盈利统计 ===")
    profitable = df_results[df_results['total_return'] > 0]
    print(f"盈利股票数: {len(profitable)} ({len(profitable)/len(df_results)*100:.1f}%)")
    print(f"亏损股票数: {len(df_results) - len(profitable)} ({(len(df_results) - len(profitable))/len(df_results)*100:.1f}%)")
    
    print(f"\n=== 夏普比率 ===")
    valid_sharpe = df_results[df_results['sharpe_ratio'].notna()]
    if len(valid_sharpe) > 0:
        print(f"平均夏普比率: {valid_sharpe['sharpe_ratio'].mean():.2f}")
    
    # 保存详细报告
    print(f"\n详细结果已保存到: reports/batch_backtest_results.csv")
    
    # 显示前10和后10
    print(f"\n=== 收益率最高的10只股票 ===")
    top10 = df_results.nlargest(10, 'total_return')
    for _, row in top10.iterrows():
        print(f"{row['symbol']}: {row['total_return']*100:.2f}%")
    
    print(f"\n=== 收益率最低的10只股票 ===")
    bottom10 = df_results.nsmallest(10, 'total_return')
    for _, row in bottom10.iterrows():
        print(f"{row['symbol']}: {row['total_return']*100:.2f}%")
    
    print("\n" + "="*60)
    print("全量回测完成！")
    print("="*60)


if __name__ == '__main__':
    main()
