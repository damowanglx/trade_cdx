"""
邮件报警模块
发送交易信号和异常报警

使用方法：
    from monitor.email_alert import EmailAlert
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os


class EmailAlert:
    """邮件报警类"""
    
    def __init__(self, smtp_server='smtp.qq.com', smtp_port=587):
        """
        初始化邮件报警
        
        Args:
            smtp_server: SMTP服务器地址
            smtp_port: SMTP端口
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = None
        self.sender_password = None
        self.receiver_email = None
        
    def configure(self, sender_email, sender_password, receiver_email):
        """
        配置邮件参数
        
        Args:
            sender_email: 发送者邮箱
            sender_password: 邮箱授权码
            receiver_email: 接收者邮箱
        """
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.receiver_email = receiver_email
        
        print(f"邮件配置完成:")
        print(f"  发送者: {sender_email}")
        print(f"  接收者: {receiver_email}")
    
    def send_email(self, subject, content):
        """
        发送邮件
        
        Args:
            subject: 邮件主题
            content: 邮件内容
        """
        if not all([self.sender_email, self.sender_password, self.receiver_email]):
            print("错误: 邮件未配置")
            return False
        
        try:
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.receiver_email
            msg['Subject'] = subject
            
            # 添加内容
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
            
            # 连接SMTP服务器
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            
            # 发送邮件
            server.sendmail(self.sender_email, self.receiver_email, msg.as_string())
            server.quit()
            
            print(f"邮件发送成功: {subject}")
            return True
            
        except Exception as e:
            print(f"邮件发送失败: {e}")
            return False
    
    def send_trade_signal(self, signal_type, symbol, price, quantity, reason):
        """
        发送交易信号
        
        Args:
            signal_type: 信号类型（买入/卖出）
            symbol: 股票代码
            price: 价格
            quantity: 数量
            reason: 原因
        """
        subject = f"交易信号: {signal_type} {symbol}"
        
        content = f"""
交易信号通知
{'='*50}

时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
类型: {signal_type}
股票: {symbol}
价格: {price:.2f}
数量: {quantity}
原因: {reason}

{'='*50}
        """
        
        return self.send_email(subject, content)
    
    def send_risk_alert(self, alert_type, message):
        """
        发送风险报警
        
        Args:
            alert_type: 报警类型
            message: 报警信息
        """
        subject = f"风险报警: {alert_type}"
        
        content = f"""
风险报警通知
{'='*50}

时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
类型: {alert_type}
信息: {message}

{'='*50}
        """
        
        return self.send_email(subject, content)
    
    def send_daily_report(self, portfolio_value, daily_return, positions):
        """
        发送每日报告
        
        Args:
            portfolio_value: 组合市值
            daily_return: 日收益率
            positions: 持仓信息
        """
        subject = f"每日报告: {datetime.now().strftime('%Y-%m-%d')}"
        
        # 构建持仓信息
        positions_str = ""
        for symbol, info in positions.items():
            positions_str += f"  {symbol}: {info['quantity']}股 @ {info['price']:.2f}\n"
        
        content = f"""
每日投资报告
{'='*50}

日期: {datetime.now().strftime('%Y-%m-%d')}
组合市值: {portfolio_value:,.2f}
日收益率: {daily_return*100:.2f}%

持仓情况:
{positions_str if positions_str else '  空仓'}

{'='*50}
        """
        
        return self.send_email(subject, content)


# 使用示例
if __name__ == '__main__':
    # 创建邮件报警实例
    alert = EmailAlert()
    
    # 配置邮件（需要替换为真实信息）
    # alert.configure(
    #     sender_email='your_email@qq.com',
    #     sender_password='your_authorization_code',
    #     receiver_email='receiver@email.com'
    # )
    
    # 测试发送
    # alert.send_trade_signal(
    #     signal_type='买入',
    #     symbol='000001.SZ',
    #     price=10.50,
    #     quantity=1000,
    #     reason='RSI超卖'
    # )
    
    print("邮件报警模块已创建")
    print("使用前请配置邮箱信息")
