"""
双均线策略回测
使用模拟数据学习回测方法

使用方法：
    python scripts/run_backtest_simple.py

学习目标：
1. 理解回测的基本概念
2. 学会使用Backtrader框架
3. 理解回测结果指标
"""

import sys
import os
import pandas as pd
import backtrader as bt

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class DualMAStrategy(bt.Strategy):
    """
    双均线策略
    
    逻辑：
    - 短期均线（5日）上穿长期均线（20日）→ 买入
    - 短期均线（5日）下穿长期均线（20日）→ 卖出
    """
    
    params = (
        ('fast_period', 5),   # 短期均线周期
        ('slow_period', 20),  # 长期均线周期
        ('printlog', True),   # 是否打印日志
    )
    
    def __init__(self):
        """初始化策略"""
        self.dataclose = self.datas[0].close
        
        # 计算均线
        self.fast_ma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.fast_period
        )
        self.slow_ma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.slow_period
        )
        
        # 计算交叉信号
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)
        
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.trade_count = 0
        
    def log(self, txt, dt=None):
        """日志记录"""
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt}: {txt}')
    
    def notify_order(self, order):
        """订单通知"""
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'买入 - 价格: {order.executed.price:.2f}, '
                        f'数量: {order.executed.size}, '
                        f'手续费: {order.executed.comm:.2f}')
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(f'卖出 - 价格: {order.executed.price:.2f}, '
                        f'数量: {order.executed.size}, '
                        f'手续费: {order.executed.comm:.2f}')
            
            self.bar_executed = len(self)
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单取消/保证金不足/被拒绝')
        
        self.order = None
    
    def notify_trade(self, trade):
        """交易通知"""
        if not trade.isclosed:
            return
        
        self.trade_count += 1
        self.log(f'交易利润 - 毛利润: {trade.pnl:.2f}, 净利润: {trade.pnlcomm:.2f}')
    
    def next(self):
        """策略核心逻辑"""
        
        if self.order:
            return
        
        if not self.position:
            # 没有持仓，检查买入信号
            if self.crossover > 0:  # 金叉
                self.log(f'买入信号 - 收盘价: {self.dataclose[0]:.2f}')
                self.order = self.buy()
        else:
            # 有持仓，检查卖出信号
            if self.crossover < 0:  # 死叉
                self.log(f'卖出信号 - 收盘价: {self.dataclose[0]:.2f}')
                self.order = self.sell()
    
    def stop(self):
        """策略结束"""
        self.log(f'(均线周期: {self.params.fast_period}/{self.params.slow_period}) '
                f'最终资金: {self.broker.getvalue():.2f}')


def run_backtest():
    """运行回测"""
    
    print("="*60)
    print("双均线策略回测")
    print("="*60)
    
    # 1. 加载数据
    print("\n[步骤1] 加载数据...")
    data_file = 'data/cache/000001_daily.csv'
    
    if not os.path.exists(data_file):
        print(f"错误：数据文件不存在 - {data_file}")
        return None
    
    dataframe = pd.read_csv(data_file, index_col='date', parse_dates=True)
    print(f"加载成功！共 {len(dataframe)} 条数据")
    
    # 2. 创建回测引擎
    print("\n[步骤2] 创建回测引擎...")
    cerebro = bt.Cerebro()
    
    # 3. 加载数据到引擎
    data = bt.feeds.PandasData(dataname=dataframe)
    cerebro.adddata(data)
    
    # 4. 添加策略
    print("\n[步骤3] 添加双均线策略...")
    print("策略参数：")
    print("  - 短期均线: 5日")
    print("  - 长期均线: 20日")
    print("  - 买入信号: 5日均线上穿20日均线（金叉）")
    print("  - 卖出信号: 5日均线下穿20日均线（死叉）")
    
    cerebro.addstrategy(DualMAStrategy)
    
    # 5. 设置初始资金
    initial_cash = 200000  # 20万
    cerebro.broker.setcash(initial_cash)
    print(f"\n[步骤4] 设置初始资金: {initial_cash:,.2f}")
    
    # 6. 设置手续费
    commission = 0.001  # 千分之一
    cerebro.broker.setcommission(commission=commission)
    print(f"[步骤5] 设置手续费率: {commission*100}%")
    
    # 7. 添加分析器
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    
    # 8. 运行回测
    print("\n[步骤6] 运行回测...")
    print("-"*60)
    
    results = cerebro.run()
    strat = results[0]
    
    # 9. 输出结果
    print("-"*60)
    final_value = cerebro.broker.getvalue()
    total_return = (final_value - initial_cash) / initial_cash * 100
    
    print(f"\n[回测结果]")
    print("="*60)
    print(f"初始资金: {initial_cash:,.2f}")
    print(f"最终资金: {final_value:,.2f}")
    print(f"总收益: {final_value - initial_cash:,.2f}")
    print(f"总收益率: {total_return:.2f}%")
    
    # 输出详细指标
    print(f"\n[详细指标]")
    print("-"*60)
    
    sharpe = strat.analyzers.sharpe.get_analysis()
    drawdown = strat.analyzers.drawdown.get_analysis()
    returns = strat.analyzers.returns.get_analysis()
    trades = strat.analyzers.trades.get_analysis()
    
    sharpe_ratio = sharpe.get('sharperatio', None)
    max_drawdown = drawdown.get('max', {}).get('drawdown', None)
    annual_return = returns.get('rnorm100', None)
    
    print(f"夏普比率: {sharpe_ratio:.2f}" if sharpe_ratio else "夏普比率: N/A")
    print(f"最大回撤: {max_drawdown:.2f}%" if max_drawdown else "最大回撤: N/A")
    print(f"年化收益率: {annual_return:.2f}%" if annual_return else "年化收益率: N/A")
    
    if 'total' in trades:
        total_trades = trades['total'].get('total', 0)
        print(f"总交易次数: {total_trades}")
        
        if 'won' in trades:
            won = trades['won'].get('total', 0)
            print(f"盈利交易: {won}")
        
        if 'lost' in trades:
            lost = trades['lost'].get('total', 0)
            print(f"亏损交易: {lost}")
        
        if total_trades > 0:
            win_rate = won / total_trades * 100
            print(f"胜率: {win_rate:.2f}%")
    
    # 10. 策略评价
    print(f"\n[策略评价]")
    print("-"*60)
    
    if total_return > 0:
        print("[OK] 策略有正收益")
    else:
        print("[!!] 策略收益为负，需要优化")
    
    if sharpe_ratio and sharpe_ratio > 1:
        print("[OK] 夏普比率良好 (>1)")
    elif sharpe_ratio and sharpe_ratio > 0:
        print("[!!] 夏普比率较低，风险调整收益一般")
    
    if max_drawdown and max_drawdown < 20:
        print("[OK] 最大回撤可控 (<20%)")
    elif max_drawdown:
        print("[!!] 最大回撤较大，需要注意风险")
    
    print("\n" + "="*60)
    print("回测完成！")
    print("="*60)
    
    print("\n下一步学习：")
    print("  1. 修改策略参数（如均线周期）")
    print("  2. 尝试其他策略（RSI、MACD等）")
    print("  3. 学习多股票组合策略")
    
    return results


if __name__ == '__main__':
    run_backtest()
