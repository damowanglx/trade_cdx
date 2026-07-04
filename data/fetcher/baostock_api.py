"""
Baostock数据获取模块
完全免费，无需注册，无需Token
基于TCP连接，更稳定

Baostock文档：http://baostock.com/baostock/index.php
"""

import baostock as bs
import pandas as pd
import os


class BaostockFetcher:
    """Baostock数据获取类"""
    
    def __init__(self):
        """初始化并登录"""
        # 登录baostock
        lg = bs.login()
        if lg.error_code == '0':
            print("Baostock登录成功（免费，无需Token）")
        else:
            print(f"Baostock登录失败: {lg.error_msg}")
    
    def get_stock_daily(self, symbol, start_date, end_date):
        """
        获取股票日线数据
        
        Args:
            symbol: 股票代码，如 'sh.600000'（浦发银行）或 'sz.000001'（平安银行）
                    sh=上海，sz=深圳
            start_date: 开始日期，格式 '2025-01-01'
            end_date: 结束日期，格式 '2026-01-01'
        
        Returns:
            DataFrame: 日线数据
        """
        try:
            # 获取日线数据
            rs = bs.query_history_k_data_plus(
                symbol,
                "date,open,high,low,close,volume,amount,turn,pctChg",
                start_date=start_date,
                end_date=end_date,
                frequency="d",  # d=日, w=周, m=月
                adjustflag="2"  # 1=后复权, 2=前复权, 3=不复权
            )
            
            if rs.error_code == '0':
                # 获取数据
                data_list = []
                while (rs.error_code == '0') & rs.next():
                    data_list.append(rs.get_row_data())
                
                if data_list:
                    df = pd.DataFrame(data_list, columns=rs.fields)
                    
                    # 转换数据类型
                    df['date'] = pd.to_datetime(df['date'])
                    numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount', 'turn', 'pctChg']
                    for col in numeric_cols:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    df = df.set_index('date')
                    df = df.sort_index()
                    
                    # 重命名列
                    df = df.rename(columns={
                        'volume': 'volume',
                        'amount': 'amount',
                        'turn': 'turnover',
                        'pctChg': 'pct_change'
                    })
                    
                    print(f"获取 {symbol} 日线数据成功，共 {len(df)} 条")
                    return df
                else:
                    print(f"获取 {symbol} 日线数据为空")
                    return pd.DataFrame()
            else:
                print(f"获取数据失败: {rs.error_msg}")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"获取日线数据失败: {e}")
            return pd.DataFrame()
    
    def get_stock_list(self):
        """
        获取A股股票列表
        
        Returns:
            DataFrame: 股票列表
        """
        try:
            rs = bs.query_stock_basic()
            if rs.error_code == '0':
                data_list = []
                while (rs.error_code == '0') & rs.next():
                    data_list.append(rs.get_row_data())
                
                df = pd.DataFrame(data_list, columns=rs.fields)
                # 只保留A股
                df = df[df['type'] == '1']  # 1=股票
                print(f"获取股票列表成功，共 {len(df)} 只股票")
                return df
            return pd.DataFrame()
        except Exception as e:
            print(f"获取股票列表失败: {e}")
            return pd.DataFrame()
    
    def save_to_csv(self, df, filename, directory='data/cache'):
        """
        保存数据到CSV文件
        
        Args:
            df: DataFrame数据
            filename: 文件名
            directory: 保存目录
        """
        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, filename)
        df.to_csv(filepath, encoding='utf-8-sig')
        print(f"数据已保存到: {filepath}")
    
    def close(self):
        """关闭连接"""
        bs.logout()
        print("Baostock连接已关闭")


# 使用示例
if __name__ == '__main__':
    # 创建数据获取器
    fetcher = BaostockFetcher()
    
    # 获取平安银行(sz.000001)最近1年数据
    symbol = 'sz.000001'  # 注意：baostock需要加前缀 sz=深圳, sh=上海
    start_date = '2025-01-01'
    end_date = '2026-01-01'
    
    print(f"\n{'='*50}")
    print(f"正在获取 {symbol} 的数据...")
    print(f"{'='*50}\n")
    
    # 获取日线数据
    daily_data = fetcher.get_stock_daily(symbol, start_date, end_date)
    if not daily_data.empty:
        print("\n日线数据预览:")
        print(daily_data[['open', 'high', 'low', 'close', 'volume']].head())
        
        # 保存到CSV
        fetcher.save_to_csv(daily_data, '000001_daily.csv')
    
    # 关闭连接
    fetcher.close()

