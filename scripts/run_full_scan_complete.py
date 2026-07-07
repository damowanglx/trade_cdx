"""
全量信号扫描（完整版）
包含买入/卖出数量、价格、止损、止盈

使用方法：
    python scripts/run_full_scan_complete.py
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


def calculate_trading_plan(price, rsi, capital=200000, position_pct=0.25):
    """
    计算交易计划
    
    Args:
        price: 当前价格
        rsi: RSI值
        capital: 总资金（默认20万）
        position_pct: 仓位比例（默认25%）
    
    Returns:
        dict: 交易计划
    """
    # 计算买入数量（按手取整，1手=100股）
    invest_amount = capital * position_pct
    buy_quantity = int(invest_amount / price / 100) * 100
    
    # 计算止损止盈价格
    stop_loss_pct = 0.10  # 止损10%
    take_profit_pct = 0.30  # 止盈30%
    
    stop_loss_price = round(price * (1 - stop_loss_pct), 2)
    take_profit_price = round(price * (1 + take_profit_pct), 2)
    
    # 根据RSI强度调整仓位
    if rsi < 20:
        # 极度超卖，加大仓位
        position_pct = 0.30
        strength = "强烈"
    elif rsi < 25:
        position_pct = 0.25
        strength = "较强"
    elif rsi < 30:
        position_pct = 0.20
        strength = "一般"
    else:
        position_pct = 0.15
        strength = "弱"
    
    # 重新计算买入数量
    invest_amount = capital * position_pct
    buy_quantity = int(invest_amount / price / 100) * 100
    
    return {
        'capital': capital,
        'position_pct': position_pct,
        'invest_amount': invest_amount,
        'buy_quantity': buy_quantity,
        'buy_price': price,
        'stop_loss_price': stop_loss_price,
        'stop_loss_pct': stop_loss_pct,
        'take_profit_price': take_profit_price,
        'take_profit_pct': take_profit_pct,
        'strength': strength,
    }


def main():
    """主函数"""
    print("="*60)
    print("全量信号扫描（完整版）")
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
                # 计算交易计划
                plan = calculate_trading_plan(current_price, current_rsi)
                
                buy_signals.append({
                    'symbol': symbol,
                    'price': current_price,
                    'rsi': current_rsi,
                    'plan': plan,
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
        print("-"*100)
        print(f"{'代码':<12} {'价格':<8} {'RSI':<6} {'买入数量':<10} {'止损价':<8} {'止盈价':<8} {'仓位':<6}")
        print("-"*100)
        
        buy_signals.sort(key=lambda x: x['rsi'])
        for signal in buy_signals:
            plan = signal['plan']
            print(f"{signal['symbol']:<12} {signal['price']:<8.2f} {signal['rsi']:<6.1f} "
                  f"{plan['buy_quantity']:<10} {plan['stop_loss_price']:<8.2f} "
                  f"{plan['take_profit_price']:<8.2f} {plan['position_pct']*100:<6.0f}%")
    
    if sell_signals:
        print("\n【卖出信号】（RSI超买）")
        print("-"*50)
        print(f"{'代码':<12} {'价格':<8} {'RSI':<6}")
        print("-"*50)
        
        sell_signals.sort(key=lambda x: x['rsi'], reverse=True)
        for signal in sell_signals:
            print(f"{signal['symbol']:<12} {signal['price']:<8.2f} {signal['rsi']:<6.1f}")
    
    # 发送邮件
    if buy_signals or sell_signals:
        print("\n发送邮件报告...")
        try:
            # 邮件主题
            subject = f"[量化交易] 全量扫描 - 买入{len(buy_signals)}只 卖出{len(sell_signals)}只"
            
            # 邮件内容
            content = f"""==================================================
量化交易全量扫描报告
==================================================

项目: Quant Trading System v1.0
扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
扫描股票数: {len(sample_files)}
总资金: 200,000元

==================================================

【买入信号】（RSI超卖）
"""
            if buy_signals:
                buy_signals.sort(key=lambda x: x['rsi'])
                for signal in buy_signals:
                    plan = signal['plan']
                    content += f"""
--------------------------------------------------
股票代码: {signal['symbol']}
当前价格: {signal['price']:.2f}
RSI指标: {signal['rsi']:.1f}
信号强度: {plan['strength']}

【交易计划】
  买入价格: {plan['buy_price']:.2f}
  买入数量: {plan['buy_quantity']}股
  投入资金: {plan['invest_amount']:,.2f}元
  仓位比例: {plan['position_pct']*100:.0f}%
  
  止损价格: {plan['stop_loss_price']:.2f}（下跌{plan['stop_loss_pct']*100:.0f}%）
  止盈价格: {plan['take_profit_price']:.2f}（上涨{plan['take_profit_pct']*100:.0f}%）
  
  止损金额: {plan['buy_quantity'] * (plan['buy_price'] - plan['stop_loss_price']):,.2f}元
  止盈金额: {plan['buy_quantity'] * (plan['take_profit_price'] - plan['buy_price']):,.2f}元

【操作步骤】
  1. 打开手机国金证券APP
  2. 搜索股票代码 {signal['symbol']}
  3. 以 {plan['buy_price']:.2f} 元买入 {plan['buy_quantity']} 股
  4. 设置止损价: {plan['stop_loss_price']:.2f}
  5. 设置止盈价: {plan['take_profit_price']:.2f}
"""
            else:
                content += "\n无买入信号\n"
            
            content += f"""
==================================================

【卖出信号】（RSI超买）
"""
            if sell_signals:
                sell_signals.sort(key=lambda x: x['rsi'], reverse=True)
                for signal in sell_signals:
                    content += f"""
--------------------------------------------------
股票代码: {signal['symbol']}
当前价格: {signal['price']:.2f}
RSI指标: {signal['rsi']:.1f}

【操作建议】
  1. 打开手机国金证券APP
  2. 搜索股票代码 {signal['symbol']}
  3. 以 {signal['price']:.2f} 元卖出全部持仓
  4. 或设置止盈价: {signal['price'] * 1.05:.2f}（上涨5%）
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
项目名称: 量化交易系统
发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
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
