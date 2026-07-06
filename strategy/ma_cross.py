"""
双均线交易策略 - 入门示例
最简单的量化交易策略，适合初学者理解

策略逻辑：
- 短期均线（5日）上穿长期均线（20日）→ 买入信号
- 短期均线（5日）下穿长期均线（20日）→ 卖出信号

学习目标：
1. 理解Backtrader框架
2. 学会编写交易策略
3. 学会进行回测
4. 理解回测结果指标
"""

import os
import sys

import backtrader as bt
import numpy as np
import pandas as pd

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class DualMAStrategy(bt.Strategy):
    """
    双均线策略
    
    参数说明：
    - fast_period: 短期均线周期，默认5
    - slow_period: 长期均线周期，默认20
    """
    
    # 策略参数
    params = (
        ('stop_loss', 0.10),      # 止损10%
        ('take_profit', 0.30),    # 止盈30%
        ('max_position', 0.30),   # 最大仓位30%
        (
        ('fast_period', 5),   # 短期均线周期
        ('slow_period', 20),  # 长期均线周期
        ('printlog', True),   # 是否打印日志
    )
    
    def __init__(self):
        """初始化策略"""
        # 保存收盘价引用
        self.dataclose = self.datas[0].close
        
        # 计算均线指标
        self.fast_ma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.fast_period
        )
        self.slow_ma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.slow_period
        )
        
        # 计算均线交叉信号
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)
        
        # 用于记录交易状态
        self.order = None
        self.buyprice = None
        self.buycomm = None
        
    def log(self, txt, dt=None):
        """日志记录函数"""
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt}: {txt}')
    
    def notify_order(self, order):
        """订单状态通知"""
        if order.status in [order.Submitted, order.Accepted]:
            # 订单已提交或已接受，等待执行
            return
        
        if order.status in [order.Completed]:
            # 订单已执行
            if order.isbuy():
                self.log(f'买入执行 - 价格: {order.executed.price:.2f}, '
                        f'数量: {order.executed.size}, '
                        f'手续费: {order.executed.comm:.2f}')
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(f'卖出执行 - 价格: {order.executed.price:.2f}, '
                        f'数量: {order.executed.size}, '
                        f'手续费: {order.executed.comm:.2f}')
            
            self.bar_executed = len(self)
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单取消/保证金不足/被拒绝')
        
        # 重置订单状态
        self.order = None
    
    def notify_trade(self, trade):
        """交易完成通知"""
        if not trade.isclosed:
            return
        
        self.log(f'交易利润 - 毛利润: {trade.pnl:.2f}, '
                f'净利润: {trade.pnlcomm:.2f}')
    
    def next(self):
        """策略核心逻辑 - 每个bar执行一次"""
        
        # 如果有未完成订单，不执行新订单
        if self.order:
            return
        
        # 检查是否持仓
        if not self.position:
            # 没有持仓，检查买入信号
            if self.crossover > 0:  # 金叉：短期均线上穿长期均线
                self.log(f'买入信号 - 收盘价: {self.dataclose[0]:.2f}')
                # 执行买入
                # 计算可买数量（使用90%资金，留10%现金）
                cash = self.broker.getcash()
                size = int(cash * 0.9 / self.dataclose[0] / 100) * 100  # 按手（100股）取整
                if size >= 100:
                    self.order = self.buy(size=size)
        else:
            # 有持仓，检查卖出信号
            if self.crossover < 0:  # 死叉：短期均线下穿长期均线
                self.log(f'卖出信号 - 收盘价: {self.dataclose[0]:.2f}')
                # 执行卖出
                self.order = self.sell()
    
    def stop(self):
        """策略结束时调用"""
        self.log(f'(均线周期: {self.params.fast_period}/{self.params.slow_period}) '
                f'最终资金: {self.broker.getvalue():.2f}')


