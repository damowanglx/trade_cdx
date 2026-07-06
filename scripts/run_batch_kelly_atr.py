"""
全量股票回测 - 凯利公式+ATR仓位管理
"""

import os
import sys

import backtrader as bt
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class RSIStrategyWithKellyATR(bt.Strategy):
    """RSI策略 + 凯利公式 + ATR仓位管理"""
    
    params = (
        ('rsi_period', 21),
        ('rsi_oversold', 30),
        ('rsi_overbought', 70),
        ('stop_loss', 0.10),
        ('take_profit', 0.30),
        ('atr_period', 14),
        ('kelly_fraction', 0.5),
        ('max_position', 0.80),
        ('min_position', 0.20),
        ('printlog', False),
    )
    
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.rsi = bt.indicators.RSI(self.datas[0].close, period=self.params.rsi_period)
        self.atr = bt.indicators.ATR(self.datas[0], period=self.params.atr_period)
        self.order = None
        self.buy_price = 0
        self.trades = []
        self.win_count = 0
        self.loss_count = 0
        self.total_profit = 0
        self.total_loss = 0
    
    def calculate_kelly_fraction(self):
        """计算凯利公式仓位比例"""
        total_trades = self.win_count + self.loss_count
        if total_trades < 10:
            return 0.5
        
        win_rate = self.win_count / total_trades
        avg_win = self.total_profit / self.win_count if self.win_count > 0 else 0
        avg_loss = abs(self.total_loss / self.loss_count) if self.loss_count > 0 else 1
        win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 1
        
        kelly = (win_loss_ratio * win_rate - (1 - win_rate)) / win_loss_ratio
        kelly = kelly * self.params.kelly_fraction
        kelly = max(0, min(kelly, 0.8))
        
        return kelly
    
    def calculate_position_size(self):
        """计算仓位大小"""
        kelly_fraction = self.calculate_kelly_fraction()
        current_atr = self.atr[0]
        current_price = self.dataclose[0]
        atr_pct = current_atr / current_price
        
        atr_adjustment = 0.02 / atr_pct if atr_pct > 0 else 1
        atr_adjustment = max(0.5, min(atr_adjustment, 2.0))
        
        position_fraction = kelly_fraction * atr_adjustment
        position_fraction = max(self.params.min_position, 
                              min(position_fraction, self.params.max_position))
        
        cash = self.broker.getcash()
        size = int(cash * position_fraction / current_price / 100) * 100
        
        return size
    
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
                size = self.calculate_position_size()
                if size >= 100:
                    self.order = self.buy(size=size)
                    self.buy_price = current_price
    
    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buy_price = order.executed.price
        self.order = None
    
    def notify_trade(self, trade):
        if trade.isclosed:
            profit = trade.pnlcomm
            if profit > 0:
                self.win_count += 1
                self.total_profit += profit
            else:
                self.loss_count += 1
                self.total_loss += profit


def backtest_single_stock(data_file, initial_cash=200000):
    """回测单只股票"""
    try:
        df = pd.read_csv(data_file, index_col='date', parse_dates=True)
        if len(df) < 100:
            return None
        
        cerebro = bt.Cerebro()
        data = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data)
        cerebro.addstrategy(RSIStrategyWithKellyATR)
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
    print("全量回测 - 凯利公式+ATR仓位管理")
    print("="*60)
    print("止损: 10%")
    print("止盈: 30%")
    print("仓位管理: 凯利公式 + ATR动态调整")
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
    df_results.to_csv('reports/batch_kelly_atr.csv', index=False, encoding='utf-8-sig')
    
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
    
    print(f"\n结果已保存到: reports/batch_kelly_atr.csv")
    print("="*60)


if __name__ == '__main__':
    main()
