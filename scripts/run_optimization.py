"""
完整回测与优化脚本
整合数据获取、参数优化、回测、报告生成

使用方法：
    python scripts/run_optimization.py
"""

import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backtest.engine import BacktestEngine
from backtest.optimizer import ParameterOptimizer
from data.fetcher.baostock_api import BaostockFetcher
from strategy.ma_cross import DualMAStrategy
from strategy.macd_strategy import MACDStrategy
from strategy.rsi_strategy import RSIStrategy


def fetch_data():
    """获取真实数据"""
    print("="*60)
    print("获取股票数据")
    print("="*60)
    
    # 检查是否已有数据
    data_file = 'data/cache/000001_real_data.csv'
    if os.path.exists(data_file):
        print(f"使用已有数据: {data_file}")
        return data_file
    
    # 获取新数据
    fetcher = BaostockFetcher()
    symbol = 'sz.000001'
    start_date = '2024-01-01'
    end_date = '2026-01-01'
    
    print(f"获取 {symbol} 数据...")
    df = fetcher.get_stock_daily(symbol, start_date, end_date)
    
    if not df.empty:
        fetcher.save_to_csv(df, '000001_real_data.csv')
        fetcher.close()
        return data_file
    
    fetcher.close()
    return None


def optimize_ma_strategy(data_file):
    """优化双均线策略参数"""
    print("\n" + "="*60)
    print("优化双均线策略参数")
    print("="*60)
    
    optimizer = ParameterOptimizer(data_file, initial_cash=200000)
    
    # 定义参数网格
    param_grid = {
        'fast_period': [3, 5, 10, 15],
        'slow_period': [15, 20, 30, 40, 50]
    }
    
    # 运行优化
    results = optimizer.optimize(DualMAStrategy, param_grid)
    
    # 导出结果
    optimizer.export_results('reports/ma_optimization.csv')
    
    return optimizer.get_best_params()


def optimize_rsi_strategy(data_file):
    """优化RSI策略参数"""
    print("\n" + "="*60)
    print("优化RSI策略参数")
    print("="*60)
    
    optimizer = ParameterOptimizer(data_file, initial_cash=200000)
    
    # 定义参数网格
    param_grid = {
        'rsi_period': [7, 14, 21],
        'rsi_oversold': [20, 25, 30],
        'rsi_overbought': [70, 75, 80]
    }
    
    # 运行优化
    results = optimizer.optimize(RSIStrategy, param_grid)
    
    # 导出结果
    optimizer.export_results('reports/rsi_optimization.csv')
    
    return optimizer.get_best_params()


def optimize_macd_strategy(data_file):
    """优化MACD策略参数"""
    print("\n" + "="*60)
    print("优化MACD策略参数")
    print("="*60)
    
    optimizer = ParameterOptimizer(data_file, initial_cash=200000)
    
    # 定义参数网格
    param_grid = {
        'fast_period': [8, 12, 16],
        'slow_period': [20, 26, 30],
        'signal_period': [7, 9, 11]
    }
    
    # 运行优化
    results = optimizer.optimize(MACDStrategy, param_grid)
    
    # 导出结果
    optimizer.export_results('reports/macd_optimization.csv')
    
    return optimizer.get_best_params()


def run_best_strategy(data_file, best_params):
    """使用最优参数运行回测"""
    print("\n" + "="*60)
    print("使用最优参数运行回测")
    print("="*60)
    
    engine = BacktestEngine(initial_cash=200000, commission=0.001)
    
    # 选择最佳策略
    best_strategy = max(best_params.items(), 
                       key=lambda x: x[1].get('return', 0) if isinstance(x[1], dict) else 0)
    
    strategy_name = best_strategy[0]
    params = best_strategy[1]
    
    print(f"最佳策略: {strategy_name}")
    print(f"最优参数: {params}")
    
    # 运行回测
    if 'MA' in strategy_name:
        engine.setup(data_file, DualMAStrategy, params)
    elif 'RSI' in strategy_name:
        engine.setup(data_file, RSIStrategy, params)
    elif 'MACD' in strategy_name:
        engine.setup(data_file, MACDStrategy, params)
    
    result = engine.run()
    
    return result


def main():
    """主函数"""
    print("="*60)
    print("量化交易系统 - 参数优化与回测")
    print("="*60)
    
    # 创建报告目录
    os.makedirs('reports', exist_ok=True)
    
    # 1. 获取数据
    data_file = fetch_data()
    if not data_file:
        print("数据获取失败，退出")
        return
    
    # 2. 优化各策略参数
    best_ma_params = optimize_ma_strategy(data_file)
    best_rsi_params = optimize_rsi_strategy(data_file)
    best_macd_params = optimize_macd_strategy(data_file)
    
    # 3. 汇总最优参数
    print("\n" + "="*60)
    print("各策略最优参数汇总")
    print("="*60)
    
    best_params = {
        'MA': best_ma_params,
        'RSI': best_rsi_params,
        'MACD': best_macd_params
    }
    
    for name, params in best_params.items():
        print(f"{name}: {params}")
    
    # 4. 使用最优参数运行回测
    print("\n" + "="*60)
    print("使用最优参数运行回测")
    print("="*60)
    
    # 对每个策略使用最优参数运行回测
    for name, params in best_params.items():
        print(f"\n--- {name} 策略 ---")
        engine = BacktestEngine(initial_cash=200000, commission=0.001)
        
        if name == 'MA':
            engine.setup(data_file, DualMAStrategy, params)
        elif name == 'RSI':
            engine.setup(data_file, RSIStrategy, params)
        elif name == 'MACD':
            engine.setup(data_file, MACDStrategy, params)
        
        result = engine.run()
    
    print("\n" + "="*60)
    print("优化完成！")
    print("="*60)
    print("\n输出文件:")
    print("  - reports/ma_optimization.csv")
    print("  - reports/rsi_optimization.csv")
    print("  - reports/macd_optimization.csv")
    print("\n下一步:")
    print("  1. 查看优化结果CSV文件")
    print("  2. 使用最优参数进行模拟交易")
    print("  3. 准备实盘交易")


if __name__ == '__main__':
    main()
