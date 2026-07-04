"""
带滑点模拟的回测引擎
滑点：0.2%（买入加0.2%，卖出减0.2%）

使用方法：
    python scripts/test_slippage.py
"""

import sys
import os
import pandas as pd
import backtrader as bt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class RSIStrategyWithSlippage(bt.Strategy):
    """
    RSI策略 - 带滑点模拟
    
    滑点设置：
    - 买入滑点：+0.2%（实际买入价比预期高0.2%）
    - 卖出滑点：-0.2%（实际卖出价比预期低0.2%）
    """
    
    params = (
        ('rsi_period', 21),
        ('rsi_oversold', 30),
        ('rsi_overbought', 70),
        ('stop_loss', 0.10),
        ('take_profit', 0.30),
        ('slippage', 0.002),  # 滑点0.2%
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


def backtest_with_slippage(data_file, slippage_pct=0.002, initial_cash=200000):
    """带滑点的回测"""
    try:
        df = pd.read_csv(data_file, index_col='date', parse_dates=True)
        if len(df) < 100:
            return None
        
        cerebro = bt.Cerebro()
        data = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data)
        cerebro.addstrategy(RSIStrategyWithSlippage)
        cerebro.broker.setcash(initial_cash)
        cerebro.broker.setcommission(commission=0.001)
        
        # 设置滑点
        cerebro.broker.set_slippage_perc(slippage_pct)
        
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


def run_slippage_test():
    """运行滑点测试"""
    print("="*60)
    print("滑点模拟测试")
    print("="*60)
    print("滑点设置: 0.2%（买入+0.2%，卖出-0.2%）")
    print()
    
    # 测试不同滑点水平
    slippage_levels = [0.0, 0.001, 0.002, 0.003, 0.005]
    
    data_file = 'data/cache/000001_real_data.csv'
    if not os.path.exists(data_file):
        print(f"数据文件不存在: {data_file}")
        return
    
    print(f"测试股票: 平安银行(000001)")
    print()
    
    results = []
    
    for slippage in slippage_levels:
        result = backtest_with_slippage(data_file, slippage)
        if result:
            results.append({
                'slippage': slippage,
                'total_return': result['total_return'],
                'sharpe_ratio': result['sharpe_ratio'],
            })
    
    # 打印结果
    print(f"{'滑点':<10} {'收益率':<12} {'夏普比率':<10}")
    print("-"*35)
    
    for r in results:
        slippage_str = f"{r['slippage']*100:.1f}%"
        return_str = f"{r['total_return']*100:.2f}%"
        sharpe_str = f"{r['sharpe_ratio']:.2f}" if r['sharpe_ratio'] else "N/A"
        print(f"{slippage_str:<10} {return_str:<12} {sharpe_str:<10}")
    
    print()
    print("结论：滑点会降低收益，但更接近真实交易")
    print("="*60)


if __name__ == '__main__':
    run_slippage_test()
