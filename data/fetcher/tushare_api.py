"""
数据获取模块
用于获取A股行情、财务等数据
"""

import tushare as ts
import pandas as pd
import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import TUSHARE_TOKEN


class DataFetcher:
    """数据获取类"""
    
    def __init__(self, token=None):
        """
        初始化数据获取器
        
        Args:
            token: Tushare Pro API Token
        """
        self.token = token or TUSHARE_TOKEN
        ts.set_token(self.token)
        self.pro = ts.pro_api()
    
    def get_daily_data(self, ts_code, start_date, end_date):
        """
        获取日线数据
        
        Args:
            ts_code: 股票代码，如 '000001.SZ'
            start_date: 开始日期，格式 'YYYYMMDD'
            end_date: 结束日期，格式 'YYYYMMDD'
        
        Returns:
            DataFrame: 日线数据
        """
        try:
            df = self.pro.daily(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date
            )
            if df is not None and not df.empty:
                # 转换日期格式
                df['trade_date'] = pd.to_datetime(df['trade_date'])
                df = df.sort_values('trade_date')
                df = df.set_index('trade_date')
                print(f"获取 {ts_code} 日线数据成功，共 {len(df)} 条")
                return df
            else:
                print(f"获取 {ts_code} 日线数据为空")
                return pd.DataFrame()
        except Exception as e:
            print(f"获取日线数据失败: {e}")
            return pd.DataFrame()
    
    def get_stock_list(self):
        """
        获取股票列表
        
        Returns:
            DataFrame: 股票列表
        """
        try:
            df = self.pro.stock_basic(
                exchange='',
                list_status='L',
                fields='ts_code,symbol,name,area,industry,market,list_date'
            )
            print(f"获取股票列表成功，共 {len(df)} 只股票")
            return df
        except Exception as e:
            print(f"获取股票列表失败: {e}")
            return pd.DataFrame()
    
    def get_daily_basic(self, ts_code, start_date, end_date):
        """
        获取每日指标数据（市盈率、市净率等）
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            DataFrame: 每日指标数据
        """
        try:
            df = self.pro.daily_basic(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                fields='ts_code,trade_date,close,turnover_rate,pe_ttm,pb,ps_ttm,total_mv'
            )
            if df is not None and not df.empty:
                df['trade_date'] = pd.to_datetime(df['trade_date'])
                df = df.sort_values('trade_date')
                df = df.set_index('trade_date')
                print(f"获取 {ts_code} 每日指标成功，共 {len(df)} 条")
                return df
            return pd.DataFrame()
        except Exception as e:
            print(f"获取每日指标失败: {e}")
            return pd.DataFrame()
    
    def get_financial_data(self, ts_code, period):
        """
        获取财务数据
        
        Args:
            ts_code: 股票代码
            period: 报告期，如 '20241231'
        
        Returns:
            DataFrame: 财务数据
        """
        try:
            # 获取利润表
            income = self.pro.income(ts_code=ts_code, period=period)
            # 获取资产负债表
            balancesheet = self.pro.balancesheet(ts_code=ts_code, period=period)
            # 获取现金流量表
            cashflow = self.pro.cashflow(ts_code=ts_code, period=period)
            
            print(f"获取 {ts_code} {period} 财务数据成功")
            return {
                'income': income,
                'balancesheet': balancesheet,
                'cashflow': cashflow
            }
        except Exception as e:
            print(f"获取财务数据失败: {e}")
            return None
    
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
    
    def load_from_csv(self, filename, directory='data/cache'):
        """
        从CSV文件加载数据
        
        Args:
            filename: 文件名
            directory: 文件目录
        
        Returns:
            DataFrame: 加载的数据
        """
        filepath = os.path.join(directory, filename)
        if os.path.exists(filepath):
            df = pd.read_csv(filepath, index_col=0, parse_dates=True)
            print(f"从 {filepath} 加载数据成功，共 {len(df)} 条")
            return df
        else:
            print(f"文件 {filepath} 不存在")
            return pd.DataFrame()


# 使用示例
if __name__ == '__main__':
    # 创建数据获取器
    fetcher = DataFetcher()
    
    # 获取平安银行(000001.SZ)最近1年数据
    ts_code = '000001.SZ'
    start_date = '20250101'
    end_date = '20260101'
    
    print(f"\n{'='*50}")
    print(f"正在获取 {ts_code} 的数据...")
    print(f"{'='*50}\n")
    
    # 获取日线数据
    daily_data = fetcher.get_daily_data(ts_code, start_date, end_date)
    if not daily_data.empty:
        print("\n日线数据预览:")
        print(daily_data.head())
        
        # 保存到CSV
        fetcher.save_to_csv(daily_data, f'{ts_code}_daily.csv')
    
    # 获取股票列表
    print("\n" + "="*50)
    print("正在获取股票列表...")
    stock_list = fetcher.get_stock_list()
    if not stock_list.empty:
        print("\n股票列表预览:")
        print(stock_list.head(10))
        fetcher.save_to_csv(stock_list, 'stock_list.csv')

