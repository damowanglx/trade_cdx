"""
生成模拟股票数据
用于学习量化交易基础，不依赖网络

生成的数据模拟真实股票走势，包含：
- 开盘价、最高价、最低价、收盘价
- 成交量
- 趋势、波动、随机性
"""

import os

import numpy as np
import pandas as pd


def generate_stock_data(symbol='000001', start_date='2025-01-01', periods=250, initial_price=10.0):
    """
    生成模拟股票数据
    
    Args:
        symbol: 股票代码
        start_date: 开始日期
        periods: 生成多少天的数据（250天≈1年交易日）
        initial_price: 初始价格
    
    Returns:
        DataFrame: 模拟的股票数据
    """
    
    np.random.seed(42)  # 固定随机种子，保证可重复
    
    # 生成日期序列（只包含交易日，跳过周末）
    dates = pd.date_range(start=start_date, periods=periods, freq='B')  # B=工作日
    
    # 生成价格数据
    # 使用几何布朗运动模拟股价
    # dS = mu * S * dt + sigma * S * dW
    
    mu = 0.0002  # 日均收益率（约5%年化）
    sigma = 0.02  # 日波动率（约30%年化）
    
    # 生成随机收益率
    returns = np.random.normal(mu, sigma, periods)
    
    # 添加一些趋势和周期性
    trend = np.sin(np.linspace(0, 4*np.pi, periods)) * 0.001  # 周期性趋势
    returns = returns + trend
    
    # 计算价格序列
    prices = initial_price * np.exp(np.cumsum(returns))
    
    # 生成OHLC数据
    data = []
    for i in range(periods):
        close = prices[i]
        
        # 生成开盘价（在收盘价附近波动）
        open_price = close * (1 + np.random.normal(0, 0.005))
        
        # 生成最高价和最低价
        high = max(open_price, close) * (1 + abs(np.random.normal(0, 0.008)))
        low = min(open_price, close) * (1 - abs(np.random.normal(0, 0.008)))
        
        # 生成成交量（与价格波动相关）
        base_volume = 1000000
        volatility = abs(returns[i]) / sigma
        volume = int(base_volume * (1 + volatility * 2) * (1 + np.random.normal(0, 0.3)))
        
        data.append({
            'date': dates[i],
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close, 2),
            'volume': volume
        })
    
    df = pd.DataFrame(data)
    df = df.set_index('date')
    
    print(f"生成 {symbol} 模拟数据成功，共 {len(df)} 条")
    print(f"时间范围: {df.index.min()} 到 {df.index.max()}")
    print(f"价格范围: {df['close'].min():.2f} - {df['close'].max():.2f}")
    
    return df


def save_data(df, filename, directory='data/cache'):
    """保存数据到CSV"""
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, filename)
    df.to_csv(filepath, encoding='utf-8-sig')
    print(f"数据已保存到: {filepath}")


if __name__ == '__main__':
    print("="*60)
    print("生成模拟股票数据")
    print("="*60)
    
    # 生成平安银行模拟数据
    df = generate_stock_data(
        symbol='000001',
        start_date='2025-01-01',
        periods=250,  # 约1年交易日
        initial_price=10.0  # 初始价格10元
    )
    
    # 保存数据
    save_data(df, '000001_daily.csv')
    
    print("\n数据预览:")
    print(df[['open', 'high', 'low', 'close', 'volume']].head(10))
    
    print("\n" + "="*60)
    print("模拟数据生成完成！")
    print("="*60)
    print("\n注意：这是模拟数据，用于学习量化交易基础")
    print("等网络恢复后，可以用真实数据替换")

