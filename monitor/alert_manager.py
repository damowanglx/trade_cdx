"""
完善版监控模块
支持邮件和微信报警

使用方法：
    from monitor.alert_manager import AlertManager
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import json


class AlertManager:
    """报警管理器"""
    
    def __init__(self):
        """初始化"""
        self.email_config = {
            'smtp_server': 'smtp.qq.com',
            'smtp_port': 587,
            'sender_email': None,
            'sender_password': None,
            'receiver_email': None,
        }
        
        self.wechat_config = {
            'webhook_url': None,  # 企业微信webhook
        }
        
        self.alert_history = []
    
    def configure_email(self, sender_email, sender_password, receiver_email):
        """配置邮件"""
        self.email_config['sender_email'] = sender_email
        self.email_config['sender_password'] = sender_password
        self.email_config['receiver_email'] = receiver_email
        print(f"邮件配置完成: {sender_email} -> {receiver_email}")
    
    def configure_wechat(self, webhook_url):
        """配置企业微信"""
        self.wechat_config['webhook_url'] = webhook_url
        print(f"企业微信配置完成")
    
    def send_email(self, subject, content):
        """发送邮件"""
        if not all([self.email_config['sender_email'], 
                   self.email_config['sender_password'],
                   self.email_config['receiver_email']]):
            print("邮件未配置")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = self.email_config['receiver_email']
            msg['Subject'] = subject
            
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], 
                                self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['sender_email'], 
                        self.email_config['sender_password'])
            server.sendmail(self.email_config['sender_email'],
                          self.email_config['receiver_email'],
                          msg.as_string())
            server.quit()
            
            print(f"邮件发送成功: {subject}")
            return True
        except Exception as e:
            print(f"邮件发送失败: {e}")
            return False
    
    def send_wechat(self, content):
        """发送企业微信"""
        if not self.wechat_config['webhook_url']:
            print("企业微信未配置")
            return False
        
        try:
            import requests
            data = {
                "msgtype": "text",
                "text": {
                    "content": content
                }
            }
            response = requests.post(self.wechat_config['webhook_url'], 
                                   json=data)
            if response.status_code == 200:
                print("企业微信发送成功")
                return True
            else:
                print(f"企业微信发送失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"企业微信发送失败: {e}")
            return False
    
    def send_alert(self, alert_type, title, content, channels=['email']):
        """发送报警"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 构建完整内容
        full_content = f"""
{alert_type}报警
{'='*50}
时间: {timestamp}
标题: {title}
{'='*50}

{content}

{'='*50}
        """
        
        # 记录历史
        self.alert_history.append({
            'timestamp': timestamp,
            'type': alert_type,
            'title': title,
            'content': content,
        })
        
        # 发送到各渠道
        results = {}
        
        if 'email' in channels:
            results['email'] = self.send_email(f"[{alert_type}] {title}", full_content)
        
        if 'wechat' in channels:
            results['wechat'] = self.send_wechat(full_content)
        
        return results
    
    def send_trade_signal(self, signal_type, symbol, price, quantity, reason):
        """发送交易信号"""
        content = f"""
交易详情:
  类型: {signal_type}
  股票: {symbol}
  价格: {price:.2f}
  数量: {quantity}
  原因: {reason}
        """
        
        return self.send_alert('交易信号', f'{signal_type} {symbol}', content)
    
    def send_risk_alert(self, risk_type, message, current_value=None, threshold=None):
        """发送风险报警"""
        content = f"""
风险详情:
  类型: {risk_type}
  信息: {message}
"""
        if current_value is not None:
            content += f"  当前值: {current_value}\n"
        if threshold is not None:
            content += f"  阈值: {threshold}\n"
        
        return self.send_alert('风险报警', risk_type, content)
    
    def send_daily_report(self, portfolio_value, daily_return, positions, 
                         total_return=None, max_drawdown=None):
        """发送每日报告"""
        # 构建持仓信息
        positions_str = ""
        for symbol, info in positions.items():
            positions_str += f"  {symbol}: {info.get('quantity', 0)}股 @ {info.get('price', 0):.2f}\n"
        
        content = f"""
投资报告:
  日期: {datetime.now().strftime('%Y-%m-%d')}
  组合市值: {portfolio_value:,.2f}
  日收益率: {daily_return*100:.2f}%
"""
        if total_return is not None:
            content += f"  总收益率: {total_return*100:.2f}%\n"
        if max_drawdown is not None:
            content += f"  最大回撤: {max_drawdown*100:.2f}%\n"
        
        content += f"""
持仓情况:
{positions_str if positions_str else '  空仓'}
        """
        
        return self.send_alert('每日报告', '投资组合报告', content)
    
    def get_alert_history(self, limit=10):
        """获取报警历史"""
        return self.alert_history[-limit:]


# 使用示例
if __name__ == '__main__':
    alert = AlertManager()
    
    # 配置邮件（需要替换为真实信息）
    # alert.configure_email(
    #     sender_email='your_email@qq.com',
    #     sender_password='your_authorization_code',
    #     receiver_email='receiver@email.com'
    # )
    
    # 配置企业微信
    # alert.configure_wechat('https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx')
    
    print("监控模块已创建")
    print("使用前请配置邮箱或企业微信")

class RealtimeMonitor:
    """实时监控类"""
    
    def __init__(self, alert_manager):
        """
        初始化实时监控
        
        Args:
            alert_manager: 报警管理器实例
        """
        self.alert_manager = alert_manager
        self.is_running = False
        self监控间隔 = 60  # 默认60秒
        
    def start(self, interval=60):
        """启动实时监控"""
        self监控间隔 = interval
        self.is_running = True
        print(f"实时监控已启动，监控间隔: {interval}秒")
        
    def stop(self):
        """停止实时监控"""
        self.is_running = False
        print("实时监控已停止")
        
    def check_portfolio(self, portfolio_value, positions):
        """检查组合状态"""
        # 检查组合价值变化
        # 检查持仓集中度
        # 检查风险指标
        pass
        
    def send实时报告(self, portfolio_value, daily_return, positions):
        """发送实时报告"""
        if self.alert_manager:
            self.alert_manager.send_daily_report(
                portfolio_value=portfolio_value,
                daily_return=daily_return,
                positions=positions
            )
