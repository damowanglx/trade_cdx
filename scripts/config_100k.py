"""
10万资金实盘配置
配置适合10万资金的交易参数

使用方法：
    python scripts/config_100k.py
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_100k_config():
    """创建10万资金配置"""
    print("="*60)
    print("10万资金实盘配置")
    print("="*60)
    
    config_content = '''"""
10万资金实盘配置
"""

# ========== 资金配置 ==========
INITIAL_CAPITAL = 100000  # 初始资金10万

# ========== 策略参数 ==========
# RSI策略最优参数
RSI_CONFIG = {
    'rsi_period': 21,
    'rsi_oversold': 30,
    'rsi_overbought': 70,
    'stop_loss': 0.10,      # 止损10%
    'take_profit': 0.30,    # 止盈30%
}

# MACD策略最优参数
MACD_CONFIG = {
    'fast_period': 12,
    'slow_period': 20,
    'signal_period': 7,
    'stop_loss': 0.10,
    'take_profit': 0.30,
}

# ========== 仓位管理 ==========
POSITION_CONFIG = {
    'max_position': 0.30,      # 单只股票最大仓位30%（3万）
    'min_position': 0.10,      # 单只股票最小仓位10%（1万）
    'max_stocks': 5,           # 最多持有5只股票
    'min_stocks': 3,           # 最少持有3只股票
    'kelly_fraction': 0.5,     # 凯利公式保守系数
}

# ========== 风险控制 ==========
RISK_CONFIG = {
    'max_drawdown': 0.15,      # 最大回撤15%（1.5万）
    'daily_loss_limit': 0.03,  # 每日最大亏损3%（3000）
    'slippage': 0.002,         # 滑点0.2%
    'commission': 0.001,       # 手续费0.1%
}

# ========== 交易股票池 ==========
# 选择流动性好、市值大的蓝筹股
STOCK_POOL = [
    # 银行股
    'sz.000001',  # 平安银行
    'sh.600036',  # 招商银行
    'sh.601398',  # 工商银行
    
    # 白酒股
    'sh.600519',  # 贵州茅台
    'sz.000858',  # 五粮液
    
    # 科技股
    'sz.000725',  # 京东方A
    'sz.002415',  # 海康威视
    
    # 新能源
    'sz.300750',  # 宁德时代
    'sz.002594',  # 比亚迪
    
    # 医药
    'sh.600276',  # 恒瑞医药
]

# ========== 调仓配置 ==========
REBALANCE_CONFIG = {
    'rebalance_days': 20,      # 调仓周期20天
    'rebalance_time': '15:00', # 调仓时间（收盘前）
}

# ========== 监控配置 ==========
MONITOR_CONFIG = {
    'enable_email': True,      # 启用邮件报警
    'enable_wechat': False,    # 暂不启用微信
    'email_receiver': 'your_email@example.com',  # 接收邮箱
}

# ========== QMT配置 ==========
QMT_CONFIG = {
    'qmt_path': r'D:\\国金QMT\\国金证券QMT交易端',
    'strategy_file': 'qmt_strategy_rsi_complete.py',
}
'''
    
    os.makedirs('config', exist_ok=True)
    with open('config/trading_100k.py', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("配置文件已创建: config/trading_100k.py")
    print()
    print("配置概要:")
    print(f"  初始资金: 100,000")
    print(f"  单只股票最大仓位: 30% (30,000)")
    print(f"  最多持有股票: 5只")
    print(f"  最大回撤限制: 15% (15,000)")
    print(f"  止损: 10%")
    print(f"  止盈: 30%")
    print(f"  调仓周期: 20天")
    print()
    print("股票池:")
    print("  平安银行、招商银行、工商银行")
    print("  贵州茅台、五粮液")
    print("  京东方A、海康威视")
    print("  宁德时代、比亚迪")
    print("  恒瑞医药")
    
    return config_content


def create_100k_backtest_script():
    """创建10万资金回测脚本"""
    script_content = '''"""
10万资金全量回测
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
    
    print(f"\\n回测完成: {len(df_results)} 只股票")
    print(f"平均收益率: {df_results['total_return'].mean()*100:.2f}%")
    print(f"盈利比例: {len(df_results[df_results['total_return'] > 0])/len(df_results)*100:.1f}%")
    
    os.makedirs('reports', exist_ok=True)
    df_results.to_csv('reports/backtest_100k.csv', index=False, encoding='utf-8-sig')
    print(f"\\n结果已保存到: reports/backtest_100k.csv")


if __name__ == '__main__':
    main()
'''
    
    with open('scripts/run_100k_backtest.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("回测脚本已创建: scripts/run_100k_backtest.py")


if __name__ == '__main__':
    create_100k_config()
    print()
    create_100k_backtest_script()
    
    print("\n" + "="*60)
    print("配置完成！")
    print("="*60)
    print("\n下一步:")
    print("1. 修改 config/trading_100k.py 中的邮箱配置")
    print("2. 运行 python scripts/run_100k_backtest.py 进行回测")
    print("3. 在QMT中加载策略进行模拟盘测试")
