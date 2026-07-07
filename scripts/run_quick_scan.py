"""
快速信号扫描（抽样200只）
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
import random
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


def main():
    """主函数"""
    print("="*60)
    print("快速信号扫描（抽样200只）")
    print("="*60)
    print(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 获取本地数据文件
    data_dir = 'data/all_stocks'
    all_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    # 随机抽样200只
    random.seed(42)
    sample_files = random.sample(all_files, min(200, len(all_files)))
    
    print(f"总股票数: {len(all_files)}")
    print(f"抽样数量: {len(sample_files)}")
    print()
    
    # 扫描结果
    buy_signals = []
    sell_signals = []
    
    for i, filename in enumerate(sample_files):
        if (i + 1) % 50 == 0:
            print(f"进度: {i+1}/{len(sample_files)}")
        
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
            
            # 价格过滤
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
                })
            elif current_rsi > 70:
                sell_signals.append({
                    'symbol': symbol,
                    'price': current_price,
                    'rsi': current_rsi,
                })
                
        except Exception as e:
            continue
    
    # 打印结果
    print("\n" + "="*60)
    print("扫描结果")
    print("="*60)
    print(f"扫描股票数: {len(sample_files)}")
    print(f"买入信号: {len(buy_signals)} 只")
    print(f"卖出信号: {len(sell_signals)} 只")
    
    if buy_signals:
        print("\n【买入信号】（RSI超卖）")
        print("-"*50)
        print(f"{'代码':<15} {'价格':<10} {'RSI':<8}")
        print("-"*50)
        
        buy_signals.sort(key=lambda x: x['rsi'])
        for signal in buy_signals:
            print(f"{signal['symbol']:<15} {signal['price']:<10.2f} {signal['rsi']:<8.1f}")
    
    if sell_signals:
        print("\n【卖出信号】（RSI超买）")
        print("-"*50)
        print(f"{'代码':<15} {'价格':<10} {'RSI':<8}")
        print("-"*50)
        
        sell_signals.sort(key=lambda x: x['rsi'], reverse=True)
        for signal in sell_signals:
            print(f"{signal['symbol']:<15} {signal['price']:<10.2f} {signal['rsi']:<8.1f}")
    
    # 发送邮件
    if buy_signals or sell_signals:
        print("\n发送邮件报告...")
        try:
            # 邮件内容
            subject = f"[量化交易] 全量扫描 - 买入{len(buy_signals)}只 卖出{len(sell_signals)}只"
            
            content = f"""==================================================
量化交易全量扫描报告
==================================================

项目: Quant Trading System v1.0
扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
扫描股票数: {len(sample_files)}

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
操作建议: 考虑卖出或减仓
"""
            else:
                content += "\n无卖出信号\n"
            
            content += f"""
==================================================
风险提示: 以上信号仅供参考，请根据自己的判断操作

---
消息来源: Quant Trading System v1.0
自动发送，请勿回复
==================================================
"""
            
            # 发送邮件
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
