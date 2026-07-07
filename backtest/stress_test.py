"""
压力测试模块
测试极端市场情况下的策略表现

使用方法：
    from backtest.stress_test import StressTester
"""

import pandas as pd
import numpy as np


class StressTester:
    """压力测试器"""
    
    def __init__(self):
        """初始化"""
        self.scenarios = {
            'financial_crisis_2008': {
                'name': '2008年金融危机',
                'market_shock': -0.40,
                'volatility_increase': 2.0,
            },
            'covid_crash_2020': {
                'name': '2020年新冠疫情崩盘',
                'market_shock': -0.30,
                'volatility_increase': 1.5,
            },
            'flash_crash': {
                'name': '闪崩',
                'market_shock': -0.10,
                'volatility_increase': 3.0,
            },
            'interest_rate_shock': {
                'name': '利率冲击',
                'market_shock': -0.15,
                'volatility_increase': 1.2,
            },
        }
    
    def run_stress_test(self, returns, portfolio_value, scenarios=None):
        """
        运行压力测试
        
        Args:
            returns: 历史收益率
            portfolio_value: 组合价值
            scenarios: 压力情景
            
        Returns:
            dict: 测试结果
        """
        if scenarios is None:
            scenarios = self.scenarios
        
        results = {}
        
        for scenario_name, scenario in scenarios.items():
            result = self._simulate_scenario(returns, portfolio_value, scenario)
            results[scenario_name] = result
        
        return results
    
    def _simulate_scenario(self, returns, portfolio_value, scenario):
        """模拟压力情景"""
        market_shock = scenario['market_shock']
        volatility_increase = scenario['volatility_increase']
        
        # 调整收益率
        stressed_returns = returns.copy()
        stressed_returns = stressed_returns + market_shock / 252
        stressed_returns = stressed_returns * volatility_increase
        
        # 计算损失
        total_loss = portfolio_value * market_shock
        max_drawdown = self._calculate_max_drawdown(stressed_returns)
        
        return {
            'total_loss': total_loss,
            'total_loss_pct': market_shock,
            'max_drawdown': max_drawdown,
            'final_value': portfolio_value * (1 + market_shock),
        }
    
    def _calculate_max_drawdown(self, returns):
        """计算最大回撤"""
        cumulative = (1 + returns).cumprod()
        peak = cumulative.cummax()
        drawdown = (cumulative - peak) / peak
        return drawdown.min()
    
    def generate_report(self, results, portfolio_value):
        """生成报告"""
        report = "=" * 60 + "\n"
        report += "压力测试报告\n"
        report += "=" * 60 + "\n\n"
        
        report += f"组合价值: {portfolio_value:,.2f}\n\n"
        
        report += f"{'情景':<20} {'损失':<15} {'损失比例':<12} {'最大回撤':<12}\n"
        report += "-" * 60 + "\n"
        
        for scenario_name, result in results.items():
            report += f"{scenario_name:<20} "
            report += f"{result['total_loss']:>12,.2f} "
            report += f"{result['total_loss_pct']:>10.2%} "
            report += f"{result['max_drawdown']:>10.2%}\n"
        
        report += "\n" + "=" * 60
        
        return report
