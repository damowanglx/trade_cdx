"""
数据更新机制模块
自动获取和更新股票数据

使用方法：
    from data.updater.data_updater import DataUpdater
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd


class DataUpdater:
    """数据更新器"""
    
    def __init__(self, data_dir: str = 'data/all_stocks',
                 cache_dir: str = 'data/cache'):
        """
        初始化数据更新器
        
        Args:
            data_dir: 数据目录
            cache_dir: 缓存目录
        """
        self.data_dir = data_dir
        self.cache_dir = cache_dir
        self.logger = logging.getLogger('data_updater')
        
        # 创建目录
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(cache_dir, exist_ok=True)
        
    def get_stock_list(self) -> List[str]:
        """
        获取股票列表
        
        Returns:
            List: 股票代码列表
        """
        try:
            import baostock as bs

            # 登录baostock
            lg = bs.login()
            if lg.error_code != '0':
                self.logger.error(f"Baostock登录失败: {lg.error_msg}")
                return []
                
            # 获取股票列表
            rs = bs.query_stock_basic()
            if rs.error_code != '0':
                self.logger.error(f"获取股票列表失败: {rs.error_msg}")
                bs.logout()
                return []
                
            data_list = []
            while (rs.error_code == '0') and rs.next():
                data_list.append(rs.get_row_data())
                
            df = pd.DataFrame(data_list, columns=rs.fields)
            
            # 只保留A股
            a_stocks = df[(df['type'] == '1') & (df['status'] == '1')]
            
            bs.logout()
            
            return a_stocks['code'].tolist()
            
        except Exception as e:
            self.logger.error(f"获取股票列表失败: {e}")
            return []
            
    def fetch_stock_data(self, symbol: str, 
                        start_date: str, 
                        end_date: str) -> Optional[pd.DataFrame]:
        """
        获取股票数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            DataFrame: 股票数据
        """
        try:
            import baostock as bs

            # 登录baostock
            lg = bs.login()
            if lg.error_code != '0':
                self.logger.error(f"Baostock登录失败: {lg.error_msg}")
                return None
                
            # 获取数据
            rs = bs.query_history_k_data_plus(
                symbol,
                "date,open,high,low,close,volume,amount",
                start_date=start_date,
                end_date=end_date,
                frequency="d",
                adjustflag="2"
            )
            
            if rs.error_code != '0':
                self.logger.error(f"获取数据失败: {rs.error_msg}")
                bs.logout()
                return None
                
            data_list = []
            while (rs.error_code == '0') and rs.next():
                data_list.append(rs.get_row_data())
                
            if not data_list:
                bs.logout()
                return None
                
            df = pd.DataFrame(data_list, columns=rs.fields)
            
            # 转换数据类型
            df['date'] = pd.to_datetime(df['date'])
            numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
            df = df.set_index('date')
            df = df.sort_index()
            
            bs.logout()
            
            return df
            
        except Exception as e:
            self.logger.error(f"获取数据失败 {symbol}: {e}")
            return None
            
    def update_stock_data(self, symbol: str, 
                         days_back: int = 30) -> bool:
        """
        更新股票数据
        
        Args:
            symbol: 股票代码
            days_back: 回溯天数
            
        Returns:
            bool: 是否成功
        """
        try:
            # 计算日期
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            # 获取数据
            df = self.fetch_stock_data(symbol, start_date, end_date)
            
            if df is None or df.empty:
                self.logger.warning(f"未获取到数据: {symbol}")
                return False
                
            # 保存数据
            filename = f"{symbol.replace('.', '_')}.csv"
            filepath = os.path.join(self.data_dir, filename)
            
            # 如果文件存在，合并数据
            if os.path.exists(filepath):
                existing_df = pd.read_csv(filepath, index_col='date', parse_dates=True)
                df = pd.concat([existing_df, df])
                df = df[~df.index.duplicated(keep='last')]
                df = df.sort_index()
                
            df.to_csv(filepath, encoding='utf-8-sig')
            
            self.logger.info(f"更新数据成功: {symbol}, {len(df)} 条")
            return True
            
        except Exception as e:
            self.logger.error(f"更新数据失败 {symbol}: {e}")
            return False
