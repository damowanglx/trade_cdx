"""
获取全量A股数据（带重试和断点续传）

功能：
- 自动重试失败的请求
- 断点续传，跳过已下载的股票
- 进度保存
- 更稳定的连接处理

使用方法：
    python scripts/fetch_all_stocks_v2.py
"""

import json
import os
import sys
import time

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
    
    # 只保留A股
    a_stocks = df[(df['type'] == '1') & (df['status'] == '1')]
    
    print(f"获取到 {len(a_stocks)} 只A股股票")
    return a_stocks['code'].tolist()


def fetch_single_stock(symbol, start_date, end_date, max_retries=3):
    """获取单只股票数据（带重试）"""
    for attempt in range(max_retries):
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
                
                if data_list and len(data_list) > 100:
                    df = pd.DataFrame(data_list, columns=rs.fields)
                    df['date'] = pd.to_datetime(df['date'])
                    numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount']
                    for col in numeric_cols:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    df = df.set_index('date')
                    return df
            return pd.DataFrame()
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)  # 等待1秒后重试
            else:
                return pd.DataFrame()
    return pd.DataFrame()


def load_progress():
    """加载进度"""
    progress_file = 'data/all_stocks/progress.json'
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            return json.load(f)
    return {'completed': [], 'failed': []}


def save_progress(progress):
    """保存进度"""
    os.makedirs('data/all_stocks', exist_ok=True)
    progress_file = 'data/all_stocks/progress.json'
    with open(progress_file, 'w') as f:
        json.dump(progress, f)


def main():
    """主函数"""
    print("="*60)
    print("获取全量A股数据（带断点续传）")
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
    
    # 加载进度
    progress = load_progress()
    completed = set(progress['completed'])
    
    # 过滤已完成的
    remaining = [s for s in all_stocks if s not in completed]
    
    print(f"\n股票总数: {len(all_stocks)}")
    print(f"已完成: {len(completed)}")
    print(f"待获取: {len(remaining)}")
    
    # 设置时间范围
    start_date = '2020-01-01'
    end_date = '2026-01-01'
    
    print(f"\n获取时间范围: {start_date} 到 {end_date}")
    print(f"预计时间: {len(remaining) * 0.5 / 60:.0f} 分钟")
    print()
    
    # 创建数据目录
    os.makedirs('data/all_stocks', exist_ok=True)
    
    # 获取每只股票数据
    success_count = 0
    fail_count = 0
    
    for i, symbol in enumerate(remaining):
        if i % 50 == 0:
            print(f"进度: {i}/{len(remaining)} ({i/len(remaining)*100:.1f}%)")
        
        df = fetch_single_stock(symbol, start_date, end_date)
        
        if not df.empty:
            # 保存数据
            filename = f"{symbol.replace('.', '_')}.csv"
            df.to_csv(f'data/all_stocks/{filename}', encoding='utf-8-sig')
            completed.add(symbol)
            success_count += 1
        else:
            progress['failed'].append(symbol)
            fail_count += 1
        
        # 每100只保存一次进度
        if i % 100 == 0:
            progress['completed'] = list(completed)
            save_progress(progress)
    
    # 保存最终进度
    progress['completed'] = list(completed)
    save_progress(progress)
    
    # 登出
    bs.logout()
    
    print("\n" + "="*60)
    print(f"数据获取完成!")
    print(f"本次成功: {success_count}")
    print(f"本次失败: {fail_count}")
    print(f"总计完成: {len(completed)}/{len(all_stocks)}")
    print("="*60)
    
    # 统计数据量
    total_files = len([f for f in os.listdir('data/all_stocks') if f.endswith('.csv')])
    print(f"\n生成文件数: {total_files}")
    print(f"保存位置: data/all_stocks/")


if __name__ == '__main__':
    main()
