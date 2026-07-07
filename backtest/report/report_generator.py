"""
回测报告生成器
生成详细的回测报告
"""

import pandas as pd
import numpy as np
from datetime import datetime


class ReportGenerator:
    """回测报告生成器"""
    
    def __init__(self):
        pass
    
    def calculate_metrics(self, portfolio_values, benchmark_values=None):
        """计算绩效指标"""
        returns = portfolio_values.pct_change().dropna()
        
        total_return = (portfolio_values.iloc[-1] / portfolio_values.iloc[0]) - 1
        trading_days = len(returns)
        annual_return = (1 + total_return) ** (252 / trading_days) - 1 if trading_days > 0 else 0
        volatility = returns.std() * np.sqrt(252)
        sharpe_ratio = annual_return / volatility if volatility > 0 else 0
        
        peak = portfolio_values.cummax()
        drawdown = (portfolio_values - peak) / peak
        max_drawdown = drawdown.min()
        
        win_rate = (returns > 0).sum() / len(returns) if len(returns) > 0 else 0
        
        avg_win = returns[returns > 0].mean() if len(returns[returns > 0]) > 0 else 0
        avg_loss = abs(returns[returns < 0].mean()) if len(returns[returns < 0]) > 0 else 1
        profit_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 0
        
        metrics = {
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'profit_loss_ratio': profit_loss_ratio,
            'trading_days': trading_days,
        }
        
        if benchmark_values is not None:
            benchmark_return = (benchmark_values.iloc[-1] / benchmark_values.iloc[0]) - 1
            excess_return = total_return - benchmark_return
            metrics['benchmark_return'] = benchmark_return
            metrics['excess_return'] = excess_return
        
        return metrics
    
    def generate_text_report(self, metrics, strategy_name='Strategy'):
        """生成文本报告"""
        report = "=" * 60 + "\n"
        report += f"回测报告 - {strategy_name}\n"
        report += "=" * 60 + "\n\n"
        
        report += "收益指标:\n"
        report += f"  总收益率: {metrics['total_return']*100:.2f}%\n"
        report += f"  年化收益率: {metrics['annual_return']*100:.2f}%\n"
        report += f"  年化波动率: {metrics['volatility']*100:.2f}%\n\n"
        
        report += "风险指标:\n"
        report += f"  夏普比率: {metrics['sharpe_ratio']:.2f}\n"
        report += f"  最大回撤: {metrics['max_drawdown']*100:.2f}%\n"
        report += f"  胜率: {metrics['win_rate']*100:.2f}%\n"
        report += f"  盈亏比: {metrics['profit_loss_ratio']:.2f}\n\n"
        
        report += "交易统计:\n"
        report += f"  交易天数: {metrics['trading_days']}\n"
        
        if 'benchmark_return' in metrics:
            report += f"\n基准对比:\n"
            report += f"  基准收益率: {metrics['benchmark_return']*100:.2f}%\n"
            report += f"  超额收益: {metrics['excess_return']*100:.2f}%\n"
        
        report += "\n" + "=" * 60
        
        return report
