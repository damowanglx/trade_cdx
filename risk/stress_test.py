"""
压力测试模块
模拟极端市场情况下的策略表现

使用方法：
    from risk.stress_test import StressTest
"""

from typing import Any, Dict, List

import numpy as np
import pandas as pd


class StressTest:
    """压力测试类"""
    
    # 预定义的压力情景
    PREDEFINED_SCENARIOS = {
        'financial_crisis_2008': {
            'name': '2008年金融危机',
            'description': '全球金融危机，市场大幅下跌',
            'market_shock': -0.40,  # 市场下跌40%
            'volatility_increase': 2.0,  # 波动率增加200%
            'correlation_increase': 0.3,  # 相关性增加
        },
        'covid_crash_2020': {
            'name': '2020年新冠疫情崩盘',
            'description': '新冠疫情导致的市场恐慌',
            'market_shock': -0.30,
            'volatility_increase': 1.5,
            'correlation_increase': 0.2,
        },
        'flash_crash': {
            'name': '闪崩',
            'description': '短时间内大幅下跌',
            'market_shock': -0.10,
            'volatility_increase': 3.0,
            'correlation_increase': 0.5,
        },
        'interest_rate_shock': {
            'name': '利率冲击',
            'description': '利率突然上升',
            'market_shock': -0.15,
            'volatility_increase': 1.2,
            'correlation_increase': 0.1,
        },
        'geopolitical_event': {
            'name': '地缘政治事件',
            'description': '战争或政治危机',
            'market_shock': -0.20,
            'volatility_increase': 1.8,
            'correlation_increase': 0.4,
        }
    }
    
    def __init__(self):
        """初始化压力测试"""
        self.scenarios = self.PREDEFINED_SCENARIOS.copy()
        
    def add_custom_scenario(self, name: str, scenario: Dict[str, Any]):
        """
        添加自定义压力情景
        
        Args:
            name: 情景名称
            scenario: 情景参数
        """
        self.scenarios[name] = scenario
        
    def run_stress_test(self, returns: pd.Series, 
                       portfolio_value: float,
                       scenarios: List[str] = None) -> Dict[str, Dict[str, float]]:
        """
        运行压力测试
        
        Args:
            returns: 历史收益率
            portfolio_value: 组合价值
            scenarios: 要测试的情景列表
            
        Returns:
            Dict: 压力测试结果
        """
        if scenarios is None:
            scenarios = list(self.scenarios.keys())
            
        results = {}
        
        for scenario_name in scenarios:
            if scenario_name not in self.scenarios:
                continue
                
            scenario = self.scenarios[scenario_name]
            result = self._simulate_scenario(returns, portfolio_value, scenario)
            results[scenario_name] = result
            
        return results
        
    def _simulate_scenario(self, returns: pd.Series, 
                          portfolio_value: float,
                          scenario: Dict[str, Any]) -> Dict[str, float]:
        """
        模拟单个压力情景
        
        Args:
            returns: 历史收益率
            portfolio_value: 组合价值
            scenario: 情景参数
            
        Returns:
            Dict: 情景模拟结果
        """
        market_shock = scenario.get('market_shock', 0)
        volatility_increase = scenario.get('volatility_increase', 1)
        
        # 调整收益率
        stressed_returns = returns.copy()
        
        # 应用市场冲击
        stressed_returns = stressed_returns + market_shock / 252  # 分摊到每天
        
        # 增加波动率
        stressed_returns = stressed_returns * volatility_increase
        
        # 计算损失
        total_loss = portfolio_value * market_shock
        max_drawdown = self._calculate_max_drawdown(stressed_returns)
        
        # 计算恢复时间
        recovery_time = self._estimate_recovery_time(stressed_returns)
        
        return {
            'total_loss': total_loss,
            'total_loss_pct': market_shock,
            'max_drawdown': max_drawdown,
            'recovery_time_days': recovery_time,
            'final_value': portfolio_value * (1 + market_shock)
        }
        
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """计算最大回撤"""
        cumulative = (1 + returns).cumprod()
        peak = cumulative.cummax()
        drawdown = (cumulative - peak) / peak
        return drawdown.min()
        
    def _estimate_recovery_time(self, returns: pd.Series) -> int:
        """估计恢复时间（天）"""
        cumulative = (1 + returns).cumprod()
        peak = cumulative.cummax()
        
        # 找到最大回撤点
        max_dd_idx = (cumulative - peak).idxmin()
        
        # 找到恢复点
        recovery_mask = cumulative[max_dd_idx:] >= peak[max_dd_idx]
        if recovery_mask.any():
            recovery_idx = recovery_mask.idxmax()
            # 处理索引类型
            if hasattr(recovery_idx, 'days'):
                return (recovery_idx - max_dd_idx).days
            else:
                return int(recovery_idx - max_dd_idx)
        else:
            return -1  # 未恢复
            
    def generate_report(self, results: Dict[str, Dict[str, float]], 
                       portfolio_value: float) -> str:
        """
        生成压力测试报告
        
        Args:
            results: 压力测试结果
            portfolio_value: 组合价值
            
        Returns:
            str: 报告文本
        """
        report = "=" * 60 + "\n"
        report += "压力测试报告\n"
        report += "=" * 60 + "\n\n"
        
        report += f"组合价值: {portfolio_value:,.2f}\n\n"
        
        report += f"{'情景':<20} {'损失':<15} {'损失比例':<12} {'最大回撤':<12} {'恢复时间':<12}\n"
        report += "-" * 70 + "\n"
        
        for scenario_name, result in results.items():
            scenario = self.scenarios.get(scenario_name, {})
            name = scenario.get('name', scenario_name)
            
            report += f"{name:<20} "
            report += f"{result['total_loss']:>12,.2f} "
            report += f"{result['total_loss_pct']:>10.2%} "
            report += f"{result['max_drawdown']:>10.2%} "
            
            recovery = result['recovery_time_days']
            if recovery > 0:
                report += f"{recovery:>10}天"
            else:
                report += f"{'未恢复':>10}"
            report += "\n"
            
        report += "\n" + "=" * 60
        
        return report


class ScenarioAnalyzer:
    """情景分析器"""
    
    @staticmethod
    def analyze_portfolio_resilience(results: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """
        分析组合韧性
        
        Args:
            results: 压力测试结果
            
        Returns:
            Dict: 分析结果
        """
        losses = [r['total_loss_pct'] for r in results.values()]
        drawdowns = [r['max_drawdown'] for r in results.values()]
        
        analysis = {
            'worst_case_loss': min(losses),
            'average_loss': np.mean(losses),
            'worst_drawdown': min(drawdowns),
            'average_drawdown': np.mean(drawdowns),
            'scenarios_tested': len(results),
            'risk_score': abs(min(losses)) * 100  # 风险评分
        }
        
        return analysis
        
    @staticmethod
    def recommend_risk_measures(analysis: Dict[str, Any]) -> List[str]:
        """
        推荐风险措施
        
        Args:
            analysis: 分析结果
            
        Returns:
            List: 建议列表
        """
        recommendations = []
        
        if analysis['worst_case_loss'] < -0.30:
            recommendations.append("建议降低仓位至50%以下")
            
        if analysis['worst_drawdown'] < -0.25:
            recommendations.append("建议设置更严格的止损（8%以内）")
            
        if analysis['risk_score'] > 30:
            recommendations.append("建议增加对冲策略")
            
        if not recommendations:
            recommendations.append("当前风险水平可接受")
            
        return recommendations

