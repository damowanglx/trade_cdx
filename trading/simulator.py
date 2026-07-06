"""
模拟交易系统
用于在模拟环境中测试策略

功能：
- 模拟交易执行
- 持仓管理
- 资金管理
- 交易记录
"""

import json
import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


class SimulatedBroker:
    """模拟券商"""
    
    def __init__(self, initial_cash=200000, commission_rate=0.001):
        """
        初始化模拟券商
        
        Args:
            initial_cash: 初始资金
            commission_rate: 手续费率
        """
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.commission_rate = commission_rate
        self.positions = {}  # {symbol: {'size': int, 'avg_price': float}}
        self.trades = []
        self.daily_values = []
        
    def get_cash(self):
        """获取现金"""
        return self.cash
    
    def get_position(self, symbol):
        """获取持仓"""
        return self.positions.get(symbol, {'size': 0, 'avg_price': 0})
    
    def get_portfolio_value(self, prices):
        """
        获取组合总价值
        
        Args:
            prices: dict，{symbol: current_price}
        """
        position_value = 0
        for symbol, pos in self.positions.items():
            if symbol in prices:
                position_value += pos['size'] * prices[symbol]
        
        return self.cash + position_value
    
    def buy(self, symbol, price, size):
        """
        买入
        
        Args:
            symbol: 股票代码
            price: 买入价格
            size: 买入数量（必须是100的倍数）
            
        Returns:
            bool: 是否成功
        """
        # 计算成本
        cost = price * size
        commission = cost * self.commission_rate
        total_cost = cost + commission
        
        # 检查资金
        if total_cost > self.cash:
            print(f"资金不足: 需要 {total_cost:.2f}, 可用 {self.cash:.2f}")
            return False
        
        # 执行买入
        self.cash -= total_cost
        
        if symbol in self.positions:
            # 更新持仓均价
            old_pos = self.positions[symbol]
            old_value = old_pos['size'] * old_pos['avg_price']
            new_value = old_value + cost
            new_size = old_pos['size'] + size
            self.positions[symbol] = {
                'size': new_size,
                'avg_price': new_value / new_size
            }
        else:
            self.positions[symbol] = {
                'size': size,
                'avg_price': price
            }
        
        # 记录交易
        trade = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'symbol': symbol,
            'action': 'buy',
            'price': price,
            'size': size,
            'cost': cost,
            'commission': commission,
            'cash_after': self.cash
        }
        self.trades.append(trade)
        
        print(f"买入 {symbol} {size}股 @ {price:.2f}, 成本 {total_cost:.2f}")
        return True
    
    def sell(self, symbol, price, size=None):
        """
        卖出
        
        Args:
            symbol: 股票代码
            price: 卖出价格
            size: 卖出数量（None表示全部卖出）
            
        Returns:
            bool: 是否成功
        """
        if symbol not in self.positions:
            print(f"没有持仓: {symbol}")
            return False
        
        pos = self.positions[symbol]
        
        if size is None:
            size = pos['size']
        
        if size > pos['size']:
            print(f"持仓不足: 持有 {pos['size']}, 卖出 {size}")
            return False
        
        # 计算收入
        revenue = price * size
        commission = revenue * self.commission_rate
        net_revenue = revenue - commission
        
        # 计算利润
        cost = pos['avg_price'] * size
        profit = net_revenue - cost
        
        # 执行卖出
        self.cash += net_revenue
        
        # 更新持仓
        if size == pos['size']:
            del self.positions[symbol]
        else:
            self.positions[symbol]['size'] -= size
        
        # 记录交易
        trade = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'symbol': symbol,
            'action': 'sell',
            'price': price,
            'size': size,
            'revenue': revenue,
            'commission': commission,
            'profit': profit,
            'cash_after': self.cash
        }
        self.trades.append(trade)
        
        print(f"卖出 {symbol} {size}股 @ {price:.2f}, 收入 {net_revenue:.2f}, 利润 {profit:.2f}")
        return True
    
    def get_trade_history(self):
        """获取交易历史"""
        return pd.DataFrame(self.trades)
    
    def get_summary(self):
        """获取账户摘要"""
        total_trades = len(self.trades)
        buy_trades = len([t for t in self.trades if t['action'] == 'buy'])
        sell_trades = len([t for t in self.trades if t['action'] == 'sell'])
        total_commission = sum(t.get('commission', 0) for t in self.trades)
        total_profit = sum(t.get('profit', 0) for t in self.trades if t['action'] == 'sell')
        
        return {
            'initial_cash': self.initial_cash,
            'current_cash': self.cash,
            'positions': self.positions,
            'total_trades': total_trades,
            'buy_trades': buy_trades,
            'sell_trades': sell_trades,
            'total_commission': total_commission,
            'total_profit': total_profit,
            'total_return': (self.cash - self.initial_cash) / self.initial_cash
        }


