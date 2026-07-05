"""
多股票组合回测模块
支持行业轮动、风险平价、资金管理

使用方法：
    python scripts/run_portfolio_backtest.py
"""

import sys
import os
import pandas as pd
import backtrader as bt
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class PortfolioStrategy(bt.Strategy):
    """
    多股票组合策略
    
    特点：
    1. 风险平价仓位管理
    2. 行业轮动选股
    3. 动态再平衡
    4. 最大回撤控制
    """
    
    params = (
        ('rebalance_days', 20),       # 调仓周期
        ('max_drawdown', 0.15),       # 最大回撤限制
        ('max_position', 0.30),       # 单只股票最大仓位
        ('min_stocks', 3),            # 最少持有股票数
        ('max_stocks', 5),            # 最多持有股票数
        ('printlog', False),
    )
    
    def __init__(self):
        self.day_count = 0
        self.portfolio_values = []
        self.peak_value = 0
        
    def next(self):
        self.day_count += 1
        
        # 记录组合价值
        portfolio_value = self.broker.getvalue()
        self.portfolio_values.append(portfolio_value)
        
        # 更新峰值
        if portfolio_value > self.peak_value:
            self.peak_value = portfolio_value
        
        # 检查最大回撤
        current_drawdown = (self.peak_value - portfolio_value) / self.peak_value
        if current_drawdown > self.params.max_drawdown:
            self.close_all_positions()
            return
        
        # 到达调仓周期
        if self.day_count % self.params.rebalance_days == 0:
            self.rebalance()
    
    def close_all_positions(self):
        """清仓所有持仓"""
        for data in self.datas:
            position = self.getposition(data)
            if position.size > 0:
                self.close(data)
    
    def rebalance(self):
        """调仓逻辑"""
        # 计算每只股票的动量得分
        scores = {}
        for data in self.datas:
            symbol = data._name
            closes = data.close.get(size=60)
            
            if len(closes) < 60:
                continue
            
            # 计算动量得分
            returns_20d = (closes[-1] - closes[-20]) / closes[-20]
            daily_returns = np.diff(closes) / closes[:-1]
            volatility = np.std(daily_returns) * np.sqrt(252)
            
            score = returns_20d / volatility if volatility > 0 else 0
            scores[symbol] = {
                'score': score,
                'volatility': volatility,
                'data': data
            }
        
        if not scores:
            return
        
        # 按得分排序，选择前N只股票
        sorted_stocks = sorted(scores.items(), key=lambda x: x[1]['score'], reverse=True)
        selected_stocks = sorted_stocks[:self.params.max_stocks]
        
        # 计算风险平价权重
        weights = self.calculate_risk_parity_weights(selected_stocks)
        
        # 调整持仓
        self.adjust_positions(selected_stocks, weights)
    
    def calculate_risk_parity_weights(self, stocks):
        """计算风险平价权重"""
        if not stocks:
            return {}
        
        volatilities = {symbol: info['volatility'] for symbol, info in stocks}
        inv_vol = {symbol: 1/vol if vol > 0 else 0 for symbol, vol in volatilities.items()}
        total_inv_vol = sum(inv_vol.values())
        
        weights = {symbol: iv/total_inv_vol for symbol, iv in inv_vol.items()}
        
        # 限制单只股票最大仓位
        for symbol in weights:
            weights[symbol] = min(weights[symbol], self.params.max_position)
        
        # 重新归一化
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {symbol: w/total_weight for symbol, w in weights.items()}
        
        return weights
    
    def adjust_positions(self, selected_stocks, weights):
        """调整持仓"""
        portfolio_value = self.broker.getvalue()
        
        # 先卖出不在目标列表中的股票
        for data in self.datas:
            symbol = data._name
            position = self.getposition(data)
            
            if position.size > 0 and symbol not in weights:
                self.close(data)
        
        # 买入/调整目标股票
        for symbol, info in selected_stocks:
            if symbol not in weights:
                continue
            
            data = info['data']
            target_weight = weights[symbol]
            target_value = portfolio_value * target_weight
            current_price = data.close[0]
            
            # 计算目标数量
            target_quantity = int(target_value / current_price / 100) * 100
            
            current_position = self.getposition(data)
            current_quantity = current_position.size
            
            # 调整持仓
            if target_quantity > current_quantity:
                buy_quantity = target_quantity - current_quantity
                if buy_quantity >= 100:
                    self.buy(data, size=buy_quantity)
            elif target_quantity < current_quantity:
                sell_quantity = current_quantity - target_quantity
                if sell_quantity >= 100:
                    self.sell(data, size=sell_quantity)


def run_portfolio_backtest():
    """运行组合回测"""
    print("="*60)
    print("多股票组合策略回测")
    print("="*60)
    print("策略特点:")
    print("  - 风险平价仓位管理")
    print("  - 动量选股")
    print("  - 最大回撤控制15%")
    print("  - 调仓周期: 20天")
    print()
    
    # 获取数据文件
    data_dir = 'data/all_stocks'
    data_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    # 随机选择10只股票组成组合
    import random
    random.seed(42)
    selected_files = random.sample(data_files, 10)
    
    print(f"组合股票数: {len(selected_files)}")
    print("股票列表:")
    for f in selected_files:
        print(f"  - {f.replace('.csv', '').replace('_', '.')}")
    print()
    
    # 创建引擎
    cerebro = bt.Cerebro()
    
    # 添加数据
    for filename in selected_files:
        filepath = os.path.join(data_dir, filename)
        df = pd.read_csv(filepath, index_col='date', parse_dates=True)
        symbol = filename.replace('.csv', '').replace('_', '.')
        
        data = bt.feeds.PandasData(dataname=df, name=symbol)
        cerebro.adddata(data)
    
    # 添加策略
    cerebro.addstrategy(PortfolioStrategy)
    cerebro.broker.setcash(100000)  # 10万资金
    cerebro.broker.setcommission(commission=0.001)
    
    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    
    # 运行回测
    print(f"初始资金: {100000:,.2f}")
    results = cerebro.run()
    strat = results[0]
    
    # 获取结果
    final_value = cerebro.broker.getvalue()
    total_return = (final_value - 100000) / 100000
    
    sharpe = strat.analyzers.sharpe.get_analysis()
    drawdown = strat.analyzers.drawdown.get_analysis()
    
    # 打印结果
    print("\n" + "="*60)
    print("回测结果")
    print("="*60)
    print(f"最终资金: {final_value:,.2f}")
    print(f"总收益: {final_value - 100000:,.2f}")
    print(f"总收益率: {total_return*100:.2f}%")
    
    sharpe_ratio = sharpe.get('sharperatio', None)
    print(f"夏普比率: {sharpe_ratio:.2f}" if sharpe_ratio else "夏普比率: N/A")
    print(f"最大回撤: {drawdown.get('max', {}).get('drawdown', 0):.2f}%")
    
    print("="*60)
    
    return results


if __name__ == '__main__':
    run_portfolio_backtest()
