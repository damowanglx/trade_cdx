"""
蒙特卡洛模拟模块
模拟策略在不同市场情况下的表现

使用方法：
    from backtest.monte_carlo import MonteCarloSimulator
"""

import numpy as np
import pandas as pd


class MonteCarloSimulator:
    """蒙特卡洛模拟器"""
    
    def __init__(self, n_simulations=1000, n_days=252):
        """
        初始化
        
        Args:
            n_simulations: 模拟次数
            n_days: 模拟天数
        """
        self.n_simulations = n_simulations
        self.n_days = n_days
        
    def simulate(self, returns, initial_value=100000):
        """
        运行蒙特卡洛模拟
        
        Args:
            returns: 历史收益率
            initial_value: 初始价值
            
        Returns:
            dict: 模拟结果
        """
        # 计算历史统计
        mean_return = returns.mean()
        std_return = returns.std()
        
        # 运行模拟
        simulation_results = []
        
        for i in range(self.n_simulations):
            # 生成随机收益率
            random_returns = np.random.normal(mean_return, std_return, self.n_days)
            
            # 计算累计收益
            cumulative_returns = np.cumprod(1 + random_returns)
            
            # 计算最终价值
            final_value = initial_value * cumulative_returns[-1]
            
            # 计算最大回撤
            peak = np.maximum.accumulate(cumulative_returns)
            drawdown = (cumulative_returns - peak) / peak
            max_drawdown = drawdown.min()
            
            simulation_results.append({
                'final_value': final_value,
                'total_return': cumulative_returns[-1] - 1,
                'max_drawdown': max_drawdown,
            })
        
        # 转换为DataFrame
        df = pd.DataFrame(simulation_results)
        
        # 计算统计
        results = {
            'mean_return': df['total_return'].mean(),
            'median_return': df['total_return'].median(),
            'std_return': df['total_return'].std(),
            'min_return': df['total_return'].min(),
            'max_return': df['total_return'].max(),
            'percentile_5': df['total_return'].quantile(0.05),
            'percentile_95': df['total_return'].quantile(0.95),
            'mean_max_drawdown': df['max_drawdown'].mean(),
            'worst_max_drawdown': df['max_drawdown'].min(),
            'simulation_results': df,
        }
        
        return results
    
    def generate_report(self, results):
        """生成报告"""
        report = "=" * 60 + "\n"
        report += "蒙特卡洛模拟报告\n"
        report += "=" * 60 + "\n\n"
        
        report += f"模拟次数: {self.n_simulations}\n"
        report += f"模拟天数: {self.n_days}\n\n"
        
        report += "收益率分布:\n"
        report += f"  平均收益率: {results['mean_return']:.2%}\n"
        report += f"  中位数收益率: {results['median_return']:.2%}\n"
        report += f"  收益率标准差: {results['std_return']:.2%}\n"
        report += f"  最小收益率: {results['min_return']:.2%}\n"
        report += f"  最大收益率: {results['max_return']:.2%}\n"
        report += f"  5%分位数: {results['percentile_5']:.2%}\n"
        report += f"  95%分位数: {results['percentile_95']:.2%}\n\n"
        
        report += "最大回撤分布:\n"
        report += f"  平均最大回撤: {results['mean_max_drawdown']:.2%}\n"
        report += f"  最差最大回撤: {results['worst_max_drawdown']:.2%}\n"
        
        report += "\n" + "=" * 60
        
        return report
