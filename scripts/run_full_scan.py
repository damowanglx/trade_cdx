"""
全量A股信号筛选系统
筛选所有活跃股票的信号

功能：
- 扫描全量A股（5000+只）
- 过滤活跃股票（成交量、换手率）
- 计算RSI、MACD等指标
- 发送符合条件的信号邮件

使用方法：
    python scripts/run_full_scan.py
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


class FullStockScanner:
    """全量股票扫描器"""
    
    def __init__(self):
        """初始化"""
        # 策略参数
        self.rsi_period = 21
        self.rsi_oversold = 30
        self.rsi_overbought = 70
        
        # 活跃度过滤参数
        self.min_volume = 5000000      # 最小成交量（500万股）
        self.min_amount = 50000000     # 最小成交额（5000万）
        self.min_price = 5.0           # 最低价格
        self.max_price = 500.0         # 最高价格
        
    def get_all_stocks(self):
        """获取所有A股股票"""
        print("获取A股股票列表...")
        
        lg = bs.login()
        
        rs = bs.query_stock_basic()
        if rs.error_code != '0':
            print(f"获取股票列表失败: {rs.error_msg}")
            bs.logout()
            return []
        
        data_list = []
        while (rs.error_code == '0') and rs.next():
            data_list.append(rs.get_row_data())
        
        df = pd.DataFrame(data_list, columns=rs.fields)
        
        # 只保留A股
        a_stocks = df[(df['type'] == '1') & (df['status'] == '1')]
        
        bs.logout()
        
        stocks = a_stocks['code'].tolist()
        print(f"获取到 {len(stocks)} 只A股股票")
        
        return stocks
    
    def get_stock_data(self, symbol, days=60):
        """获取股票数据"""
        try:
            lg = bs.login()
            
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - pd.Timedelta(days=days*2)).strftime('%Y-%m-%d')
            
            rs = bs.query_history_k_data_plus(
                symbol,
                "date,open,high,low,close,volume,amount,turn",
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
                    for col in ['open', 'high', 'low', 'close', 'volume', 'amount', 'turn']:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    df = df.set_index('date')
                    df = df.sort_index()
                    bs.logout()
                    return df
            
            bs.logout()
            return pd.DataFrame()
            
        except Exception as e:
            return pd.DataFrame()
    
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
        return dif, dea
    
    def check_activity(self, df):
        """检查股票活跃度"""
        if len(df) < 5:
            return False, "数据不足"
        
        # 检查最近5天的平均成交量和成交额
        recent = df.tail(5)
        avg_volume = recent['volume'].mean()
        avg_amount = recent['amount'].mean()
        current_price = recent['close'].iloc[-1]
        
        if avg_volume < self.min_volume:
            return False, f"成交量过低: {avg_volume:,.0f}"
        
        if avg_amount < self.min_amount:
            return False, f"成交额过低: {avg_amount:,.0f}"
        
        if current_price < self.min_price:
            return False, f"价格过低: {current_price:.2f}"
        
        if current_price > self.max_price:
            return False, f"价格过高: {current_price:.2f}"
        
        return True, "活跃"
    
    def analyze_stock(self, symbol, df):
        """分析单只股票"""
        if len(df) < 30:
            return None
        
        close = df['close']
        
        # 计算指标
        rsi = self.calculate_rsi(close, self.rsi_period)
        dif, dea = self.calculate_macd(close)
        ma5 = close.rolling(5).mean()
        ma20 = close.rolling(20).mean()
        
        # 获取最新值
        current_rsi = rsi.iloc[-1]
        current_dif = dif.iloc[-1]
        current_dea = dea.iloc[-1]
        prev_dif = dif.iloc[-2]
        prev_dea = dea.iloc[-2]
        current_price = close.iloc[-1]
        current_volume = df['volume'].iloc[-1]
        current_amount = df['amount'].iloc[-1]
        
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
        
        # MACD信号
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
        
        return {
            'symbol': symbol,
            'price': current_price,
            'rsi': current_rsi,
            'volume': current_volume,
            'amount': current_amount,
            'signals': signals,
            'timestamp': datetime.now()
        }
    
    def scan_all_stocks(self, max_stocks=1000):
        """扫描所有股票"""
        print("="*60)
        print("全量A股信号扫描")
        print("="*60)
        print(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 获取所有股票
        all_stocks = self.get_all_stocks()
        
        # 限制扫描数量
        if len(all_stocks) > max_stocks:
            print(f"限制扫描数量: {max_stocks}")
            all_stocks = all_stocks[:max_stocks]
        
        print(f"开始扫描 {len(all_stocks)} 只股票...")
        print()
        
        # 扫描结果
        buy_signals = []
        sell_signals = []
        active_stocks = []
        error_count = 0
        
        for i, symbol in enumerate(all_stocks):
            if (i + 1) % 100 == 0:
                print(f"进度: {i+1}/{len(all_stocks)} ({(i+1)/len(all_stocks)*100:.1f}%)")
            
            # 获取数据
            df = self.get_stock_data(symbol)
            
            if df.empty:
                error_count += 1
                continue
            
            # 检查活跃度
            is_active, reason = self.check_activity(df)
            
            if not is_active:
                continue
            
            active_stocks.append(symbol)
            
            # 分析信号
            result = self.analyze_stock(symbol, df)
            
            if result and result['signals']:
                # 找出强信号
                strong_buy = [s for s in result['signals'] if s['type'] == 'buy' and s['strength'] == 'strong']
                strong_sell = [s for s in result['signals'] if s['type'] == 'sell' and s['strength'] == 'strong']
                
                if strong_buy:
                    buy_signals.append(result)
                elif strong_sell:
                    sell_signals.append(result)
        
        # 打印结果
        print("\n" + "="*60)
        print("扫描结果")
        print("="*60)
        print(f"扫描股票数: {len(all_stocks)}")
        print(f"活跃股票数: {len(active_stocks)}")
        print(f"数据错误: {error_count}")
        print(f"买入信号: {len(buy_signals)} 只")
        print(f"卖出信号: {len(sell_signals)} 只")
        
        # 打印买入信号
        if buy_signals:
            print("\n【买入信号】")
            print("-"*80)
            print(f"{'代码':<10} {'价格':<10} {'RSI':<8} {'成交量':<15} {'成交额':<15}")
            print("-"*80)
            
            # 按RSI排序
            buy_signals.sort(key=lambda x: x['rsi'])
            
            for signal in buy_signals:
                symbol = signal['symbol']
                price = signal['price']
                rsi = signal['rsi']
                volume = signal['volume']
                amount = signal['amount']
                reasons = [s['reason'] for s in signal['signals'] if s['type'] == 'buy']
                
                print(f"{symbol:<10} {price:<10.2f} {rsi:<8.1f} {volume:<15,.0f} {amount:<15,.0f}")
                for reason in reasons:
                    print(f"  - {reason}")
                print()
        
        # 打印卖出信号
        if sell_signals:
            print("\n【卖出信号】")
            print("-"*80)
            print(f"{'代码':<10} {'价格':<10} {'RSI':<8} {'成交量':<15} {'成交额':<15}")
            print("-"*80)
            
            # 按RSI排序
            sell_signals.sort(key=lambda x: x['rsi'], reverse=True)
            
            for signal in sell_signals:
                symbol = signal['symbol']
                price = signal['price']
                rsi = signal['rsi']
                volume = signal['volume']
                amount = signal['amount']
                reasons = [s['reason'] for s in signal['signals'] if s['type'] == 'sell']
                
                print(f"{symbol:<10} {price:<10.2f} {rsi:<8.1f} {volume:<15,.0f} {amount:<15,.0f}")
                for reason in reasons:
                    print(f"  - {reason}")
                print()
        
        return buy_signals, sell_signals


class EmailSender:
    """邮件发送器"""
    
    def __init__(self):
        """初始化"""
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
    
    def send_full_scan_report(self, buy_signals, sell_signals):
        """发送全量扫描报告"""
        subject = f"[量化交易] 全量扫描报告 - 买入{len(buy_signals)}只 卖出{len(sell_signals)}只"
        
        content = f"""==================================================
