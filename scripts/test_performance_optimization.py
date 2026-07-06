"""
性能优化测试
测试缓存、并行计算、内存优化

使用方法：
    python scripts/test_performance_optimization.py
"""

import sys
import os
import pandas as pd
import numpy as np
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_data_loading_performance():
    """测试数据加载性能"""
    print("=== 数据加载性能测试 ===")
    
    data_dir = 'data/all_stocks'
    if not os.path.exists(data_dir):
        print("数据目录不存在")
        return
    
    # 测试单文件加载
    files = os.listdir(data_dir)[:10]
    
    start_time = time.time()
    for f in files:
        filepath = os.path.join(data_dir, f)
        df = pd.read_csv(filepath, index_col='date', parse_dates=True)
    single_time = time.time() - start_time
    
    print(f"单文件加载（10个）: {single_time:.3f}秒")
    print(f"平均每文件: {single_time/10:.3f}秒")
    
    # 测试批量加载
    start_time = time.time()
    dataframes = []
    for f in files:
        filepath = os.path.join(data_dir, f)
        df = pd.read_csv(filepath, index_col='date', parse_dates=True)
        dataframes.append(df)
    batch_time = time.time() - start_time
    
    print(f"批量加载（10个）: {batch_time:.3f}秒")
    
    return single_time, batch_time


def test_indicator_calculation_performance():
    """测试指标计算性能"""
    print("\n=== 指标计算性能测试 ===")
    
    # 创建测试数据
    np.random.seed(42)
    prices = pd.Series(np.cumsum(np.random.randn(1000)) + 100)
    
    # 测试RSI计算
    start_time = time.time()
    for _ in range(100):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
    rsi_time = time.time() - start_time
    
    print(f"RSI计算（100次）: {rsi_time:.3f}秒")
    print(f"平均每次: {rsi_time/100:.4f}秒")
    
    # 测试MACD计算
    start_time = time.time()
    for _ in range(100):
        ema12 = prices.ewm(span=12).mean()
        ema26 = prices.ewm(span=26).mean()
        dif = ema12 - ema26
        dea = dif.ewm(span=9).mean()
        macd = 2 * (dif - dea)
    macd_time = time.time() - start_time
    
    print(f"MACD计算（100次）: {macd_time:.3f}秒")
    print(f"平均每次: {macd_time/100:.4f}秒")
    
    # 测试均线计算
    start_time = time.time()
    for _ in range(100):
        ma5 = prices.rolling(5).mean()
        ma10 = prices.rolling(10).mean()
        ma20 = prices.rolling(20).mean()
    ma_time = time.time() - start_time
    
    print(f"均线计算（100次）: {ma_time:.3f}秒")
    print(f"平均每次: {ma_time/100:.4f}秒")
    
    return rsi_time, macd_time, ma_time


def test_memory_usage():
    """测试内存使用"""
    print("\n=== 内存使用测试 ===")
    
    import sys
    
    # 创建大数据集
    df = pd.DataFrame({
        'open': np.random.randn(10000),
        'high': np.random.randn(10000),
        'low': np.random.randn(10000),
        'close': np.random.randn(10000),
        'volume': np.random.randint(1000, 10000, 10000)
    })
    
    # 测量内存
    df_size = sys.getsizeof(df)
    print(f"DataFrame内存: {df_size/1024:.2f} KB")
    print(f"平均每行: {df_size/len(df):.2f} bytes")
    
    # 测试内存优化
    df_optimized = df.copy()
    df_optimized['volume'] = df_optimized['volume'].astype('int32')
    
    optimized_size = sys.getsizeof(df_optimized)
    print(f"优化后内存: {optimized_size/1024:.2f} KB")
    print(f"内存节省: {(df_size - optimized_size)/df_size*100:.1f}%")
    
    return df_size, optimized_size


def main():
    """主函数"""
    print("="*60)
    print("性能优化测试")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 运行性能测试
    test_data_loading_performance()
    test_indicator_calculation_performance()
    test_memory_usage()
    
    print("\n" + "="*60)
    print("性能优化测试完成！")
    print("="*60)


if __name__ == '__main__':
    main()
