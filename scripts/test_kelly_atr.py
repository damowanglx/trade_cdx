"""
凯利公式+ATR动态仓位管理策略
结合胜率和波动率优化仓位

使用方法：
    python scripts/test_kelly_atr.py
"""

import sys
import os
import pandas as pd
import backtrader as bt
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class RSIStrategyWithKellyATR(bt.Strategy):
    """
    RSI策略 + 凯利公式 + ATR仓位管理
    
    仓位管理逻辑：
    1. 使用凯利公式计算基础仓位比例
    2. 使用ATR调整仓位（波动大时减仓，波动小时加仓）
    3. 最大仓位不超过80%，最小仓位不低于20%
    """
    
    params = (
        ('rsi_period', 21),
        ('rsi_oversold', 30),
        ('rsi_overbought', 70),
        ('stop_loss', 0.10),
        ('take_profit', 0.30),
        ('atr_period', 14),
        ('kelly_fraction', 0.5),  # 凯利公式的保守系数
        ('max_position', 0.80),   # 最大仓位80%
        ('min_position', 0.20),   # 最小仓位20%
        ('printlog', False),
    )
    
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.rsi = bt.indicators.RSI(self.datas[0].close, period=self.params.rsi_period)
        self.atr = bt.indicators.ATR(self.datas[0], period=self.params.atr_period)
        self.order = None
        self.buy_price = 0
        
        # 交易记录（用于计算凯利公式）
        self.trades = []
        self.win_count = 0
        self.loss_count = 0
        self.total_profit = 0
        self.total_loss = 0
    
    def calculate_kelly_fraction(self):
        """计算凯利公式仓位比例"""
        total_trades = self.win_count + self.loss_count
        
        # 至少需要10笔交易才使用凯利公式
        if total_trades < 10:
            return 0.5  # 默认50%
        
        # 计算胜率
        win_rate = self.win_count / total_trades
        
        # 计算盈亏比
        avg_win = self.total_profit / self.win_count if self.win_count > 0 else 0
        avg_loss = abs(self.total_loss / self.loss_count) if self.loss_count > 0 else 1
        
        win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 1
        
        # 凯利公式：f = (bp - q) / b
        # b = 盈亏比, p = 胜率, q = 败率
        kelly = (win_loss_ratio * win_rate - (1 - win_rate)) / win_loss_ratio
        
        # 应用保守系数
        kelly = kelly * self.params.kelly_fraction
        
        # 限制范围
        kelly = max(0, min(kelly, 0.8))
        
        return kelly
    
    def calculate_position_size(self):
        """计算仓位大小"""
        # 获取凯利公式仓位
        kelly_fraction = self.calculate_kelly_fraction()
        
        # 获取ATR
        current_atr = self.atr[0]
        current_price = self.dataclose[0]
        
        # 计算ATR百分比
        atr_pct = current_atr / current_price
        
        # ATR调整系数（波动越大，仓位越小）
        # 基准ATR百分比：2%
        atr_adjustment = 0.02 / atr_pct if atr_pct > 0 else 1
        atr_adjustment = max(0.5, min(atr_adjustment, 2.0))  # 限制在0.5-2倍
        
        # 最终仓位比例
        position_fraction = kelly_fraction * atr_adjustment
        
        # 限制范围
        position_fraction = max(self.params.min_position, 
                              min(position_fraction, self.params.max_position))
        
        # 计算可买数量
        cash = self.broker.getcash()
        size = int(cash * position_fraction / current_price / 100) * 100
        
        return size, position_fraction
    
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
                size, position_fraction = self.calculate_position_size()
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
            # 记录交易结果
            profit = trade.pnlcomm
            if profit > 0:
                self.win_count += 1
                self.total_profit += profit
            else:
                self.loss_count += 1
                self.total_loss += profit
            
            self.trades.append({
                'profit': profit,
                'is_win': profit > 0
            })


def run_backtest():
    """运行回测"""
    print("="*60)
    print("RSI策略 + 凯利公式 + ATR仓位管理")
    print("="*60)
    print()
    print("仓位管理逻辑：")
    print("  1. 凯利公式：根据胜率和盈亏比计算最优仓位")
    print("  2. ATR调整：波动大时减仓，波动小时加仓")
    print("  3. 仓位范围：20% - 80%")
    print()
    
    # 加载数据
    data_file = 'data/cache/000001_real_data.csv'
    if not os.path.exists(data_file):
        print(f"数据文件不存在: {data_file}")
        return
    
    df = pd.read_csv(data_file, index_col='date', parse_dates=True)
    
    # 创建引擎
    cerebro = bt.Cerebro()
    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)
    cerebro.addstrategy(RSIStrategyWithKellyATR)
    cerebro.broker.setcash(200000)
    cerebro.broker.setcommission(commission=0.001)
    
    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    
    # 运行回测
    print(f"初始资金: {200000:,.2f}")
    results = cerebro.run()
    strat = results[0]
    
    # 获取结果
    final_value = cerebro.broker.getvalue()
    total_return = (final_value - 200000) / 200000
    
    sharpe = strat.analyzers.sharpe.get_analysis()
    drawdown = strat.analyzers.drawdown.get_analysis()
    trades = strat.analyzers.trades.get_analysis()
    
    # 打印结果
    print("\n" + "="*60)
    print("回测结果")
    print("="*60)
    print(f"最终资金: {final_value:,.2f}")
    print(f"总收益: {final_value - 200000:,.2f}")
    print(f"总收益率: {total_return*100:.2f}%")
    
    sharpe_ratio = sharpe.get('sharperatio', None)
    print(f"夏普比率: {sharpe_ratio:.2f}" if sharpe_ratio else "夏普比率: N/A")
    print(f"最大回撤: {drawdown.get('max', {}).get('drawdown', 0):.2f}%")
    
    if 'total' in trades:
        total_trades = trades['total'].get('total', 0)
        won = trades.get('won', {}).get('total', 0)
        print(f"总交易次数: {total_trades}")
        print(f"盈利次数: {won}")
        print(f"胜率: {won/total_trades*100:.1f}%" if total_trades > 0 else "胜率: N/A")
    
    # 打印凯利公式计算结果
    print(f"\n凯利公式统计：")
    print(f"  胜率: {strat.win_count/(strat.win_count+strat.loss_count)*100:.1f}%" if (strat.win_count+strat.loss_count) > 0 else "  胜率: N/A")
    print(f"  盈利次数: {strat.win_count}")
    print(f"  亏损次数: {strat.loss_count}")
    print(f"  总盈利: {strat.total_profit:,.2f}")
    print(f"  总亏损: {strat.total_loss:,.2f}")
    
    print("="*60)
    
    return results


if __name__ == '__main__':
    run_backtest()
