"""
批量获取A股数据
获取多只股票、更长时间的数据

使用方法：
    python scripts/fetch_more_data.py
"""

import os
import sys

import baostock as bs
import pandas as pd

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def fetch_stock_data(symbol, start_date, end_date):
    """获取单只股票数据"""
    try:
        rs = bs.query_history_k_data_plus(
            symbol,
            "date,open,high,low,close,volume,amount",
            start_date=start_date,
            end_date=end_date,
            frequency="d",
            adjustflag="2"  # 前复权
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
                return df
        return pd.DataFrame()
    except Exception as e:
        print(f"获取 {symbol} 失败: {e}")
        return pd.DataFrame()


def main():
    """主函数"""
    print("="*60)
    print("批量获取A股数据")
    print("="*60)
    
    # 登录
    lg = bs.login()
    print(f"Baostock登录: {lg.error_msg}")
    
    # 定义股票列表（蓝筹股 + 热门股）
    stocks = {
        # 银行股
        'sz.000001': '平安银行',
        'sh.601398': '工商银行',
        'sh.601939': '建设银行',
        'sh.600036': '招商银行',
        
        # 白酒股
        'sh.600519': '贵州茅台',
        'sz.000858': '五粮液',
        'sz.000568': '泸州老窖',
        
        # 科技股
        'sz.000725': '京东方A',
        'sz.002415': '海康威视',
        
        # 新能源
        'sz.300750': '宁德时代',
        'sz.002594': '比亚迪',
        
        # 医药
        'sh.600276': '恒瑞医药',
        'sz.000538': '云南白药',
    }
    
    # 获取5年数据
    start_date = '2020-01-01'
    end_date = '2026-01-01'
    
    print(f"\n获取时间范围: {start_date} 到 {end_date}")
    print(f"获取股票数量: {len(stocks)} 只")
    print()
    
    # 创建数据目录
    os.makedirs('data/cache', exist_ok=True)
    
    # 获取每只股票数据
    success_count = 0
    for symbol, name in stocks.items():
        print(f"获取 {name}({symbol})...", end=" ")
        
        df = fetch_stock_data(symbol, start_date, end_date)
        
        if not df.empty:
            # 保存数据
            filename = f"{symbol.replace('.', '_')}_daily.csv"
            df.to_csv(f'data/cache/{filename}', encoding='utf-8-sig')
            print(f"成功! {len(df)} 条数据")
            success_count += 1
        else:
            print("失败!")
    
    # 登出
    bs.logout()
    
    print("\n" + "="*60)
    print(f"数据获取完成! 成功: {success_count}/{len(stocks)}")
    print("="*60)
    print("\n数据保存在: data/cache/ 目录")
    print("\n生成的文件:")
    for f in os.listdir('data/cache'):
        if f.endswith('_daily.csv'):
            filepath = os.path.join('data/cache', f)
            size = os.path.getsize(filepath) / 1024
            print(f"  - {f} ({size:.1f} KB)")


if __name__ == '__main__':
    main()
