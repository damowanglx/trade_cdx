"""
风险控制模块
VaR风险价值、压力测试、风险监控

使用方法：
    from risk.risk_control import RiskController
"""

import numpy as np
import pandas as pd


class RiskController:
    """风险控制器"""
    
    def __init__(self, max_drawdown=0.15, max_position=0.30, 
                 stop_loss=0.10, take_profit=0.30):
        """
        初始化
        
        Args:
            max_drawdown: 最大回撤限制
            max_position: 最大仓位限制
            stop_loss: 止损比例
            take_profit: 止盈比例
        """
        self.max_drawdown = max_drawdown
        self.max_position = max_position
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        
        self.peak_value = 0
        self.daily_returns = []
        
    def update_peak(self, current_value):
        """更新峰值"""
        if current_value > self.peak_value:
            self.peak_value = current_value
    
    def calculate_drawdown(self, current_value):
        """计算当前回撤"""
        if self.peak_value <= 0:
            return 0
        return (self.peak_value - current_value) / self.peak_value
    
    def check_drawdown_limit(self, current_value):
        """检查回撤是否超限"""
        drawdown = self.calculate_drawdown(current_value)
        return drawdown <= self.max_drawdown
    
    def check_position_limit(self, position_value, total_value):
        """检查仓位是否超限"""
        if total_value <= 0:
            return False
        position_pct = position_value / total_value
        return position_pct <= self.max_position
    
    def calculate_stop_loss_price(self, buy_price):
        """计算止损价格"""
        return buy_price * (1 - self.stop_loss)
    
    def calculate_take_profit_price(self, buy_price):
        """计算止盈价格"""
        return buy_price * (1 + self.take_profit)
    
    def check_stop_loss(self, buy_price, current_price):
        """检查是否触发止损"""
        stop_price = self.calculate_stop_loss_price(buy_price)
        return current_price <= stop_price
    
    def check_take_profit(self, buy_price, current_price):
        """检查是否触发止盈"""
        profit_price = self.calculate_take_profit_price(buy_price)
        return current_price >= profit_price
    
    def calculate_var(self, returns, confidence=0.95):
        """计算VaR风险价值"""
        if len(returns) == 0:
            return 0
        
        # 使用历史模拟法
        sorted_returns = np.sort(returns)
        index = int(len(sorted_returns) * (1 - confidence))
        
        if index < 0:
            index = 0
        
        return abs(sorted_returns[index])
    
    def calculate_max_drawdown(self, values):
        """计算最大回撤"""
        if len(values) == 0:
            return 0
        
        peak = values.cummax()
        drawdown = (values - peak) / peak
        return drawdown.min()
    
    def calculate_sharpe_ratio(self, returns, risk_free_rate=0.001):
        """计算夏普比率"""
        if len(returns) == 0:
            return 0
        
        excess_returns = returns - risk_free_rate / 252
        return excess_returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
    
    def calculate_calmar_ratio(self, returns, max_drawdown):
        """计算卡尔玛比率"""
        if max_drawdown == 0:
            return 0
        
        annual_return = returns.mean() * 252
        return annual_return / abs(max_drawdown)
    
    def generate_risk_report(self, portfolio_value, returns, positions):
        """生成风险报告"""
        report = "=" * 60 + "\n"
        report += "风险控制报告\n"
        report += "=" * 60 + "\n\n"
        
        # 计算风险指标
        drawdown = self.calculate_drawdown(portfolio_value)
        var_95 = self.calculate_var(returns, 0.95)
        sharpe = self.calculate_sharpe_ratio(returns)
        
        report += f"当前组合价值: {portfolio_value:,.2f}\n"
        report += f"当前回撤: {drawdown*100:.2f}%\n"
        report += f"最大回撤限制: {self.max_drawdown*100:.2f}%\n"
        report += f"VaR (95%): {var_95*100:.2f}%\n"
        report += f"夏普比率: {sharpe:.2f}\n\n"
        
        # 检查风控状态
        report += "风控状态:\n"
        report += f"  回撤限制: {'通过' if self.check_drawdown_limit(portfolio_value) else '超限'}\n"
        
        # 持仓检查
        total_position = sum(p.get('value', 0) for p in positions.values())
        report += f"  仓位限制: {'通过' if self.check_position_limit(total_position, portfolio_value) else '超限'}\n"
        
        report += "\n" + "=" * 60
        
        return report
