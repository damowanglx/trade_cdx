"""
股票信号预警系统
监控股票池，触发信号时发送邮件通知

功能：
- 监控多只股票
- 计算RSI、MACD等指标
- 触发买入/卖出信号时发送邮件
- 用户收到通知后用手机APP下单

使用方法：
    python scripts/run_signal_alert.py
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, time
import time as time_module
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SignalGenerator:
    """信号生成器"""
    
    def __init__(self):
        """初始化"""
        # 股票池（扩大到30只）
        self.stock_pool = {
            # 银行股
            '000001': '平安银行',
            '600036': '招商银行',
            '601398': '工商银行',
            '601939': '建设银行',
            '601288': '农业银行',
            
            # 白酒股
            '600519': '贵州茅台',
            '000858': '五粮液',
            '000568': '泸州老窖',
            '002304': '洋河股份',
            
            # 科技股
            '300750': '宁德时代',
            '002594': '比亚迪',
            '300059': '东方财富',
            '002475': '立讯精密',
            
            # 医药股
            '600276': '恒瑞医药',
            '000538': '云南白药',
            '300760': '迈瑞医疗',
            
            # 消费股
            '000333': '美的集团',
            '000651': '格力电器',
            '603259': '药明康德',
            
            # 地产股
            '000002': '万科A',
            '001979': '招商蛇口',
            
            # 新能源
            '601012': '隆基绿能',
            '002459': '晶澳科技',
            
            # 证券股
            '600030': '中信证券',
            '601211': '国泰君安',
            
            # 保险股
            '601318': '中国平安',
            '601628': '中国人寿',
            
            # 其他蓝筹
            '600900': '长江电力',
            '601857': '中国石油',
            '600028': '中国石化',
        }
        
        # 策略参数
        self.rsi_period = 21
        self.rsi_oversold = 30
        self.rsi_overbought = 70
        
    def calculate_rsi(self, prices, period=14):
        """计算RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """计算MACD"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        dif = ema_fast - ema_slow
        dea = dif.ewm(span=signal).mean()
        macd = 2 * (dif - dea)
        return dif, dea, macd
    
    def calculate_ma(self, prices, period):
        """计算均线"""
        return prices.rolling(period).mean()
    
    def analyze_stock(self, symbol, data):
        """分析单只股票"""
        if len(data) < 30:
            return None
        
        close = data['close']
        
        # 计算指标
        rsi = self.calculate_rsi(close, self.rsi_period)
        dif, dea, macd = self.calculate_macd(close)
        ma5 = self.calculate_ma(close, 5)
        ma20 = self.calculate_ma(close, 20)
        
        # 获取最新值
        current_rsi = rsi.iloc[-1]
        current_dif = dif.iloc[-1]
        current_dea = dea.iloc[-1]
        prev_dif = dif.iloc[-2]
        prev_dea = dea.iloc[-2]
        current_ma5 = ma5.iloc[-1]
        current_ma20 = ma20.iloc[-1]
        current_price = close.iloc[-1]
        
        # 信号判断
        signals = []
        
        # RSI信号
        if current_rsi < self.rsi_oversold:
            signals.append({
                'type': 'buy',
                'reason': f'RSI超卖 ({current_rsi:.1f} < {self.rsi_oversold})',
                'strength': 'strong'
            })
        elif current_rsi > self.rsi_overbought:
            signals.append({
                'type': 'sell',
                'reason': f'RSI超买 ({current_rsi:.1f} > {self.rsi_overbought})',
                'strength': 'strong'
            })
        
        # MACD金叉/死叉
        if prev_dif < prev_dea and current_dif > current_dea:
            signals.append({
                'type': 'buy',
                'reason': 'MACD金叉',
                'strength': 'medium'
            })
        elif prev_dif > prev_dea and current_dif < current_dea:
            signals.append({
                'type': 'sell',
                'reason': 'MACD死叉',
                'strength': 'medium'
            })
        
        # 均线信号
        if current_ma5 > current_ma20:
            signals.append({
                'type': 'buy',
                'reason': 'MA5 > MA20（多头排列）',
                'strength': 'weak'
            })
        else:
            signals.append({
                'type': 'sell',
                'reason': 'MA5 < MA20（空头排列）',
                'strength': 'weak'
            })
        
        return {
            'symbol': symbol,
            'price': current_price,
            'rsi': current_rsi,
            'ma5': current_ma5,
            'ma20': current_ma20,
            'signals': signals,
            'timestamp': datetime.now()
        }


class AlertSender:
    """报警发送器"""
    
    def __init__(self):
        """初始化"""
        # 股票池（扩大到30只）
        self.stock_pool = {
            # 银行股
            '000001': '平安银行',
            '600036': '招商银行',
            '601398': '工商银行',
            '601939': '建设银行',
            '601288': '农业银行',
            
            # 白酒股
            '600519': '贵州茅台',
            '000858': '五粮液',
            '000568': '泸州老窖',
            '002304': '洋河股份',
            
            # 科技股
            '300750': '宁德时代',
            '002594': '比亚迪',
            '300059': '东方财富',
            '002475': '立讯精密',
            
            # 医药股
            '600276': '恒瑞医药',
            '000538': '云南白药',
            '300760': '迈瑞医疗',
            
            # 消费股
            '000333': '美的集团',
            '000651': '格力电器',
            '603259': '药明康德',
            
            # 地产股
            '000002': '万科A',
            '001979': '招商蛇口',
            
            # 新能源
            '601012': '隆基绿能',
            '002459': '晶澳科技',
            
            # 证券股
            '600030': '中信证券',
            '601211': '国泰君安',
            
            # 保险股
            '601318': '中国平安',
            '601628': '中国人寿',
            
            # 其他蓝筹
            '600900': '长江电力',
            '601857': '中国石油',
            '600028': '中国石化',
        }
        
        # 邮箱配置
        self.email_config = {
            'smtp_server': 'smtp.163.com',
            'smtp_port': 465,
            'sender_email': 'damowang123lx@163.com',
            'sender_password': 'GXrpVgWngzGxpTkb',
            'receiver_email': 'damowang123lx@163.com',
        }
        
    def send_email(self, subject, content):
        """发送邮件"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = self.email_config['receiver_email']
            msg['Subject'] = subject
            
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
            
            server = smtplib.SMTP_SSL(
                self.email_config['smtp_server'], 
                self.email_config['smtp_port']
            )
            server.login(
                self.email_config['sender_email'],
                self.email_config['sender_password']
            )
            server.sendmail(
                self.email_config['sender_email'],
                self.email_config['receiver_email'],
                msg.as_string()
            )
            server.quit()
            
            return True
        except Exception as e:
            print(f"邮件发送失败: {e}")
            return False
    
    def send_signal_alert(self, signal_info):
        """发送信号报警"""
        symbol = signal_info['symbol']
        price = signal_info['price']
        rsi = signal_info['rsi']
        signals = signal_info['signals']
        
        # 获取股票名称
        stock_name = self.stock_pool.get(symbol, symbol)
        
        # 找出最强信号
        buy_signals = [s for s in signals if s['type'] == 'buy']
        sell_signals = [s for s in signals if s['type'] == 'sell']
        
        if buy_signals:
            signal_type = '买入'
            reasons = [s['reason'] for s in buy_signals]
        elif sell_signals:
            signal_type = '卖出'
            reasons = [s['reason'] for s in sell_signals]
        else:
            return False
        
        # 邮件主题
        subject = f"[量化交易] {signal_type} {symbol}-{stock_name} @ {price:.2f}"
        
        # 邮件内容
        content = f"""==================================================
量化交易信号预警系统
==================================================

项目: Quant Trading System v1.0 (量化交易系统)
策略: RSI + MACD + 均线
==================================================

【交易信号】

时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
股票代码: {symbol}
股票名称: {stock_name}
信号类型: {signal_type}
当前价格: {price:.2f}
RSI指标: {rsi:.1f}

【信号原因】
"""
        for reason in reasons:
            content += f"  - {reason}\n"
        
        content += f"""
【操作建议】
"""
        if signal_type == '买入':
            content += """  1. 确认信号有效性
  2. 用手机APP下单买入
  3. 建议仓位：20-30%
  4. 设置止损：-10%
  5. 设置止盈：+30%
"""
        else:
            content += """  1. 确认信号有效性
  2. 用手机APP下单卖出
  3. 清仓或减仓
  4. 记录交易
"""
        
        content += f"""
【风险提示】
  - 以上信号仅供参考
  - 请根据自己的判断操作
  - 控制好仓位和风险

==================================================
消息来源: Quant Trading System v1.0
项目名称: 量化交易系统
发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
自动发送，请勿回复
==================================================
"""
        
        return self.send_email(subject, content)


