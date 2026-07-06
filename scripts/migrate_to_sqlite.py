"""
SQLite数据库模块
将CSV数据迁移到SQLite数据库

使用方法：
    python scripts/migrate_to_sqlite.py
"""

import os
import sqlite3
import sys
from datetime import datetime

import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_database():
    """创建数据库和表"""
    print("创建数据库...")
    
    # 创建数据库目录
    os.makedirs('data/database', exist_ok=True)
    
    # 连接数据库
    db_path = 'data/database/stock_data.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建股票基本信息表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_info (
            symbol TEXT PRIMARY KEY,
            name TEXT,
            market TEXT,
            industry TEXT,
            list_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建日线数据表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume REAL,
            amount REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(symbol, date)
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_symbol ON daily_data(symbol)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_date ON daily_data(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_symbol_date ON daily_data(symbol, date)')
    
    # 创建回测结果表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS backtest_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy TEXT NOT NULL,
            symbol TEXT NOT NULL,
            total_return REAL,
            sharpe_ratio REAL,
            max_drawdown REAL,
            total_trades INTEGER,
            win_rate REAL,
            params TEXT,
            test_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    print(f"[OK] 数据库创建成功: {db_path}")
    
    return conn


def import_csv_to_sqlite(conn, csv_dir='data/all_stocks'):
    """导入CSV数据到SQLite"""
    print(f"\n导入CSV数据...")
    
    # 获取所有CSV文件
    csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
    print(f"找到 {len(csv_files)} 个CSV文件")
    
    cursor = conn.cursor()
    success_count = 0
    error_count = 0
    
    for i, filename in enumerate(csv_files):
        if i % 500 == 0:
            print(f"进度: {i}/{len(csv_files)} ({i/len(csv_files)*100:.1f}%)")
        
        try:
            # 读取CSV文件
            filepath = os.path.join(csv_dir, filename)
            df = pd.read_csv(filepath, index_col='date', parse_dates=True)
            
            # 提取股票代码
            symbol = filename.replace('.csv', '').replace('_', '.')
            
            # 准备数据
            records = []
            for date, row in df.iterrows():
                records.append((
                    symbol,
                    date.strftime('%Y-%m-%d'),
                    row.get('open', None),
                    row.get('high', None),
                    row.get('low', None),
                    row.get('close', None),
                    row.get('volume', None),
                    row.get('amount', None)
                ))
            
            # 批量插入
            cursor.executemany('''
                INSERT OR REPLACE INTO daily_data 
                (symbol, date, open, high, low, close, volume, amount)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', records)
            
            # 插入股票信息
            cursor.execute('''
                INSERT OR IGNORE INTO stock_info (symbol, market)
                VALUES (?, ?)
            ''', (symbol, symbol.split('.')[0]))
            
            success_count += 1
            
        except Exception as e:
            error_count += 1
            if error_count <= 5:  # 只打印前5个错误
                print(f"导入失败 {filename}: {e}")
    
    conn.commit()
    print(f"\n导入完成:")
    print(f"  成功: {success_count}")
    print(f"  失败: {error_count}")
    
    return success_count


def verify_database(conn):
    """验证数据库"""
    print(f"\n验证数据库...")
    
    cursor = conn.cursor()
    
    # 统计股票数量
    cursor.execute('SELECT COUNT(*) FROM stock_info')
    stock_count = cursor.fetchone()[0]
    
    # 统计数据行数
    cursor.execute('SELECT COUNT(*) FROM daily_data')
    row_count = cursor.fetchone()[0]
    
    # 统计日期范围
    cursor.execute('SELECT MIN(date), MAX(date) FROM daily_data')
    date_range = cursor.fetchone()
    
    # 获取数据库大小
    db_path = 'data/database/stock_data.db'
    db_size = os.path.getsize(db_path) / 1024 / 1024  # MB
    
    print(f"\n数据库统计:")
    print(f"  股票数量: {stock_count}")
    print(f"  数据行数: {row_count:,}")
    print(f"  日期范围: {date_range[0]} 到 {date_range[1]}")
    print(f"  数据库大小: {db_size:.2f} MB")
    
    # 测试查询
    print(f"\n测试查询:")
    
    # 查询平安银行数据
    cursor.execute('''
        SELECT COUNT(*) FROM daily_data 
        WHERE symbol = 'sz.000001'
    ''')
    count = cursor.fetchone()[0]
    print(f"  平安银行数据行数: {count}")
    
    # 查询最新数据
    cursor.execute('''
        SELECT symbol, date, close FROM daily_data 
        WHERE symbol = 'sz.000001' 
        ORDER BY date DESC LIMIT 5
    ''')
    print(f"  最新5条数据:")
    for row in cursor.fetchall():
        print(f"    {row[0]} {row[1]} 收盘价: {row[2]:.2f}")


def main():
    """主函数"""
    print("="*60)
    print("CSV数据迁移到SQLite数据库")
    print("="*60)
    
    # 创建数据库
    conn = create_database()
    
    # 导入数据
    success_count = import_csv_to_sqlite(conn)
    
    # 验证数据库
    verify_database(conn)
    
    # 关闭连接
    conn.close()
    
    print("\n" + "="*60)
    print("数据库迁移完成！")
    print("="*60)
    print(f"\n数据库位置: data/database/stock_data.db")
    print(f"\n后续可以使用SQL查询数据，速度更快！")


if __name__ == '__main__':
    main()
