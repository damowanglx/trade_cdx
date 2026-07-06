"""
10万资金全量回测
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


def main():
    """主函数"""
    print("="*60)
    print("10万资金全量回测")
    print("="*60)
    
    data_dir = 'data/all_stocks'
    data_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    print(f"股票总数: {len(data_files)}")
    print(f"初始资金: 100,000")
    print()
    
    results = []
    
    for i, filename in enumerate(data_files):
        if i % 500 == 0:
            print(f"进度: {i}/{len(data_files)}")
        
        data_file = os.path.join(data_dir, filename)
        try:
            df = pd.read_csv(data_file, index_col='date', parse_dates=True)
            if len(df) < 100:
                continue
            
            cerebro = bt.Cerebro()
            data = bt.feeds.PandasData(dataname=df)
            cerebro.adddata(data)
            cerebro.addstrategy(RSIStrategy)
            cerebro.broker.setcash(100000)
            cerebro.broker.setcommission(commission=0.001)
            cerebro.broker.set_slippage_perc(0.002)
            
            cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
            cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
            
            result = cerebro.run()
            strat = result[0]
            
            final_value = cerebro.broker.getvalue()
            total_return = (final_value - 100000) / 100000
            sharpe = strat.analyzers.sharpe.get_analysis()
            
            results.append({
                'symbol': filename.replace('.csv', '').replace('_', '.'),
                'total_return': total_return,
                'sharpe_ratio': sharpe.get('sharperatio', None),
                'final_value': final_value,
            })
        except:
            continue
    
    df_results = pd.DataFrame(results)
    
    print(f"\n回测完成: {len(df_results)} 只股票")
    print(f"平均收益率: {df_results['total_return'].mean()*100:.2f}%")
    print(f"盈利比例: {len(df_results[df_results['total_return'] > 0])/len(df_results)*100:.1f}%")
    
    os.makedirs('reports', exist_ok=True)
    df_results.to_csv('reports/backtest_100k.csv', index=False, encoding='utf-8-sig')
    print(f"\n结果已保存到: reports/backtest_100k.csv")


if __name__ == '__main__':
    main()
