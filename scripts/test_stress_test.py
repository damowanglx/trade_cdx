"""
压力测试模块测试
测试压力测试和情景分析

使用方法：
    python scripts/test_stress_test.py
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from risk.stress_test import StressTest, ScenarioAnalyzer


def main():
    """主函数"""
    print("="*60)
    print("压力测试模块测试")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 生成模拟收益率数据
    np.random.seed(42)
    returns = pd.Series(np.random.normal(0.001, 0.02, 252))
    portfolio_value = 100000  # 10万资金
    
    print("=== 测试数据 ===")
    print(f"组合价值: {portfolio_value:,.2f}")
    print(f"数据点数: {len(returns)}")
    print(f"平均日收益率: {returns.mean():.4%}")
    print(f"年化波动率: {returns.std() * np.sqrt(252):.2%}")
    print()
    
    # 创建压力测试实例
    stress_test = StressTest()
    
    # 显示预定义情景
    print("=== 预定义压力情景 ===")
    for name, scenario in stress_test.PREDEFINED_SCENARIOS.items():
        print(f"{name}: {scenario['name']}")
        print(f"  描述: {scenario['description']}")
        print(f"  市场冲击: {scenario['market_shock']:.0%}")
        print()
    
    # 运行压力测试
    print("=== 运行压力测试 ===")
    results = stress_test.run_stress_test(returns, portfolio_value)
    
    # 生成报告
    report = stress_test.generate_report(results, portfolio_value)
    print(report)
    
    # 情景分析
    print("\n=== 情景分析 ===")
    analysis = ScenarioAnalyzer.analyze_portfolio_resilience(results)
    
    print(f"最坏情况损失: {analysis['worst_case_loss']:.2%}")
    print(f"平均损失: {analysis['average_loss']:.2%}")
    print(f"最坏回撤: {analysis['worst_drawdown']:.2%}")
    print(f"风险评分: {analysis['risk_score']:.1f}")
    
    # 推荐风险措施
    print("\n=== 风险建议 ===")
    recommendations = ScenarioAnalyzer.recommend_risk_measures(analysis)
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    # 保存报告
    os.makedirs('reports', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    with open(f'reports/stress_test_report_{timestamp}.txt', 'w', encoding='utf-8') as f:
        f.write(report)
        f.write("\n\n=== 情景分析 ===\n")
        f.write(f"最坏情况损失: {analysis['worst_case_loss']:.2%}\n")
        f.write(f"平均损失: {analysis['average_loss']:.2%}\n")
        f.write(f"最坏回撤: {analysis['worst_drawdown']:.2%}\n")
        f.write(f"风险评分: {analysis['risk_score']:.1f}\n")
        f.write("\n=== 风险建议 ===\n")
        for i, rec in enumerate(recommendations, 1):
            f.write(f"{i}. {rec}\n")
    
    print(f"\n报告已保存到: reports/stress_test_report_{timestamp}.txt")
    print("="*60)
    print("压力测试完成！")
    print("="*60)


if __name__ == '__main__':
    main()
