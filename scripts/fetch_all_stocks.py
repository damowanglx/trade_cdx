"""
获取全量A股数据
获取所有A股股票的历史数据

使用方法：
    python scripts/fetch_all_stocks.py
"""

import os
import sys
from datetime import datetime

import baostock as bs
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_all_stock_codes():
    """获取所有A股股票代码"""
    print("获取A股股票列表...")
    
    rs = bs.query_stock_basic()
    if rs.error_code != '0':
        print(f"获取股票列表失败: {rs.error_msg}")
        return []
    
    data_list = []
    while (rs.error_code == '0') and rs.next():
        data_list.append(rs.get_row_data())
    
    df = pd.DataFrame(data_list, columns=rs.fields)
    
    # 只保留A股（type=1表示股票，status=1表示上市）
    a_stocks = df[(df['type'] == '1') & (df['status'] == '1')]
    
    print(f"获取到 {len(a_stocks)} 只A股股票")
    return a_stocks['code'].tolist()


def fetch_single_stock(symbol, start_date, end_date):
    """获取单只股票数据"""
    try:
        rs = bs.query_history_k_data_plus(
            symbol,
            "date,open,high,low,close,volume,amount",
            start_date=start_date,
            end_date=end_date,
            frequency="d",
            adjustflag="2"
        )
        
        if rs.error_code == '0':
            data_list = []
            while (rs.error_code == '0') and rs.next():
                data_list.append(rs.get_row_data())
            
            if data_list and len(data_list) > 100:  # 至少100条数据
                df = pd.DataFrame(data_list, columns=rs.fields)
                df['date'] = pd.to_datetime(df['date'])
                numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount']
                for col in numeric_cols:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                df = df.set_index('date')
                return df
        return pd.DataFrame()
    except:
        return pd.DataFrame()


def main():
    """主函数"""
    print("="*60)
    print("获取全量A股数据")
    print("="*60)
    
    # 登录
    lg = bs.login()
    print(f"Baostock登录: {lg.error_msg}")
    
    # 获取所有股票代码
    all_stocks = get_all_stock_codes()
    
    if not all_stocks:
        print("获取股票列表失败")
        bs.logout()
        return
    
    # 设置时间范围（5年）
    start_date = '2020-01-01'
    end_date = '2026-01-01'
    
    print(f"\n获取时间范围: {start_date} 到 {end_date}")
    print(f"股票总数: {len(all_stocks)} 只")
    print(f"预计时间: {len(all_stocks) * 0.5 / 60:.0f} 分钟")
    print()
    
    # 创建数据目录
    os.makedirs('data/all_stocks', exist_ok=True)
    
    # 获取每只股票数据
    success_count = 0
    fail_count = 0
    
    for i, symbol in enumerate(all_stocks):
        if i % 100 == 0:
            print(f"进度: {i}/{len(all_stocks)} ({i/len(all_stocks)*100:.1f}%)")
        
        df = fetch_single_stock(symbol, start_date, end_date)
        
        if not df.empty:
            # 保存数据
            filename = f"{symbol.replace('.', '_')}.csv"
            df.to_csv(f'data/all_stocks/{filename}', encoding='utf-8-sig')
            success_count += 1
        else:
            fail_count += 1
    
    # 登出
    bs.logout()
    
    print("\n" + "="*60)
    print(f"数据获取完成!")
    print(f"成功: {success_count} 只")
    print(f"失败: {fail_count} 只")
    print(f"总计: {len(all_stocks)} 只")
    print("="*60)
    
    # 统计数据量
    total_files = len([f for f in os.listdir('data/all_stocks') if f.endswith('.csv')])
    print(f"\n生成文件数: {total_files}")
    print(f"保存位置: data/all_stocks/")


if __name__ == '__main__':
    main()