def run_backtest(data_file, initial_cash=200000, commission=0.001, plot=True):
    """
    运行回测
    
    Args:
        data_file: 数据文件路径（CSV格式）
        initial_cash: 初始资金
        commission: 手续费率
        plot: 是否绘制图表
    
    Returns:
        dict: 回测结果
    """
    
    print("="*60)
    print("双均线策略回测")
    print("="*60)
    
    # 1. 创建回测引擎
    cerebro = bt.Cerebro()
    
    # 2. 加载数据
    print(f"\n加载数据: {data_file}")
    dataframe = pd.read_csv(data_file, index_col=0, parse_dates=True)
    
    # 确保数据包含必要的列
    required_cols = ['open', 'high', 'low', 'close', 'vol']
    for col in required_cols:
        if col not in dataframe.columns:
            print(f"错误: 数据缺少 {col} 列")
            return None
    
    # 转换为Backtrader数据格式
    data = bt.feeds.PandasData(dataname=dataframe)
    cerebro.adddata(data)
    
    # 3. 添加策略
    cerebro.addstrategy(DualMAStrategy)
    
    # 4. 设置初始资金
    cerebro.broker.setcash(initial_cash)
    
    # 5. 设置手续费
    cerebro.broker.setcommission(commission=commission)
    
    # 6. 添加分析器
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    
    # 7. 运行回测
    print(f"\n初始资金: {initial_cash:,.2f}")
    print("-"*60)
    
    results = cerebro.run()
    strat = results[0]
    
    # 8. 输出回测结果
    print("-"*60)
    final_value = cerebro.broker.getvalue()
    total_return = (final_value - initial_cash) / initial_cash * 100
    
    print(f"最终资金: {final_value:,.2f}")
    print(f"总收益: {final_value - initial_cash:,.2f}")
    print(f"总收益率: {total_return:.2f}%")
    
    # 输出分析器结果
    print("\n详细指标:")
    print("-"*60)
    
    sharpe = strat.analyzers.sharpe.get_analysis()
    drawdown = strat.analyzers.drawdown.get_analysis()
    returns = strat.analyzers.returns.get_analysis()
    trades = strat.analyzers.trades.get_analysis()
    
    print(f"夏普比率: {sharpe.get('sharperatio', 'N/A')}")
    print(f"最大回撤: {drawdown.get('max', {}).get('drawdown', 'N/A'):.2f}%")
    print(f"年化收益率: {returns.get('rnorm100', 'N/A'):.2f}%")
    
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
            print(f"胜率: {won/total_trades*100:.2f}%")
    
    # 9. 绘制图表
    if plot:
        print("\n正在绘制回测图表...")
        cerebro.plot(style='candle', volume=True)
    
    print("\n" + "="*60)
    print("回测完成！")
    print("="*60)
    
    return {
        'initial_cash': initial_cash,
        'final_value': final_value,
        'total_return': total_return,
        'sharpe_ratio': sharpe.get('sharperatio'),
        'max_drawdown': drawdown.get('max', {}).get('drawdown'),
        'annual_return': returns.get('rnorm100'),
    }


# 使用示例
if __name__ == '__main__':
    # 检查数据文件是否存在
    data_file = 'data/cache/000001.SZ_daily.csv'
    
    if not os.path.exists(data_file):
        print(f"数据文件不存在: {data_file}")
        print("请先运行: python scripts/01_data_analysis.py 获取数据")
    else:
        # 运行回测
        results = run_backtest(
            data_file=data_file,
            initial_cash=200000,  # 初始资金20万
            commission=0.001,     # 手续费千分之一
            plot=True             # 显示图表
        )
        
        if results:
            print("\n回测结果摘要:")
            print(f"  初始资金: {results['initial_cash']:,.2f}")
            print(f"  最终资金: {results['final_value']:,.2f}")
            print(f"  总收益率: {results['total_return']:.2f}%")
            print(f"  夏普比率: {results['sharpe_ratio']}")
            print(f"  最大回撤: {results['max_drawdown']:.2f}%")



