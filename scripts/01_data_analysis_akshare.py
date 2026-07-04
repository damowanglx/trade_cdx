"""
第一个量化交易脚本 - 使用AKShare（免费，无需注册）
用于学习和理解量化交易的基础知识

使用方法：
    python scripts/01_data_analysis_akshare.py

学习目标：
1. 学会使用AKShare获取A股数据（完全免费）
2. 学会使用Pandas处理数据
3. 学会绘制K线图和均线
4. 理解基本的技术指标
"""

import sys
import os
import pandas as pd
import numpy as np

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.fetcher.akshare_api import AKShareFetcher
from data.fetcher.visualizer import Visualizer


def main():
    """主函数"""
    
    print("="*60)
    print("量化交易入门 - 数据获取与可视化（使用AKShare）")
    print("="*60)
    print("\n[OK] 使用AKShare：完全免费，无需注册，无需Token！")
    
    # 1. 创建数据获取器
    print("\n[步骤1] 初始化数据获取器...")
    fetcher = AKShareFetcher()
    
    # 2. 获取股票数据
    print("\n[步骤2] 获取平安银行(000001)最近1年数据...")
    symbol = '000001'  # 平安银行
    start_date = '20250101'
    end_date = '20260101'
    
    daily_data = fetcher.get_stock_daily(symbol, start_date, end_date)
    
    if daily_data.empty:
        print("获取数据失败，请检查网络连接")
        return
    
    # 3. 数据预览
    print("\n[步骤3] 数据预览:")
    print("-"*60)
    print(f"数据时间范围: {daily_data.index.min()} 到 {daily_data.index.max()}")
    print(f"数据条数: {len(daily_data)}")
    print("\n前5条数据:")
    print(daily_data[['open', 'high', 'low', 'close', 'volume']].head())
    
    # 4. 计算技术指标
    print("\n[步骤4] 计算技术指标...")
    
    # 计算均线
    daily_data['ma5'] = daily_data['close'].rolling(5).mean()
    daily_data['ma10'] = daily_data['close'].rolling(10).mean()
    daily_data['ma20'] = daily_data['close'].rolling(20).mean()
    daily_data['ma60'] = daily_data['close'].rolling(60).mean()
    
    # 计算收益率
    daily_data['return'] = daily_data['close'].pct_change()
    
    # 计算波动率（20日）
    daily_data['volatility'] = daily_data['return'].rolling(20).std() * np.sqrt(252)
    
    print("技术指标计算完成！")
    print("\n新增列: ma5, ma10, ma20, ma60, return, volatility")
    
    # 5. 基本统计信息
    print("\n[步骤5] 基本统计信息:")
    print("-"*60)
    print(f"最新价格: {daily_data['close'].iloc[-1]:.2f}")
    print(f"最高价格: {daily_data['high'].max():.2f}")
    print(f"最低价格: {daily_data['low'].min():.2f}")
    print(f"平均日收益率: {daily_data['return'].mean()*100:.4f}%")
    print(f"收益率标准差: {daily_data['return'].std()*100:.4f}%")
    print(f"年化波动率: {daily_data['volatility'].iloc[-1]*100:.2f}%")
    
    # 6. 保存数据
    print("\n[步骤6] 保存数据...")
    fetcher.save_to_csv(daily_data, f'{symbol}_daily_with_indicators.csv')
    
    # 7. 绘制图表
    print("\n[步骤7] 绘制K线图和均线...")
    viz = Visualizer()
    
    # 绘制带均线的K线图
    viz.plot_with_ma(
        daily_data, 
        ma_periods=[5, 20, 60],
        title=f'{symbol} 平安银行 K线图与均线',
        save_path='data/cache/kline_with_ma.png'
    )
    
    # 绘制收益率分布
    viz.plot_returns_distribution(
        daily_data['return'].dropna(),
        title=f'{symbol} 平安银行 日收益率分布',
        save_path='data/cache/returns_distribution.png'
    )
    
    print("\n" + "="*60)
    print("数据获取与分析完成！")
    print("="*60)
    print("\n生成的文件:")
    print("  - data/cache/000001_daily_with_indicators.csv (数据文件)")
    print("  - data/cache/kline_with_ma.png (K线图)")
    print("  - data/cache/returns_distribution.png (收益率分布图)")
    
    print("\n下一步学习:")
    print("  1. 查看生成的CSV文件，理解数据结构")
    print("  2. 查看生成的图表，理解K线和均线")
    print("  3. 尝试修改代码，获取其他股票的数据")
    print("  4. 学习下一节：策略回测")


if __name__ == '__main__':
    main()
