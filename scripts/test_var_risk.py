"""
VaR风险价值测试
测试VaR计算和压力测试

使用方法：
    python scripts/test_var_risk.py
"""

import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from risk.var_calculator import RiskMetrics, VaRCalculator


def main():
    """主函数"""
    print("="*60)
    print("VaR风险价值测试")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 生成模拟收益率数据
    np.random.seed(42)
    returns = pd.Series(np.random.normal(0.001, 0.02, 252))  # 一年日收益率
    
    print("=== 测试数据 ===")
    print(f"数据点数: {len(returns)}")
    print(f"平均日收益率: {returns.mean():.4%}")
    print(f"日波动率: {returns.std():.4%}")
    print(f"年化波动率: {returns.std() * np.sqrt(252):.2%}")
    print()
    
    # 测试不同置信水平的VaR
    print("=== VaR计算测试 ===")
    
    for confidence in [0.90, 0.95, 0.99]:
        var_calc = VaRCalculator(confidence_level=confidence)
        
        # 历史模拟法
        var_historical = var_calc.calculate_var(returns, method='historical')
        print(f"历史模拟法VaR ({confidence*100}%): {var_historical:.4%}")
        
        # 参数法
        var_parametric = var_calc.calculate_var(returns, method='parametric')
        print(f"参数法VaR ({confidence*100}%): {var_parametric:.4%}")
        print()
    
    # 测试不同持有期
    print("=== 不同持有期 ===")
    var_calc = VaRCalculator(confidence_level=0.95)
    
    for period in [1, 5, 10, 20]:
        var = var_calc.calculate_var(returns, holding_period=period)
        print(f"VaR ({period}天): {var:.4%}")
    
    # 计算CVaR
    print("\n=== 条件VaR (CVaR) ===")
    cvar = var_calc.calculate_cvar(returns)
    print(f"CVaR (95%): {cvar:.4%}")
    
    # 测试风险指标
    print("\n=== 风险指标测试 ===")
    
    # 夏普比率
    sharpe = RiskMetrics.calculate_sharpe_ratio(returns)
    print(f"夏普比率: {sharpe:.2f}")
    
    # 最大回撤
    max_dd = RiskMetrics.calculate_max_drawdown(returns)
    print(f"最大回撤: {max_dd:.2%}")
    
    # 卡尔玛比率
    calmar = RiskMetrics.calculate_calmar_ratio(returns)
    print(f"卡尔玛比率: {calmar:.2f}")
    
    # 压力测试
    print("\n=== 压力测试 ===")
    scenarios = {
        '市场下跌10%': -0.10,
        '市场下跌20%': -0.20,
        '市场下跌30%': -0.30,
        '市场上涨10%': 0.10,
        '市场上涨20%': 0.20,
    }
    
    stress_results = var_calc.stress_test(returns, scenarios)
    
    print(f"\n{'情景':<15} {'VaR':<12}")
    print("-"*30)
    for scenario, var in stress_results.items():
        print(f"{scenario:<15} {var:.4%}")
    
    print("\n" + "="*60)
    print("VaR风险价值测试完成！")
    print("="*60)


if __name__ == '__main__':
    main()
