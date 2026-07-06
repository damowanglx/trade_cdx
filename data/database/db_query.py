"""
SQLite数据库查询模块
提供便捷的数据查询接口

使用方法：
    from data.database.db_query import StockDB
"""

import os
import sqlite3

import pandas as pd


class StockDB:
    """股票数据库查询类"""
    
    def __init__(self, db_path='data/database/stock_data.db'):
        """初始化数据库连接"""
        self.db_path = db_path
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"数据库文件不存在: {db_path}")
    
    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path, timeout=10)
    
    def get_stock_list(self):
        """获取股票列表"""
        conn = self.get_connection()
        df = pd.read_sql('SELECT * FROM stock_info', conn)
        conn.close()
        return df
    
    def get_daily_data(self, symbol, start_date=None, end_date=None):
        """获取日线数据"""
        conn = self.get_connection()
        
        query = 'SELECT * FROM daily_data WHERE symbol = ?'
        params = [symbol]
        
        if start_date:
            query += ' AND date >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND date <= ?'
            params.append(end_date)
        
        query += ' ORDER BY date'
        
        df = pd.read_sql(query, conn, params=params)
        conn.close()
        
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
        
        return df
    
    def get_multiple_stocks(self, symbols, start_date=None, end_date=None):
        """获取多只股票数据"""
        conn = self.get_connection()
        
        placeholders = ','.join(['?' for _ in symbols])
        query = f'SELECT * FROM daily_data WHERE symbol IN ({placeholders})'
        params = list(symbols)
        
        if start_date:
            query += ' AND date >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND date <= ?'
            params.append(end_date)
        
        query += ' ORDER BY symbol, date'
        
        df = pd.read_sql(query, conn, params=params)
        conn.close()
        
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        
        return df
    
    def get_latest_price(self, symbol):
        """获取最新价格"""
        conn = self.get_connection()
        
        query = '''
            SELECT * FROM daily_data 
            WHERE symbol = ? 
            ORDER BY date DESC 
            LIMIT 1
        '''
        
        df = pd.read_sql(query, conn, params=[symbol])
        conn.close()
        
        return df.iloc[0] if not df.empty else None
    
    def get_database_stats(self):
        """获取数据库统计信息"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # 股票数量
        cursor.execute('SELECT COUNT(*) FROM stock_info')
        stats['stock_count'] = cursor.fetchone()[0]
        
        # 数据行数
        cursor.execute('SELECT COUNT(*) FROM daily_data')
        stats['row_count'] = cursor.fetchone()[0]
        
        # 日期范围
        cursor.execute('SELECT MIN(date), MAX(date) FROM daily_data')
        date_range = cursor.fetchone()
        stats['min_date'] = date_range[0]
        stats['max_date'] = date_range[1]
        
        # 数据库大小
        stats['db_size_mb'] = os.path.getsize(self.db_path) / 1024 / 1024
        
        conn.close()
        
        return stats
    
    def query(self, sql, params=None):
        """执行自定义SQL查询"""
        conn = self.get_connection()
        df = pd.read_sql(sql, conn, params=params)
        conn.close()
        return df


# 使用示例
if __name__ == '__main__':
    db = StockDB()
    
    # 获取数据库统计
    stats = db.get_database_stats()
    print("数据库统计:")
    print(f"  股票数量: {stats['stock_count']}")
    print(f"  数据行数: {stats['row_count']:,}")
    print(f"  日期范围: {stats['min_date']} 到 {stats['max_date']}")
    print(f"  数据库大小: {stats['db_size_mb']:.2f} MB")
    
    # 获取平安银行数据
    df = db.get_daily_data('sz.000001', start_date='2024-01-01')
    print(f"\n平安银行数据: {len(df)} 条")
    print(df.tail())
