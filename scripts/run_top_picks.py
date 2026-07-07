"""
精选股票推荐
只推荐3-5只最佳买入和卖出信号

使用方法：
    python scripts/run_top_picks.py
"""

import sys
import os
import requests
import pandas as pd
import numpy as np
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ClickHouse配置
CLICKHOUSE_URL = 'http://localhost:8123'
CLICKHOUSE_USER = 'quant'
CLICKHOUSE_PASS = 'quant123'
CLICKHOUSE_DB = 'quant'


def query_clickhouse(sql):
    """查询ClickHouse"""
    try:
        r = requests.get(CLICKHOUSE_URL, params={
            'query': sql,
            'user': CLICKHOUSE_USER,
            'password': CLICKHOUSE_PASS,
            'database': CLICKHOUSE_DB,
        })
        
        if r.status_code == 200 and r.text.strip():
            lines = r.text.strip().split('\n')
            if len(lines) > 0:
                headers = lines[0].split('\t')
                data = []
                for line in lines[1:]:
                    if line.strip():
                        data.append(line.split('\t'))
                if data:
                    return pd.DataFrame(data, columns=headers)
        return pd.DataFrame()
    except Exception as e:
        print(f"查询失败: {e}")
        return pd.DataFrame()


def calculate_rsi(prices, period=14):
    """计算RSI"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def main():
    """主函数"""
    print("="*60)
    print("精选股票推荐")
    print("="*60)
    print(f"推荐时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 获取最新交易日
    r = requests.get(CLICKHOUSE_URL, params={
        'query': 'SELECT max(trade_date) FROM daily_bars',
        'user': CLICKHOUSE_USER,
        'password': CLICKHOUSE_PASS,
        'database': CLICKHOUSE_DB,
    })
    latest_date = r.text.strip()
    print(f"最新交易日: {latest_date}")
    
    # 获取全市场数据
    print("获取全市场数据...")
    data_sql = f"""
    SELECT ts_code, trade_date, close, vol
    FROM daily_bars 
    WHERE trade_date >= toString(toDate('{latest_date}') - 90)
    ORDER BY ts_code, trade_date
    FORMAT TabSeparatedWithNames
    """
    
    df = query_clickhouse(data_sql)
    
    if df.empty:
        print("获取数据失败")
        return
    
    print(f"获取到 {len(df)} 条数据")
    
    # 转换数据类型
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df['vol'] = pd.to_numeric(df['vol'], errors='coerce')
    
    # 计算所有股票的RSI
    print("计算RSI指标...")
    
    all_stocks = []
    
    for ts_code, group in df.groupby('ts_code'):
        if len(group) < 30:
            continue
        
        group = group.sort_values('trade_date')
        
        current_price = float(group['close'].iloc[-1])
        current_volume = float(group['vol'].iloc[-1])
        
        # 过滤条件
        if current_price < 10 or current_price > 300:  # 只推荐10元以上的股票（通常是大盘股）
            continue
        if current_volume < 50000000:  # 成交量5000万以上（更活跃）
            continue
        
        # 计算成交额（价格 * 成交量）
        current_amount = current_price * current_volume
        if current_amount < 100000000:  # 成交额1亿以上（流动性好）
            continue
        
        # 排除科创板（688开头）和北交所（8开头）
        if ts_code.startswith('688') or ts_code.startswith('8'):
            continue
        
        # 只保留主板（60开头）和创业板（30、00开头）
        if not (ts_code.startswith('60') or ts_code.startswith('30') or ts_code.startswith('00')):
            continue
        
        # 计算RSI
        rsi = calculate_rsi(group['close'], 21)
        current_rsi = float(rsi.iloc[-1])
        
        if np.isnan(current_rsi):
            continue
        
        # 计算20日平均成交量
        avg_volume = float(group['vol'].tail(20).mean())
        
        all_stocks.append({
            'symbol': ts_code,
            'price': current_price,
            'rsi': current_rsi,
            'volume': current_volume,
            'avg_volume': avg_volume,
        })
    
    # 转换为DataFrame
    stocks_df = pd.DataFrame(all_stocks)
    
    # 筛选买入信号（RSI < 30，且成交量活跃）
    buy_candidates = stocks_df[
        (stocks_df['rsi'] < 30) & 
        (stocks_df['volume'] > stocks_df['avg_volume'] * 0.5)
    ].sort_values('rsi').head(5)
    
    # 筛选卖出信号（RSI > 70）
    sell_candidates = stocks_df[stocks_df['rsi'] > 70].sort_values('rsi', ascending=False).head(5)
    
    # 打印推荐结果
    print("\n" + "="*60)
    print("精选推荐")
    print("="*60)
    
    # 买入推荐
    print("\n【买入推荐】（RSI超卖，建议买入）")
    print("-"*60)
    
    buy_recommendations = []
    
    for i, (_, stock) in enumerate(buy_candidates.iterrows(), 1):
        symbol = stock['symbol']
        price = stock['price']
        rsi = stock['rsi']
        
        # 计算交易计划
        if rsi < 15:
            position_pct = 0.30
            strength = "强烈推荐"
        elif rsi < 20:
            position_pct = 0.25
            strength = "推荐"
        else:
            position_pct = 0.20
            strength = "关注"
        
        # 20万资金
        capital = 200000
        invest_amount = capital * position_pct
        buy_quantity = int(invest_amount / price / 100) * 100
        stop_loss = round(price * 0.90, 2)
        take_profit = round(price * 1.30, 2)
        
        buy_recommendations.append({
            'symbol': symbol,
            'price': price,
            'rsi': rsi,
            'strength': strength,
            'position_pct': position_pct,
            'invest_amount': invest_amount,
            'buy_quantity': buy_quantity,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
        })
        
        print(f"\n{i}. {symbol} - {strength}")
        print(f"   当前价格: {price:.2f}")
        print(f"   RSI指标: {rsi:.1f}")
        print(f"   买入数量: {buy_quantity} 股")
        print(f"   投入资金: {invest_amount:,.2f} 元")
        print(f"   止损价格: {stop_loss:.2f}（下跌10%）")
        print(f"   止盈价格: {take_profit:.2f}（上涨30%）")
    
    # 卖出推荐
    print("\n" + "="*60)
    print("【卖出建议】（RSI超买，考虑卖出）")
    print("-"*60)
    
    sell_recommendations = []
    
    for i, (_, stock) in enumerate(sell_candidates.iterrows(), 1):
        symbol = stock['symbol']
        price = stock['price']
        rsi = stock['rsi']
        
        sell_recommendations.append({
            'symbol': symbol,
            'price': price,
            'rsi': rsi,
        })
        
        print(f"\n{i}. {symbol}")
        print(f"   当前价格: {price:.2f}")
        print(f"   RSI指标: {rsi:.1f}")
        print(f"   建议: 考虑卖出或减仓")
    
    # 发送邮件
    print("\n" + "="*60)
    print("发送邮件...")
    
    try:
        subject = f"[量化交易] 精选推荐 - 买入{len(buy_recommendations)}只 卖出{len(sell_recommendations)}只"
        
        content = f"""==================================================
