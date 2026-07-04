"""
并行回测脚本
使用multiprocessing加速回测

使用方法：
    python scripts/run_parallel_backtest.py
"""

import sys
import os
import pandas as pd
import backtrader as bt
from multiprocessing import Pool, cpu_count
from datetime import datetime

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


def backtest_single_stock(args):
    """回测单只股票（用于并行）"""
    data_file, initial_cash = args
    
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
        cerebro.broker.set_slippage_perc(0.002)
        
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        
        results = cerebro.run()
        strat = results[0]
        
        final_value = cerebro.broker.getvalue()
        total_return = (final_value - initial_cash) / initial_cash
        sharpe = strat.analyzers.sharpe.get_analysis()
        
        return {
            'symbol': os.path.basename(data_file).replace('.csv', '').replace('_', '.'),
            'total_return': total_return,
            'sharpe_ratio': sharpe.get('sharperatio', None),
            'final_value': final_value,
        }
    except:
        return None


def main():
    """主函数"""
    print("="*60)
    print("并行回测 - 多进程加速")
    print("="*60)
    
    # 获取CPU核心数
    num_cores = cpu_count()
    print(f"CPU核心数: {num_cores}")
    print(f"使用进程数: {num_cores}")
    print()
    
    # 获取数据文件
    data_dir = 'data/all_stocks'
    data_files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    print(f"股票总数: {len(data_files)}")
    print(f"初始资金: 100,000")
    print()
    
    # 准备参数
    initial_cash = 100000
    args_list = [(f, initial_cash) for f in data_files]
    
    # 并行回测
    print("开始并行回测...")
    start_time = datetime.now()
    
    with Pool(processes=num_cores) as pool:
        results = pool.map(backtest_single_stock, args_list)
    
    end_time = datetime.now()
    elapsed = (end_time - start_time).total_seconds()
    
    # 过滤无效结果
    results = [r for r in results if r is not None]
    
    # 转换为DataFrame
    df_results = pd.DataFrame(results)
    
    # 保存结果
    os.makedirs('reports', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    df_results.to_csv(f'reports/parallel_backtest_{timestamp}.csv', index=False, encoding='utf-8-sig')
    
    # 打印统计
    print("\n" + "="*60)
    print("并行回测结果")
    print("="*60)
    print(f"成功回测: {len(results)} 只")
    print(f"耗时: {elapsed:.1f} 秒")
    print(f"平均每只: {elapsed/len(results)*1000:.1f} 毫秒")
    print()
    
    print(f"=== 收益率统计 ===")
    print(f"平均收益率: {df_results['total_return'].mean()*100:.2f}%")
    print(f"盈利比例: {len(df_results[df_results['total_return'] > 0])/len(df_results)*100:.1f}%")
    
    print(f"\n结果已保存到: reports/parallel_backtest_{timestamp}.csv")
    print("="*60)


if __name__ == '__main__':
    main()
