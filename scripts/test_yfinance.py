"""
使用yfinance获取A股数据
yfinance使用Yahoo Finance服务器，全球可访问

A股股票代码格式：
- 上海：600000.SS（浦发银行）
- 深圳：000001.SZ（平安银行）
"""

import yfinance as yf
import pandas as pd
import os

def test_yfinance():
    """测试yfinance是否可用"""
    
    print("="*60)
    print("测试yfinance数据获取")
    print("="*60)
    
    # 平安银行 A股代码：000001.SZ
    symbol = "000001.SZ"
    
    print(f"\n正在获取 {symbol} 的数据...")
    
    try:
        # 获取最近1年数据
        stock = yf.Ticker(symbol)
        df = stock.history(period="1y")
        
        if df is not None and not df.empty:
            print(f"\n获取成功！共 {len(df)} 条数据")
            print("\n数据预览:")
            print(df[['Open', 'High', 'Low', 'Close', 'Volume']].head())
            
            # 保存数据
            os.makedirs('data/cache', exist_ok=True)
            df.to_csv('data/cache/000001_yfinance.csv', encoding='utf-8-sig')
            print("\n数据已保存到: data/cache/000001_yfinance.csv")
            
            return True
        else:
            print("获取数据为空")
            return False
            
    except Exception as e:
        print(f"获取数据失败: {e}")
        return False

if __name__ == '__main__':
    test_yfinance()