def get_stock_data(symbol, days=60):
    """获取股票数据"""
    import baostock as bs
    
    try:
        lg = bs.login()
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - pd.Timedelta(days=days*2)).strftime('%Y-%m-%d')
        
        prefix = 'sz' if symbol.startswith('0') or symbol.startswith('3') else 'sh'
        
        rs = bs.query_history_k_data_plus(
            f'{prefix}.{symbol}',
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
            
            if data_list:
                df = pd.DataFrame(data_list, columns=rs.fields)
                df['date'] = pd.to_datetime(df['date'])
                for col in ['open', 'high', 'low', 'close', 'volume', 'amount']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                df = df.set_index('date')
                df = df.sort_index()
                return df
        
        bs.logout()
        return pd.DataFrame()
        
    except Exception as e:
        print(f"获取数据失败 {symbol}: {e}")
        return pd.DataFrame()


def main():
    """主函数"""
    print("="*60)
    print("股票信号预警系统")
    print("="*60)
    print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"项目: Quant Trading System v1.0")
    print()
    
    # 创建信号生成器
    generator = SignalGenerator()
    alert_sender = AlertSender()
    
    # 监控股票池
    print("监控股票池:")
    for symbol, name in generator.stock_pool.items():
        print(f"  - {symbol} {name}")
    print()
    
    # 分析每只股票
    print("分析股票信号...")
    print("-"*60)
    
    alert_count = 0
    
    for symbol, name in generator.stock_pool.items():
        print(f"\n分析 {name}({symbol})...")
        
        # 获取数据
        data = get_stock_data(symbol)
        
        if data.empty:
            print(f"  获取数据失败")
            continue
        
        # 分析信号
        result = generator.analyze_stock(symbol, data)
        
        if result:
            print(f"  当前价格: {result['price']:.2f}")
            print(f"  RSI: {result['rsi']:.1f}")
            print(f"  MA5: {result['ma5']:.2f}")
            print(f"  MA20: {result['ma20']:.2f}")
            
            # 显示信号
            if result['signals']:
                print(f"  信号:")
                for signal in result['signals']:
                    print(f"    - {signal['type'].upper()}: {signal['reason']}")
                
                # 发送报警
                has_strong_signal = any(s['strength'] == 'strong' for s in result['signals'])
                if has_strong_signal:
                    print(f"  >>> 发送报警邮件 <<<")
                    success = alert_sender.send_signal_alert(result)
                    if success:
                        print(f"  邮件发送成功")
                        alert_count += 1
                    else:
                        print(f"  邮件发送失败")
            else:
                print(f"  无信号")
    
    print("\n" + "="*60)
    print(f"分析完成！发送 {alert_count} 个报警")
    print("="*60)
    
    print("\n提示：")
    print("  - 收到邮件后，用手机APP下单")
    print("  - 控制好仓位（建议20-30%）")
    print("  - 设置止损（-10%）和止盈（+30%）")


if __name__ == '__main__':
    main()

