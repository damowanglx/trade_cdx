"""
运行模拟交易

使用方法：
    python scripts/run_simulation.py
"""

import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.fetcher.baostock_api import BaostockFetcher
from trading.simulator import SimulatedBroker, SimulatedTrader


class SimpleMAStrategy:
    """简单均线策略"""
    
    def __init__(self, fast_period=5, slow_period=20):
        self.fast_period = fast_period
        self.slow_period = slow_period


def main():
    """主函数"""
    print("="*60)
    print("量化交易系统 - 模拟交易")
    print("="*60)
    
    # 1. 获取数据
    data_file = 'data/cache/000001_real_data.csv'
    if not os.path.exists(data_file):
        print("获取数据...")
        fetcher = BaostockFetcher()
        df = fetcher.get_stock_daily('sz.000001', '2024-01-01', '2026-01-01')
        fetcher.save_to_csv(df, '000001_real_data.csv')
        fetcher.close()
    
    # 2. 创建模拟券商
    broker = SimulatedBroker(initial_cash=200000, commission_rate=0.001)
    
    # 3. 创建策略
    strategy = SimpleMAStrategy(fast_period=5, slow_period=20)
    
    # 4. 创建模拟交易者
    trader = SimulatedTrader(
        strategy=strategy,
        broker=broker,
        symbol='000001',
        data_file=data_file
    )
    
    # 5. 运行模拟交易
    trader.run(start_idx=60)  # 跳过前60天，等待均线形成
    
    print("\n" + "="*60)
    print("模拟交易完成！")
    print("="*60)
    print("\n下一步:")
    print("  1. 查看 logs/ 目录下的交易记录")
    print("  2. 分析交易结果，优化策略")
    print("  3. 准备实盘交易")


if __name__ == '__main__':
    main()
