"""
量化交易入门 - 数据分析与可视化
使用模拟数据学习量化交易基础

使用方法：
    python scripts/learn_data_analysis.py

学习目标：
1. 理解股票数据结构（OHLCV）
2. 学会计算技术指标（均线、收益率）
3. 学会绘制K线图
4. 理解基本的量化概念
"""

import pandas as pd
import numpy as np
import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    """主函数"""
    
    print("="*60)
    print("量化交易入门 - 数据分析与可视化")
    print("="*60)
    
    # 1. 加载数据
    print("\n[步骤1] 加载股票数据...")
    data_file = 'data/cache/000001_daily.csv'
    
    if not os.path.exists(data_file):
        print(f"错误：数据文件不存在 - {data_file}")
        print("请先运行: python scripts/generate_sample_data.py")
        return
    
    df = pd.read_csv(data_file, index_col='date', parse_dates=True)
    print(f"加载成功！共 {len(df)} 条数据")
    
    # 2. 数据预览
    print("\n[步骤2] 数据预览（前10条）:")
    print("-"*60)
    print(df[['open', 'high', 'low', 'close', 'volume']].head(10))
    
    # 3. 理解数据结构
    print("\n[步骤3] 理解数据结构（OHLCV）:")
    print("-"*60)
    print("OHLCV是股票数据的基本格式：")
    print(f"  - Open（开盘价）: 当天第一笔交易的价格")
    print(f"  - High（最高价）: 当天最高的交易价格")
    print(f"  - Low（最低价）: 当天最低的交易价格")
    print(f"  - Close（收盘价）: 当天最后一笔交易的价格")
    print(f"  - Volume（成交量）: 当天交易的股票数量")
    
    print(f"\n当前数据统计:")
    print(f"  最新收盘价: {df['close'].iloc[-1]:.2f}")
    print(f"  历史最高价: {df['high'].max():.2f}")
    print(f"  历史最低价: {df['low'].min():.2f}")
    print(f"  平均成交量: {df['volume'].mean():,.0f}")
    
    # 4. 计算技术指标
    print("\n[步骤4] 计算技术指标...")
    print("-"*60)
    
    # 4.1 计算均线（Moving Average）
    print("计算均线（MA）...")
    df['ma5'] = df['close'].rolling(window=5).mean()   # 5日均线
    df['ma10'] = df['close'].rolling(window=10).mean() # 10日均线
    df['ma20'] = df['close'].rolling(window=20).mean() # 20日均线
    df['ma60'] = df['close'].rolling(window=60).mean() # 60日均线
    
    print("  - MA5（5日均线）: 最近5天的平均价格")
    print("  - MA10（10日均线）: 最近10天的平均价格")
    print("  - MA20（20日均线）: 最近20天的平均价格")
    print("  - MA60（60日均线）: 最近60天的平均价格")
    
    # 4.2 计算收益率
    print("\n计算收益率...")
    df['daily_return'] = df['close'].pct_change()  # 日收益率
    df['cumulative_return'] = (1 + df['daily_return']).cumprod() - 1  # 累计收益率
    
    print(f"  平均日收益率: {df['daily_return'].mean()*100:.4f}%")
    print(f"  收益率标准差: {df['daily_return'].std()*100:.4f}%")
    print(f"  累计收益率: {df['cumulative_return'].iloc[-1]*100:.2f}%")
    
    # 4.3 计算波动率
    print("\n计算波动率...")
    df['volatility'] = df['daily_return'].rolling(window=20).std() * np.sqrt(252)
    print(f"  年化波动率: {df['volatility'].iloc[-1]*100:.2f}%")
    
    # 5. 均线交叉信号
    print("\n[步骤5] 均线交叉信号（金叉/死叉）:")
    print("-"*60)
    print("均线交叉是经典的交易信号：")
    print("  - 金叉（Golden Cross）: 短期均线上穿长期均线 → 买入信号")
    print("  - 死叉（Death Cross）: 短期均线下穿长期均线 → 卖出信号")
    
    # 计算金叉死叉信号
    df['ma5_above_ma20'] = df['ma5'] > df['ma20']
    df['cross_signal'] = df['ma5_above_ma20'].astype(int).diff()
    
    # 统计信号
    golden_cross = (df['cross_signal'] == 1).sum()  # 金叉次数
    death_cross = (df['cross_signal'] == -1).sum()  # 死叉次数
    
    print(f"\n  金叉次数: {golden_cross} 次")
    print(f"  死叉次数: {death_cross} 次")
    
    # 6. 保存处理后的数据
    print("\n[步骤6] 保存处理后的数据...")
    output_file = 'data/cache/000001_with_indicators.csv'
    df.to_csv(output_file, encoding='utf-8-sig')
    print(f"数据已保存到: {output_file}")
    
    # 7. 显示最近数据
    print("\n[步骤7] 最近10天数据（含技术指标）:")
    print("-"*60)
    print(df[['close', 'ma5', 'ma20', 'daily_return', 'volatility']].tail(10))
    
    # 8. 学习总结
    print("\n" + "="*60)
    print("学习总结")
    print("="*60)
    print("\n你今天学到了：")
    print("  1. 股票数据结构（OHLCV）")
    print("  2. 均线的概念和计算（MA5, MA10, MA20, MA60）")
    print("  3. 收益率的计算（日收益率、累计收益率）")
    print("  4. 波动率的概念（年化波动率）")
    print("  5. 金叉死叉交易信号")
    
    print("\n下一步学习：")
    print("  1. 运行策略回测：python scripts/run_backtest.py")
    print("  2. 查看生成的CSV文件，理解数据变化")
    print("  3. 尝试修改均线参数，观察信号变化")
    
    print("\n" + "="*60)
    print("数据处理完成！")
    print("="*60)


if __name__ == '__main__':
    main()