量化交易全量扫描报告
==================================================

项目: Quant Trading System v1.0 (量化交易系统)
策略: RSI + MACD
扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

==================================================

【买入信号】（RSI超卖）
"""
        if buy_signals:
            # 按RSI排序
            buy_signals.sort(key=lambda x: x['rsi'])
            
            for signal in buy_signals:
                symbol = signal['symbol']
                price = signal['price']
                rsi = signal['rsi']
                volume = signal['volume']
                amount = signal['amount']
                
                content += f"""
股票代码: {symbol}
当前价格: {price:.2f}
RSI指标: {rsi:.1f}
成交量: {volume:,.0f}
成交额: {amount:,.0f}
信号原因: RSI超卖 ({rsi:.1f} < 30)
操作建议: 可考虑买入，仓位20-30%，止损-10%，止盈+30%
"""
        else:
            content += "\n无买入信号\n"
        
        content += f"""
==================================================

【卖出信号】（RSI超买）
"""
        if sell_signals:
            # 按RSI排序
            sell_signals.sort(key=lambda x: x['rsi'], reverse=True)
            
            for signal in sell_signals:
                symbol = signal['symbol']
                price = signal['price']
                rsi = signal['rsi']
                volume = signal['volume']
                amount = signal['amount']
                
                content += f"""
股票代码: {symbol}
当前价格: {price:.2f}
RSI指标: {rsi:.1f}
成交量: {volume:,.0f}
成交额: {amount:,.0f}
信号原因: RSI超买 ({rsi:.1f} > 70)
操作建议: 考虑卖出或减仓
"""
        else:
            content += "\n无卖出信号\n"
        
        content += f"""
==================================================
风险提示:
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


def main():
    """主函数"""
    # 创建扫描器
    scanner = FullStockScanner()
    email_sender = EmailSender()
    
    # 扫描股票（限制500只，避免超时）
    buy_signals, sell_signals = scanner.scan_all_stocks(max_stocks=100)
    
    # 发送邮件
    if buy_signals or sell_signals:
        print("\n发送邮件报告...")
        success = email_sender.send_full_scan_report(buy_signals, sell_signals)
        if success:
            print("邮件发送成功！")
        else:
            print("邮件发送失败！")
    else:
        print("\n无信号，不发送邮件")
    
    print("\n" + "="*60)
    print("全量扫描完成！")
    print("="*60)


if __name__ == '__main__':
    main()

