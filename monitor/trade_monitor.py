"""
监控模块
监控策略运行状态，记录交易日志，异常报警

功能：
- 交易日志记录
- 绩效统计
- 异常报警
- 实时监控
"""

import json
import os
from datetime import datetime

from loguru import logger


class TradeLogger:
    """交易日志记录器"""
    
    def __init__(self, log_dir='logs'):
        """
        初始化
        
        Args:
            log_dir: 日志目录
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # 配置loguru
        log_file = os.path.join(log_dir, 'trade_{time}.log')
        logger.add(log_file, rotation='1 day', retention='30 days')
        
        self.trades = []
        self.daily_stats = []
        
    def log_trade(self, trade_info):
        """
        记录交易
        
        Args:
            trade_info: dict，包含交易信息
                - date: 交易日期
                - symbol: 股票代码
                - action: 买卖方向（buy/sell）
                - price: 成交价格
                - size: 成交数量
                - cost: 交易成本
                - commission: 手续费
                - reason: 交易原因
        """
        self.trades.append(trade_info)
        
        # 写入日志
        logger.info(f"交易记录: {trade_info}")
        
        # 保存到文件
        self.save_trades()
    
    def log_daily_stats(self, stats):
        """
        记录每日统计
        
        Args:
            stats: dict，包含统计信息
                - date: 日期
                - portfolio_value: 组合市值
                - cash: 现金
                - positions: 持仓
                - daily_return: 日收益率
                - total_return: 总收益率
                - max_drawdown: 最大回撤
        """
        self.daily_stats.append(stats)
        
        # 写入日志
        logger.info(f"每日统计: {stats}")
        
        # 保存到文件
        self.save_daily_stats()
    
    def save_trades(self):
        """保存交易记录到文件"""
        trades_file = os.path.join(self.log_dir, 'trades.json')
        with open(trades_file, 'w', encoding='utf-8') as f:
            json.dump(self.trades, f, ensure_ascii=False, indent=2, default=str)
    
    def save_daily_stats(self):
        """保存每日统计到文件"""
        stats_file = os.path.join(self.log_dir, 'daily_stats.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.daily_stats, f, ensure_ascii=False, indent=2, default=str)
    
    def get_trade_summary(self):
        """获取交易摘要"""
        if not self.trades:
            return {}
        
        total_trades = len(self.trades)
        buy_trades = [t for t in self.trades if t.get('action') == 'buy']
        sell_trades = [t for t in self.trades if t.get('action') == 'sell']
        
        total_commission = sum(t.get('commission', 0) for t in self.trades)
        total_profit = sum(t.get('profit', 0) for t in self.trades)
        
        return {
            'total_trades': total_trades,
            'buy_trades': len(buy_trades),
            'sell_trades': len(sell_trades),
            'total_commission': total_commission,
            'total_profit': total_profit,
            'avg_profit_per_trade': total_profit / total_trades if total_trades > 0 else 0
        }
    
    def get_performance_report(self):
        """获取绩效报告"""
        if not self.daily_stats:
            return {}
        
        # 计算收益率
        values = [s.get('portfolio_value', 0) for s in self.daily_stats]
        returns = []
        for i in range(1, len(values)):
            if values[i-1] > 0:
                returns.append((values[i] - values[i-1]) / values[i-1])
        
        import numpy as np
        returns = np.array(returns)
        
        # 计算指标
        total_return = (values[-1] - values[0]) / values[0] if values[0] > 0 else 0
        annual_return = total_return * 252 / len(values) if len(values) > 0 else 0
        volatility = np.std(returns) * np.sqrt(252) if len(returns) > 0 else 0
        sharpe_ratio = annual_return / volatility if volatility > 0 else 0
        
        # 计算最大回撤
        max_drawdown = 0
        peak = values[0]
        for value in values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'trading_days': len(values),
            'start_value': values[0],
            'end_value': values[-1]
        }


class AlertManager:
    """报警管理器"""
    
    def __init__(self, alert_thresholds=None):
        """
        初始化
        
        Args:
            alert_thresholds: dict，报警阈值
                - max_drawdown: 最大回撤阈值
                - daily_loss: 每日亏损阈值
                - position_concentration: 持仓集中度阈值
        """
        self.alert_thresholds = alert_thresholds or {
            'max_drawdown': 0.15,
            'daily_loss': 0.03,
            'position_concentration': 0.5
        }
        self.alerts = []
        
    def check_drawdown(self, current_drawdown):
        """检查回撤报警"""
        if current_drawdown > self.alert_thresholds['max_drawdown']:
            alert = {
                'type': 'drawdown',
                'message': f'回撤超限: {current_drawdown:.2%}',
                'threshold': self.alert_thresholds['max_drawdown'],
                'timestamp': datetime.now().isoformat()
            }
            self.alerts.append(alert)
            logger.warning(f"报警: {alert['message']}")
            return True
        return False
    
    def check_daily_loss(self, daily_return):
        """检查每日亏损报警"""
        if daily_return < -self.alert_thresholds['daily_loss']:
            alert = {
                'type': 'daily_loss',
                'message': f'每日亏损超限: {daily_return:.2%}',
                'threshold': self.alert_thresholds['daily_loss'],
                'timestamp': datetime.now().isoformat()
            }
            self.alerts.append(alert)
            logger.warning(f"报警: {alert['message']}")
            return True
        return False
    
    def check_position_concentration(self, position_pct):
        """检查持仓集中度报警"""
        if position_pct > self.alert_thresholds['position_concentration']:
            alert = {
                'type': 'position_concentration',
                'message': f'持仓集中度超限: {position_pct:.2%}',
                'threshold': self.alert_thresholds['position_concentration'],
                'timestamp': datetime.now().isoformat()
            }
            self.alerts.append(alert)
            logger.warning(f"报警: {alert['message']}")
            return True
        return False
    
    def get_alerts(self):
        """获取所有报警"""
        return self.alerts
    
    def clear_alerts(self):
        """清除报警"""
        self.alerts = []


class PerformanceAnalyzer:
    """绩效分析器"""
    
    @staticmethod
    def calculate_metrics(returns):
        """
        计算绩效指标
        
        Args:
            returns: 收益率序列
            
        Returns:
            dict: 绩效指标
        """
        import numpy as np
        returns = np.array(returns)
        
        metrics = {
            'total_return': np.prod(1 + returns) - 1,
            'annual_return': np.mean(returns) * 252,
            'volatility': np.std(returns) * np.sqrt(252),
            'sharpe_ratio': (np.mean(returns) * 252) / (np.std(returns) * np.sqrt(252)) if np.std(returns) > 0 else 0,
            'max_drawdown': PerformanceAnalyzer.calculate_max_drawdown(returns),
            'win_rate': np.sum(returns > 0) / len(returns) if len(returns) > 0 else 0,
            'profit_factor': abs(np.sum(returns[returns > 0]) / np.sum(returns[returns < 0])) if np.sum(returns[returns < 0]) != 0 else float('inf'),
            'avg_win': np.mean(returns[returns > 0]) if np.sum(returns > 0) > 0 else 0,
            'avg_loss': np.mean(returns[returns < 0]) if np.sum(returns < 0) > 0 else 0,
            'max_win': np.max(returns) if len(returns) > 0 else 0,
            'max_loss': np.min(returns) if len(returns) > 0 else 0,
            'trading_days': len(returns)
        }
        
        return metrics
    
    @staticmethod
    def calculate_max_drawdown(returns):
        """计算最大回撤"""
        import numpy as np
        cumulative = np.cumprod(1 + returns)
        peak = np.maximum.accumulate(cumulative)
        drawdown = (peak - cumulative) / peak
        return np.max(drawdown) if len(drawdown) > 0 else 0
    
    @staticmethod
    def generate_report(metrics):
        """生成绩效报告"""
        report = "=" * 60 + "\n"
        report += "绩效报告\n"
        report += "=" * 60 + "\n\n"
        
        report += "收益指标:\n"
        report += f"  总收益率: {metrics['total_return']:.2%}\n"
        report += f"  年化收益率: {metrics['annual_return']:.2%}\n"
        report += f"  年化波动率: {metrics['volatility']:.2%}\n"
        report += f"  夏普比率: {metrics['sharpe_ratio']:.2f}\n\n"
        
        report += "风险指标:\n"
        report += f"  最大回撤: {metrics['max_drawdown']:.2%}\n"
        report += f"  胜率: {metrics['win_rate']:.2%}\n"
        report += f"  盈亏比: {metrics['profit_factor']:.2f}\n\n"
        
        report += "交易统计:\n"
        report += f"  平均盈利: {metrics['avg_win']:.4f}\n"
        report += f"  平均亏损: {metrics['avg_loss']:.4f}\n"
        report += f"  最大单日盈利: {metrics['max_win']:.4f}\n"
        report += f"  最大单日亏损: {metrics['max_loss']:.4f}\n"
        report += f"  交易天数: {metrics['trading_days']}\n"
        
        report += "=" * 60
        
        return report

def send_email_alert(subject, content, email_config=None):
    """
    发送邮件报警
    
    Args:
        subject: 邮件主题
        content: 邮件内容
        email_config: 邮箱配置
    """
    if email_config is None:
        # 尝试从配置文件加载
        try:
            from config.email_config import EMAIL_CONFIG
            email_config = EMAIL_CONFIG
        except ImportError:
            print("邮箱配置未找到")
            return False
    
    try:
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        
        msg = MIMEMultipart()
        msg['From'] = email_config['sender_email']
        msg['To'] = email_config['receiver_email']
        msg['Subject'] = subject
        
        msg.attach(MIMEText(content, 'plain', 'utf-8'))
        
        server = smtplib.SMTP_SSL(email_config['smtp_server'], email_config['smtp_port'])
        server.login(email_config['sender_email'], email_config['sender_password'])
        server.sendmail(email_config['sender_email'], email_config['receiver_email'], msg.as_string())
        server.quit()
        
        print(f"邮件发送成功: {subject}")
        return True
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False
