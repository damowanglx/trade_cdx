"""
样本外测试验证
使用Walk-Forward方法验证策略泛化能力

数据分割：
- 训练集：2020-2023年（3年）
- 测试集：2024-2025年（2年）

使用方法：
    python scripts/run_walk_forward_test.py
"""

import sys
import os
import pandas as pd
import backtrader as bt

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


def backtest_with_params(df, params, initial_cash=200000):
    """使用指定参数回测"""
    try:
        cerebro = bt.Cerebro()
        data = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data)
        cerebro.addstrategy(RSIStrategy, **params)
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
        
        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe.get('sharperatio', None),
        }
    except:
        return None


def run_walk_forward_test():
    """运行Walk-Forward测试"""
    print("="*60)
    print("Walk-Forward 样本外测试")
    print("="*60)
    print()
    print("数据分割：")
    print("  训练集：2020-2023年（3年）")
    print("  测试集：2024-2025年（2年）")
    print()
    
    # 参数组合
    param_combinations = [
        {'rsi_period': 14, 'rsi_oversold': 25, 'rsi_overbought': 75},
        {'rsi_period': 14, 'rsi_oversold': 30, 'rsi_overbought': 70},
        {'rsi_period': 21, 'rsi_oversold': 25, 'rsi_overbought': 75},
        {'rsi_period': 21, 'rsi_oversold': 30, 'rsi_overbought': 70},
    ]
    
    # 获取数据文件
    data_dir = 'data/all_stocks'
    data_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    # 随机抽样50只股票
    import random
    random.seed(42)
    sample_files = random.sample(data_files, 50)
    
    print(f"抽样股票: {len(sample_files)} 只")
    print(f"参数组合: {len(param_combinations)} 种")
    print()
    
    # 存储结果
    train_results = []
    test_results = []
    
    for i, filename in enumerate(sample_files):
        if i % 10 == 0:
            print(f"进度: {i}/{len(sample_files)} ({i/len(sample_files)*100:.1f}%)")
        
        data_file = os.path.join(data_dir, filename)
        df = pd.read_csv(data_file, index_col='date', parse_dates=True)
        
        # 分割数据
        train_df = df[df.index < '2024-01-01']
        test_df = df[df.index >= '2024-01-01']
        
        if len(train_df) < 100 or len(test_df) < 50:
            continue
        
        # 测试每个参数组合
        for params in param_combinations:
            # 训练集回测
            train_result = backtest_with_params(train_df, params)
            if train_result:
                train_result['symbol'] = filename.replace('.csv', '')
                train_result['params'] = str(params)
                train_results.append(train_result)
            
            # 测试集回测
            test_result = backtest_with_params(test_df, params)
            if test_result:
                test_result['symbol'] = filename.replace('.csv', '')
                test_result['params'] = str(params)
                test_results.append(test_result)
    
    # 转换为DataFrame
    train_df = pd.DataFrame(train_results)
    test_df = pd.DataFrame(test_results)
    
    # 保存结果
    os.makedirs('reports', exist_ok=True)
    train_df.to_csv('reports/walk_forward_train.csv', index=False, encoding='utf-8-sig')
    test_df.to_csv('reports/walk_forward_test.csv', index=False, encoding='utf-8-sig')
    
    # 打印结果
    print("\n" + "="*60)
    print("Walk-Forward 测试结果")
    print("="*60)
    
    print(f"\n训练集（2020-2023）：")
    print(f"  样本数: {len(train_df)}")
    print(f"  平均收益率: {train_df['total_return'].mean()*100:.2f}%")
    print(f"  盈利比例: {len(train_df[train_df['total_return'] > 0])/len(train_df)*100:.1f}%")
    
    print(f"\n测试集（2024-2025）：")
    print(f"  样本数: {len(test_df)}")
    print(f"  平均收益率: {test_df['total_return'].mean()*100:.2f}%")
    print(f"  盈利比例: {len(test_df[test_df['total_return'] > 0])/len(test_df)*100:.1f}%")
    
    # 计算过拟合程度
    train_avg = train_df['total_return'].mean()
    test_avg = test_df['total_return'].mean()
    overfit_ratio = (train_avg - test_avg) / train_avg * 100 if train_avg > 0 else 0
    
    print(f"\n过拟合分析：")
    print(f"  训练集平均收益: {train_avg*100:.2f}%")
    print(f"  测试集平均收益: {test_avg*100:.2f}%")
    print(f"  收益衰减: {overfit_ratio:.1f}%")
    
    if overfit_ratio < 20:
        print(f"  评估: 过拟合程度较低，策略泛化能力较好")
    elif overfit_ratio < 40:
        print(f"  评估: 过拟合程度中等，建议进一步验证")
    else:
        print(f"  评估: 过拟合程度较高，策略可能不适合实盘")
    
    print(f"\n结果已保存到:")
    print(f"  - reports/walk_forward_train.csv")
    print(f"  - reports/walk_forward_test.csv")
    print("="*60)


if __name__ == '__main__':
    run_walk_forward_test()
