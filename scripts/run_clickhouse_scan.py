"""
ClickHouse全量扫描脚本（修复版）
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
    print("ClickHouse全量扫描")
    print("="*60)
    print(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 获取最新交易日
    print("获取最新交易日...")
    r = requests.get(CLICKHOUSE_URL, params={
        'query': 'SELECT max(trade_date) FROM daily_bars',
        'user': CLICKHOUSE_USER,
        'password': CLICKHOUSE_PASS,
        'database': CLICKHOUSE_DB,
    })
    
    latest_date = r.text.strip()
    print(f"最新交易日: {latest_date}")
    
    # 获取全市场最新数据
    print("\n获取全市场数据...")
    data_sql = f"""
    SELECT ts_code, trade_date, close, vol
    FROM daily_bars 
    WHERE trade_date >= toString(toDate('{latest_date}') - 90)
    ORDER BY ts_code, trade_date FORMAT TabSeparatedWithNames
    """
    
    df = query_clickhouse(data_sql)
    
    if df.empty:
        print("获取数据失败")
        return
    
    print(f"获取到 {len(df)} 条数据")
    
    # 转换数据类型
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df['vol'] = pd.to_numeric(df['vol'], errors='coerce')
    
    # 按股票分组计算RSI
    print("\n计算RSI指标...")
    
    buy_signals = []
    sell_signals = []
    
    for ts_code, group in df.groupby('ts_code'):
        if len(group) < 30:
            continue
        
        group = group.sort_values('trade_date')
        
        current_price = float(group['close'].iloc[-1])
        current_vol = float(group['vol'].iloc[-1])
        
        if current_price < 5 or current_price > 500:
            continue
        
        if current_vol < 5000000:
            continue
        
        rsi = calculate_rsi(group['close'], 21)
        current_rsi = float(rsi.iloc[-1])
        
        if np.isnan(current_rsi):
            continue
        
        # 计算交易计划
        if current_rsi < 30:
            if current_rsi < 20:
                position_pct = 0.30
                strength = "强烈"
            elif current_rsi < 25:
                position_pct = 0.25
                strength = "较强"
            else:
                position_pct = 0.20
                strength = "一般"
            
            invest_amount = 200000 * position_pct
            buy_quantity = int(invest_amount / current_price / 100) * 100
            
            buy_signals.append({
                'symbol': ts_code,
                'price': current_price,
                'rsi': current_rsi,
                'buy_quantity': buy_quantity,
                'invest_amount': invest_amount,
                'position_pct': position_pct,
                'strength': strength,
                'stop_loss': round(current_price * 0.90, 2),
                'take_profit': round(current_price * 1.30, 2),
            })
        elif current_rsi > 70:
            sell_signals.append({
                'symbol': ts_code,
                'price': current_price,
                'rsi': current_rsi,
            })
    
    # 打印结果
    print("\n" + "="*60)
    print("扫描结果")
    print("="*60)
    print(f"买入信号: {len(buy_signals)} 只")
    print(f"卖出信号: {len(sell_signals)} 只")
    
    if buy_signals:
        print("\n【买入信号】（RSI超卖）")
        print("-"*100)
        print(f"{'代码':<12} {'价格':<8} {'RSI':<6} {'买入数量':<10} {'止损价':<8} {'止盈价':<8} {'仓位':<6}")
        print("-"*100)
        
        buy_signals.sort(key=lambda x: x['rsi'])
        for signal in buy_signals[:20]:
            print(f"{signal['symbol']:<12} {signal['price']:<8.2f} {signal['rsi']:<6.1f} "
                  f"{signal['buy_quantity']:<10} {signal['stop_loss']:<8.2f} "
                  f"{signal['take_profit']:<8.2f} {signal['position_pct']*100:<6.0f}%")
    
    if sell_signals:
        print("\n【卖出信号】（RSI超买）")
        print("-"*50)
        print(f"{'代码':<12} {'价格':<8} {'RSI':<6}")
        print("-"*50)
        
        sell_signals.sort(key=lambda x: x['rsi'], reverse=True)
        for signal in sell_signals[:20]:
            print(f"{signal['symbol']:<12} {signal['price']:<8.2f} {signal['rsi']:<6.1f}")
    
    # 发送邮件
    if buy_signals or sell_signals:
        print("\n发送邮件报告...")
        try:
            subject = f"[量化交易] 全量扫描 - 买入{len(buy_signals)}只 卖出{len(sell_signals)}只"
            
            content = f"""==================================================
量化交易全量扫描报告
==================================================

项目: Quant Trading System v1.0
数据源: ClickHouse
扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
最新交易日: {latest_date}
总资金: 200,000元

==================================================

【买入信号】（RSI超卖）
"""
            if buy_signals:
                buy_signals.sort(key=lambda x: x['rsi'])
                for signal in buy_signals[:20]:
                    content += f"""
--------------------------------------------------
股票代码: {signal['symbol']}
当前价格: {signal['price']:.2f}
RSI指标: {signal['rsi']:.1f}
信号强度: {signal['strength']}

【交易计划】
  买入价格: {signal['price']:.2f}
  买入数量: {signal['buy_quantity']}股
  投入资金: {signal['invest_amount']:,.2f}元
  仓位比例: {signal['position_pct']*100:.0f}%
  
  止损价格: {signal['stop_loss']:.2f}（下跌10%）
  止盈价格: {signal['take_profit']:.2f}（上涨30%）

【操作步骤】
  1. 打开手机国金证券APP
  2. 搜索股票代码 {signal['symbol']}
  3. 以 {signal['price']:.2f} 元买入 {signal['buy_quantity']} 股
  4. 设置止损价: {signal['stop_loss']:.2f}
  5. 设置止盈价: {signal['take_profit']:.2f}
"""
            else:
                content += "\n无买入信号\n"
            
            content += f"""
==================================================

【卖出信号】（RSI超买）
"""
            if sell_signals:
                sell_signals.sort(key=lambda x: x['rsi'], reverse=True)
                for signal in sell_signals[:20]:
                    content += f"""
--------------------------------------------------
股票代码: {signal['symbol']}
当前价格: {signal['price']:.2f}
RSI指标: {signal['rsi']:.1f}

【操作建议】
  1. 打开手机国金证券APP
  2. 搜索股票代码 {signal['symbol']}
  3. 以 {signal['price']:.2f} 元卖出全部持仓
"""
            else:
                content += "\n无卖出信号\n"
            
            content += f"""
==================================================
【风险提示】
  - 以上信号仅供参考，请根据自己的判断操作
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
    print("扫描完成！")
    print("="*60)


if __name__ == '__main__':
    main()


