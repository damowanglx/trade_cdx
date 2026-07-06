"""
使用真实数据的完整回测脚本
整合所有模块：数据获取、策略、风控、监控

使用方法：
    python scripts/run_full_backtest.py
"""

import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backtest.engine import BacktestEngine
from data.fetcher.baostock_api import BaostockFetcher
from strategy.ma_cross import DualMAStrategy
from strategy.macd_strategy import MACDStrategy
from strategy.rsi_strategy import RSIStrategy


def fetch_real_data():
    """获取真实数据"""
    print("="*60)
    print("获取真实股票数据")
    print("="*60)
    
    fetcher = BaostockFetcher()
    
    # 获取平安银行数据
    symbol = 'sz.000001'
    start_date = '2024-01-01'
    end_date = '2026-01-01'
    
    print(f"\n获取 {symbol} 数据...")
    df = fetcher.get_stock_daily(symbol, start_date, end_date)
    
    if not df.empty:
        # 保存数据
        fetcher.save_to_csv(df, '000001_real_data.csv')
        print(f"数据获取成功，共 {len(df)} 条")
        return 'data/cache/000001_real_data.csv'
    else:
        print("数据获取失败，使用模拟数据")
        return 'data/cache/000001_daily.csv'
    
    fetcher.close()


def run_strategy_comparison(data_file):
    """运行策略比较"""
    print("\n" + "="*60)
    print("策略比较测试")
    print("="*60)
    
    engine = BacktestEngine(initial_cash=200000, commission=0.001)
    
    # 定义策略
    strategies = {
        '双均线策略': (DualMAStrategy, {'fast_period': 5, 'slow_period': 20}),
        'RSI策略': (RSIStrategy, {'rsi_period': 14, 'rsi_oversold': 30, 'rsi_overbought': 70}),
        'MACD策略': (MACDStrategy, {'fast_period': 12, 'slow_period': 26, 'signal_period': 9}),
    }
    
    # 比较策略
    results = engine.compare_strategies(data_file, strategies)
    
    return results


def run_single_strategy(data_file, strategy_name='MACD'):
    """运行单个策略详细回测"""
    print("\n" + "="*60)
    print(f"详细回测: {strategy_name}策略")
    print("="*60)
    
    engine = BacktestEngine(initial_cash=200000, commission=0.001)
    
    # 选择策略
    if strategy_name == 'MA':
        strategy_class = DualMAStrategy
        params = {'fast_period': 5, 'slow_period': 20, 'printlog': True}
    elif strategy_name == 'RSI':
        strategy_class = RSIStrategy
        params = {'rsi_period': 14, 'rsi_oversold': 30, 'rsi_overbought': 70, 'printlog': True}
    elif strategy_name == 'MACD':
        strategy_class = MACDStrategy
        params = {'fast_period': 12, 'slow_period': 26, 'signal_period': 9, 'printlog': True}
    else:
        print(f"未知策略: {strategy_name}")
        return None
    
    # 运行回测
    engine.setup(data_file, strategy_class, params)
    result = engine.run(print_log=True)
    
    return result


def main():
    """主函数"""
    print("="*60)
    print("量化交易系统 - 完整回测")
    print("="*60)
    
    # 1. 获取真实数据
    data_file = fetch_real_data()
    
    # 2. 运行策略比较
    comparison_results = run_strategy_comparison(data_file)
    
    # 3. 运行最佳策略的详细回测
    best_strategy = max(comparison_results.items(), 
                       key=lambda x: x[1]['total_return'] if x[1]['total_return'] else -999)
    
    print(f"\n最佳策略: {best_strategy[0]}")
    print(f"收益率: {best_strategy[1]['total_return']:.2%}")
    
    # 4. 运行最佳策略的详细回测
    if 'MA' in best_strategy[0]:
        run_single_strategy(data_file, 'MA')
    elif 'RSI' in best_strategy[0]:
        run_single_strategy(data_file, 'RSI')
    elif 'MACD' in best_strategy[0]:
        run_single_strategy(data_file, 'MACD')
    
    print("\n" + "="*60)
    print("回测完成！")
    print("="*60)
    print("\n下一步:")
    print("  1. 查看 logs/ 目录下的交易日志")
    print("  2. 优化策略参数")
    print("  3. 尝试多股票组合策略")
    print("  4. 准备模拟盘测试")


if __name__ == '__main__':
    main()
