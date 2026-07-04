"""
全量股票回测 - 带止损止盈的RSI策略
止损：-10%
止盈：+30%

使用方法：
    python scripts/run_batch_risk_control.py
"""

import sys
import os
import pandas as pd
import backtrader as bt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class RSIStrategyWithRiskControl(bt.Strategy):
    """带止损止盈的RSI策略"""
    
    params = (
        ('rsi_period', 21),
        ('rsi_oversold', 30),
        ('rsi_overbought', 70),
        ('stop_loss', 0.10),      # 止损10%
        ('take_profit', 0.30),    # 止盈30%
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
        
        # 持仓检查：止损止盈
        if self.position:
            profit_pct = (current_price - self.buy_price) / self.buy_price
            
            # 止损
            if profit_pct <= -self.params.stop_loss:
                self.order = self.sell()
                return
            
            # 止盈
            if profit_pct >= self.params.take_profit:
                self.order = self.sell()
                return
            
            # RSI超买卖出
            if self.rsi[0] > self.params.rsi_overbought:
                self.order = self.sell()
                return
        
        # 空仓检查：买入信号
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


def backtest_single_stock(data_file, initial_cash=200000):
    """回测单只股票"""
    try:
        df = pd.read_csv(data_file, index_col='date', parse_dates=True)
        if len(df) < 100:
            return None
        
        cerebro = bt.Cerebro()
        data = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data)
        cerebro.addstrategy(RSIStrategyWithRiskControl)
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
    print("全量回测 - 带止损止盈的RSI策略")
    print("="*60)
    print("止损: 10%")
    print("止盈: 30%")
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
        result = backtest_single_stock(data_file)
        
        if result:
            result['symbol'] = filename.replace('.csv', '').replace('_', '.')
            results.append(result)
            success_count += 1
    
    df_results = pd.DataFrame(results)
    
    # 保存结果
    os.makedirs('reports', exist_ok=True)
    df_results.to_csv('reports/batch_rsi_risk_control.csv', index=False, encoding='utf-8-sig')
    
    # 打印统计
    print("\n" + "="*60)
    print("回测结果统计")
    print("="*60)
    print(f"成功回测: {success_count} 只")
    print(f"平均收益率: {df_results['total_return'].mean()*100:.2f}%")
    print(f"中位数收益率: {df_results['total_return'].median()*100:.2f}%")
    print(f"盈利比例: {len(df_results[df_results['total_return'] > 0])/len(df_results)*100:.1f}%")
    
    valid_sharpe = df_results[df_results['sharpe_ratio'].notna()]
    if len(valid_sharpe) > 0:
        print(f"平均夏普比率: {valid_sharpe['sharpe_ratio'].mean():.2f}")
    
    print(f"\n结果已保存到: reports/batch_rsi_risk_control.csv")
    print("="*60)


if __name__ == '__main__':
    main()
