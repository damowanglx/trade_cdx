"""
全量信号扫描（使用本地数据）
使用已下载的股票数据进行信号扫描

使用方法：
    python scripts/run_local_scan.py
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def calculate_rsi(prices, period=14):
    """计算RSI"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def scan_local_stocks():
    """扫描本地股票数据"""
    print("="*60)
    print("全量A股信号扫描（本地数据）")
    print("="*60)
    print(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 获取本地数据文件
    data_dir = 'data/all_stocks'
    data_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    print(f"本地数据文件: {len(data_files)} 只股票")
    print()
    
    # 扫描结果
    buy_signals = []
    sell_signals = []
    scan_count = 0
    
    for i, filename in enumerate(data_files):
        if (i + 1) % 500 == 0:
            print(f"进度: {i+1}/{len(data_files)}")
        
        try:
            # 读取数据
            filepath = os.path.join(data_dir, filename)
            df = pd.read_csv(filepath)
            
            if len(df) < 30:
                continue
            
            # 获取股票代码
            symbol = filename.replace('.csv', '').replace('_', '.')
            
            # 获取最新数据
            current_price = df['close'].iloc[-1]
            current_volume = df['volume'].iloc[-1] if 'volume' in df.columns else 0
            
            # 活跃度过滤
            if current_price < 5 or current_price > 500:
                continue
            
            # 计算RSI
            rsi = calculate_rsi(df['close'], 21)
            current_rsi = rsi.iloc[-1]
            
            scan_count += 1
            
            # 信号判断
            if current_rsi < 30:
                buy_signals.append({
                    'symbol': symbol,
                    'price': current_price,
                    'rsi': current_rsi,
                    'volume': current_volume,
                })
            elif current_rsi > 70:
                sell_signals.append({
                    'symbol': symbol,
                    'price': current_price,
                    'rsi': current_rsi,
                    'volume': current_volume,
                })
                
        except Exception as e:
            continue
    
    # 打印结果
    print("\n" + "="*60)
    print("扫描结果")
    print("="*60)
    print(f"扫描股票数: {scan_count}")
    print(f"买入信号: {len(buy_signals)} 只")
    print(f"卖出信号: {len(sell_signals)} 只")
    
    if buy_signals:
        print("\n【买入信号】（RSI超卖）")
        print("-"*70)
        print(f"{'代码':<12} {'价格':<10} {'RSI':<8} {'成交量':<15}")
        print("-"*70)
        
        buy_signals.sort(key=lambda x: x['rsi'])
        for signal in buy_signals[:20]:  # 只显示前20只
            print(f"{signal['symbol']:<12} {signal['price']:<10.2f} {signal['rsi']:<8.1f} {signal['volume']:<15,.0f}")
    
    if sell_signals:
        print("\n【卖出信号】（RSI超买）")
        print("-"*70)
        print(f"{'代码':<12} {'价格':<10} {'RSI':<8} {'成交量':<15}")
        print("-"*70)
        
        sell_signals.sort(key=lambda x: x['rsi'], reverse=True)
        for signal in sell_signals[:20]:  # 只显示前20只
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
            for signal in buy_signals[:20]:
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
            for signal in sell_signals[:20]:
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
    buy_signals, sell_signals = scan_local_stocks()
    
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
