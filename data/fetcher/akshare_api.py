"""
AKShare数据获取模块
完全免费，无需注册，无需Token

AKShare文档：https://akshare.akfamily.xyz/
"""

import akshare as ak
import pandas as pd
import os


class AKShareFetcher:
    """AKShare数据获取类"""
    
    def __init__(self):
        """初始化"""
        print("AKShare数据获取器初始化完成（免费，无需Token）")
    
    def get_stock_daily(self, symbol, start_date, end_date):
        """
        获取股票日线数据
        
        Args:
            symbol: 股票代码，如 '000001'（平安银行）
            start_date: 开始日期，格式 '20250101'
            end_date: 结束日期，格式 '20260101'
        
        Returns:
            DataFrame: 日线数据
        """
        try:
            # AKShare获取日线数据
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",  # daily=日线, weekly=周线, monthly=月线
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"  # qfq=前复权, hfq=后复权, 空=不复权
            )
            
            if df is not None and not df.empty:
                # 重命名列（AKShare返回的列名是中文）
                df = df.rename(columns={
                    '日期': 'date',
                    '开盘': 'open',
                    '收盘': 'close',
                    '最高': 'high',
                    '最低': 'low',
                    '成交量': 'volume',
                    '成交额': 'amount',
                    '振幅': 'amplitude',
                    '涨跌幅': 'pct_change',
                    '涨跌额': 'change',
                    '换手率': 'turnover'
                })
                
                # 转换日期格式
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date')
                df = df.sort_index()
                
                print(f"获取 {symbol} 日线数据成功，共 {len(df)} 条")
                return df
            else:
                print(f"获取 {symbol} 日线数据为空")
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
            df = ak.stock_info_a_code_name()
            print(f"获取股票列表成功，共 {len(df)} 只股票")
            return df
        except Exception as e:
            print(f"获取股票列表失败: {e}")
            return pd.DataFrame()
    
    def get_stock_info(self, symbol):
        """
        获取股票基本信息
        
        Args:
            symbol: 股票代码
        
        Returns:
            dict: 股票信息
        """
        try:
            # 获取个股信息
            df = ak.stock_individual_info_em(symbol=symbol)
            if df is not None and not df.empty:
                info = dict(zip(df['item'], df['value']))
                print(f"获取 {symbol} 基本信息成功")
                return info
            return {}
        except Exception as e:
            print(f"获取股票信息失败: {e}")
            return {}
    
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


# 使用示例
if __name__ == '__main__':
    # 创建数据获取器
    fetcher = AKShareFetcher()
    
    # 获取平安银行(000001)最近1年数据
    symbol = '000001'
    start_date = '20250101'
    end_date = '20260101'
    
    print(f"\n{'='*50}")
    print(f"正在获取 {symbol} 的数据...")
    print(f"{'='*50}\n")
    
    # 获取日线数据
    daily_data = fetcher.get_stock_daily(symbol, start_date, end_date)
    if not daily_data.empty:
        print("\n日线数据预览:")
        print(daily_data[['open', 'high', 'low', 'close', 'volume']].head())
        
        # 保存到CSV
        fetcher.save_to_csv(daily_data, f'{symbol}_daily.csv')
    
    # 获取股票列表
    print("\n" + "="*50)
    print("正在获取股票列表...")
    stock_list = fetcher.get_stock_list()
    if not stock_list.empty:
        print("\n股票列表预览（前10只）:")
        print(stock_list.head(10))
        fetcher.save_to_csv(stock_list, 'stock_list.csv')

