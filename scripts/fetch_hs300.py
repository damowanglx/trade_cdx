"""
获取沪深300基准数据
"""

import baostock as bs
import pandas as pd
import os

def fetch_hs300():
    """获取沪深300数据"""
    print("获取沪深300数据...")
    
    lg = bs.login()
    print(f"登录状态: {lg.error_msg}")
    
    # 获取沪深300指数数据
    rs = bs.query_history_k_data_plus(
        "sh.000300",
        "date,open,high,low,close,volume,amount",
        start_date="2020-01-01",
        end_date="2026-01-01",
        frequency="d"
    )
    
    if rs.error_code == '0':
        data_list = []
        while (rs.error_code == '0') and rs.next():
            data_list.append(rs.get_row_data())
        
        if data_list:
            df = pd.DataFrame(data_list, columns=rs.fields)
            df['date'] = pd.to_datetime(df['date'])
            numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            df = df.set_index('date')
            
            # 保存数据
            os.makedirs('data/cache', exist_ok=True)
            df.to_csv('data/cache/hs300_benchmark.csv', encoding='utf-8-sig')
            
            print(f"获取成功! 共 {len(df)} 条数据")
            print(f"时间范围: {df.index.min()} 到 {df.index.max()}")
            print(f"保存位置: data/cache/hs300_benchmark.csv")
            
            return df
    
    bs.logout()
    return None

if __name__ == '__main__':
    fetch_hs300()