class SimulatedTrader:
    """模拟交易者"""
    
    def __init__(self, strategy, broker, symbol, data_file):
        """
        初始化
        
        Args:
            strategy: 策略实例
            broker: 模拟券商实例
            symbol: 交易标的
            data_file: 数据文件
        """
        self.strategy = strategy
        self.broker = broker
        self.symbol = symbol
        self.data = pd.read_csv(data_file, index_col='date', parse_dates=True)
        self.current_idx = 0
        
    def run(self, start_idx=0, end_idx=None):
        """
        运行模拟交易
        
        Args:
            start_idx: 起始索引
            end_idx: 结束索引
        """
        if end_idx is None:
            end_idx = len(self.data)
        
        print("="*60)
        print("开始模拟交易")
        print("="*60)
        print(f"标的: {self.symbol}")
        print(f"数据范围: {self.data.index[start_idx]} 到 {self.data.index[end_idx-1]}")
        print(f"初始资金: {self.broker.initial_cash:,.2f}")
        print()
        
        # 计算技术指标
        self.data['ma5'] = self.data['close'].rolling(5).mean()
        self.data['ma20'] = self.data['close'].rolling(20).mean()
        self.data['rsi'] = self._calculate_rsi(self.data['close'], 14)
        
        for i in range(start_idx, end_idx):
            self.current_idx = i
            current_data = self.data.iloc[i]
            current_price = current_data['close']
            
            # 获取持仓
            position = self.broker.get_position(self.symbol)
            
            # 策略信号
            signal = self._get_signal(i, position)
            
            # 执行交易
            if signal == 'buy' and position['size'] == 0:
                # 计算可买数量
                cash = self.broker.get_cash()
                size = int(cash * 0.9 / current_price / 100) * 100
                if size >= 100:
                    self.broker.buy(self.symbol, current_price, size)
            
            elif signal == 'sell' and position['size'] > 0:
                self.broker.sell(self.symbol, current_price)
            
            # 记录每日净值
            portfolio_value = self.broker.get_portfolio_value({self.symbol: current_price})
            self.broker.daily_values.append({
                'date': self.data.index[i],
                'value': portfolio_value
            })
        
        # 打印结果
        self._print_results()
    
    def _get_signal(self, idx, position):
        """获取交易信号"""
        if idx < 20:
            return None
        
        current = self.data.iloc[idx]
        prev = self.data.iloc[idx - 1]
        
        # 均线交叉信号
        ma5 = current['ma5']
        ma20 = current['ma20']
        prev_ma5 = prev['ma5']
        prev_ma20 = prev['ma20']
        
        if pd.isna(ma5) or pd.isna(ma20) or pd.isna(prev_ma5) or pd.isna(prev_ma20):
            return None
        
        # 金叉买入
        if prev_ma5 <= prev_ma20 and ma5 > ma20 and position['size'] == 0:
            return 'buy'
        
        # 死叉卖出
        if prev_ma5 >= prev_ma20 and ma5 < ma20 and position['size'] > 0:
            return 'sell'
        
        return None
    
    def _calculate_rsi(self, prices, period=14):
        """计算RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _print_results(self):
        """打印结果"""
        summary = self.broker.get_summary()
        
        print("\n" + "="*60)
        print("模拟交易结果")
        print("="*60)
        print(f"初始资金: {summary['initial_cash']:,.2f}")
        print(f"当前现金: {summary['current_cash']:,.2f}")
        print(f"总收益: {summary['total_profit']:,.2f}")
        print(f"总收益率: {summary['total_return']:.2%}")
        print(f"总交易次数: {summary['total_trades']}")
        print(f"手续费总额: {summary['total_commission']:.2f}")
        
        if summary['positions']:
            print(f"\n当前持仓:")
            for symbol, pos in summary['positions'].items():
                print(f"  {symbol}: {pos['size']}股 @ {pos['avg_price']:.2f}")
        
        print("="*60)
        
        # 保存交易记录
        trades_df = self.broker.get_trade_history()
        os.makedirs('logs', exist_ok=True)
        trades_file = f'logs/sim_trades_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        trades_df.to_csv(trades_file, index=False, encoding='utf-8-sig')
        print(f"\n交易记录已保存到: {trades_file}")