量化交易精选推荐
==================================================

项目: Quant Trading System v1.0
推荐时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
最新交易日: {latest_date}
总资金: 200,000元

==================================================

【买入推荐】（RSI超卖，建议买入）
"""
        for i, rec in enumerate(buy_recommendations, 1):
            content += f"""
--------------------------------------------------
{i}. 股票代码: {rec['symbol']}
   当前价格: {rec['price']:.2f}
   RSI指标: {rec['rsi']:.1f}
   推荐强度: {rec['strength']}

【交易计划】
   买入价格: {rec['price']:.2f}
   买入数量: {rec['buy_quantity']} 股
   投入资金: {rec['invest_amount']:,.2f} 元
   仓位比例: {rec['position_pct']*100:.0f}%
   
   止损价格: {rec['stop_loss']:.2f}（下跌10%）
   止盈价格: {rec['take_profit']:.2f}（上涨30%）
   
   止损金额: {rec['buy_quantity'] * (rec['price'] - rec['stop_loss']):,.2f}元
   止盈金额: {rec['buy_quantity'] * (rec['take_profit'] - rec['price']):,.2f}元

【操作步骤】
   1. 打开手机国金证券APP
   2. 搜索股票代码 {rec['symbol']}
   3. 以 {rec['price']:.2f} 元买入 {rec['buy_quantity']} 股
   4. 设置止损价: {rec['stop_loss']:.2f}
   5. 设置止盈价: {rec['take_profit']:.2f}
"""
        
        content += f"""
==================================================

【卖出建议】（RSI超买，考虑卖出）
"""
        for i, rec in enumerate(sell_recommendations, 1):
            content += f"""
--------------------------------------------------
{i}. 股票代码: {rec['symbol']}
   当前价格: {rec['price']:.2f}
   RSI指标: {rec['rsi']:.1f}
   建议: 考虑卖出或减仓
"""
        
        content += f"""
==================================================
【风险提示】
  - 以上推荐仅供参考，请根据自己的判断操作
  - 控制好仓位，不要满仓操作
  - 设置好止损止盈，控制风险
  - 投资有风险，入市需谨慎

==================================================
消息来源: Quant Trading System v1.0
数据源: ClickHouse
项目名称: 量化交易系统
发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
自动发送，请勿回复
==================================================
"""
        
        msg = MIMEMultipart()
        msg['From'] = 'damowang123lx@163.com'
        msg['To'] = 'damowang123lx@163.com'
        msg['Subject'] = subject
        msg.attach(MIMEText(content, 'plain', 'utf-8'))
        
        server = smtplib.SMTP_SSL('smtp.163.com', 465)
        server.login('damowang123lx@163.com', 'GXrpVgWngzGxpTkb')
        server.sendmail('damowang123lx@163.com', 'damowang123lx@163.com', msg.as_string())
        server.quit()
        
        print("邮件发送成功！")
        
    except Exception as e:
        print(f"邮件发送失败: {e}")
    
    print("\n" + "="*60)
    print("推荐完成！")
    print("="*60)


if __name__ == '__main__':
    main()



