"""
全量A股信号筛选系统（优化版）
一次性登录，批量获取数据

使用方法：
    python scripts/run_full_scan_v2.py
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import baostock as bs

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def calculate_rsi(prices, period=14):
    """计算RSI"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def scan_stocks():
    """扫描股票"""
    print("="*60)
    print("全量A股信号筛选")
    print("="*60)
    print(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 登录
    lg = bs.login()
    print(f"Baostock登录: {lg.error_msg}")
    
    # 获取股票列表
    print("获取股票列表...")
    rs = bs.query_stock_basic()
    data_list = []
    while (rs.error_code == '0') and rs.next():
        data_list.append(rs.get_row_data())
    
    df_stocks = pd.DataFrame(data_list, columns=rs.fields)
    a_stocks = df_stocks[(df_stocks['type'] == '1') & (df_stocks['status'] == '1')]
    stock_list = a_stocks['code'].tolist()
    
    print(f"获取到 {len(stock_list)} 只A股股票")
    
    # 限制扫描数量
    stock_list = stock_list[:200]
    print(f"扫描前 {len(stock_list)} 只")
    print()
    
    # 扫描结果
    buy_signals = []
    sell_signals = []
    
    # 逐个扫描
    for i, symbol in enumerate(stock_list):
        if (i + 1) % 50 == 0:
            print(f"进度: {i+1}/{len(stock_list)}")
        
        try:
            # 获取数据
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - pd.Timedelta(days=90)).strftime('%Y-%m-%d')
            
            rs = bs.query_history_k_data_plus(
                symbol,
                "date,close,volume,amount",
                start_date=start_date,
                end_date=end_date,
                frequency="d",
                adjustflag="2"
            )
            
            if rs.error_code != '0':
                continue
            
            data_list = []
            while (rs.error_code == '0') and rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list or len(data_list) < 30:
                continue
            
            df = pd.DataFrame(data_list, columns=rs.fields)
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            
            # 活跃度过滤
            recent = df.tail(5)
            avg_volume = recent['volume'].mean()
            avg_amount = recent['amount'].mean()
            current_price = df['close'].iloc[-1]
            
            if avg_volume < 5000000 or avg_amount < 50000000:
                continue
            if current_price < 5 or current_price > 500:
                continue
            
            # 计算RSI
            rsi = calculate_rsi(df['close'], 21)
            current_rsi = rsi.iloc[-1]
            
            # 信号判断
            if current_rsi < 30:
                buy_signals.append({
                    'symbol': symbol,
                    'price': current_price,
                    'rsi': current_rsi,
                    'volume': avg_volume,
                    'amount': avg_amount,
                })
            elif current_rsi > 70:
                sell_signals.append({
                    'symbol': symbol,
                    'price': current_price,
                    'rsi': current_rsi,
                    'volume': avg_volume,
                    'amount': avg_amount,
                })
                
        except Exception as e:
            continue
    
    # 登出
    bs.logout()
    
    # 打印结果
    print("\n" + "="*60)
    print("扫描结果")
    print("="*60)
    print(f"扫描股票数: {len(stock_list)}")
    print(f"买入信号: {len(buy_signals)} 只")
    print(f"卖出信号: {len(sell_signals)} 只")
    
    if buy_signals:
        print("\n【买入信号】（RSI超卖）")
        print("-"*60)
        print(f"{'代码':<12} {'价格':<10} {'RSI':<8} {'成交量':<15}")
        print("-"*60)
        
        buy_signals.sort(key=lambda x: x['rsi'])
        for signal in buy_signals:
            print(f"{signal['symbol']:<12} {signal['price']:<10.2f} {signal['rsi']:<8.1f} {signal['volume']:<15,.0f}")
    
    if sell_signals:
        print("\n【卖出信号】（RSI超买）")
        print("-"*60)
        print(f"{'代码':<12} {'价格':<10} {'RSI':<8} {'成交量':<15}")
        print("-"*60)
        
        sell_signals.sort(key=lambda x: x['rsi'], reverse=True)
        for signal in sell_signals:
            print(f"{signal['symbol']:<12} {signal['price']:<10.2f} {signal['rsi']:<8.1f} {signal['volume']:<15,.0f}")
    
    return buy_signals, sell_signals


def send_email_report(buy_signals, sell_signals):
    """发送邮件报告"""
    try:
        # 邮件配置
        smtp_server = 'smtp.163.com'
        smtp_port = 465
        sender_email = 'damowang123lx@163.com'
        sender_password = 'GXrpVgWngzGxpTkb'
        receiver_email = 'damowang123lx@163.com'
        
        # 邮件主题
        subject = f"[量化交易] 全量扫描 - 买入{len(buy_signals)}只 卖出{len(sell_signals)}只"
        
        # 邮件内容
        content = f"""==================================================
量化交易全量扫描报告
==================================================

项目: Quant Trading System v1.0
扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

==================================================

【买入信号】（RSI超卖，可考虑买入）
"""
        if buy_signals:
            buy_signals.sort(key=lambda x: x['rsi'])
            for signal in buy_signals:
                content += f"""
股票代码: {signal['symbol']}
当前价格: {signal['price']:.2f}
RSI指标: {signal['rsi']:.1f}
成交量: {signal['volume']:,.0f}
操作建议: 仓位20-30%，止损-10%，止盈+30%
"""
        else:
            content += "\n无买入信号\n"
        
        content += f"""
==================================================

【卖出信号】（RSI超买，考虑卖出）
"""
        if sell_signals:
            sell_signals.sort(key=lambda x: x['rsi'], reverse=True)
            for signal in sell_signals:
                content += f"""
股票代码: {signal['symbol']}
当前价格: {signal['price']:.2f}
RSI指标: {signal['rsi']:.1f}
成交量: {signal['volume']:,.0f}
操作建议: 考虑卖出或减仓
"""
        else:
            content += "\n无卖出信号\n"
        
        content += f"""
==================================================
风险提示: 以上信号仅供参考，请根据自己的判断操作
==================================================

---
消息来源: Quant Trading System v1.0
项目名称: 量化交易系统
自动发送，请勿回复
"""
        
        # 发送邮件
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(content, 'plain', 'utf-8'))
        
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        
        print("邮件发送成功！")
        return True
        
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False


def main():
    """主函数"""
    # 扫描股票
    buy_signals, sell_signals = scan_stocks()
    
    # 发送邮件
    if buy_signals or sell_signals:
        print("\n发送邮件报告...")
        send_email_report(buy_signals, sell_signals)
    else:
        print("\n无信号，不发送邮件")
    
    print("\n" + "="*60)
    print("全量扫描完成！")
    print("="*60)


if __name__ == '__main__':
    main()
