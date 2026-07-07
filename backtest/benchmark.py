"""
基准对比模块
与沪深300等基准指数对比

使用方法：
    from backtest.benchmark import BenchmarkComparator
"""

import pandas as pd
import numpy as np


class BenchmarkComparator:
    """基准对比器"""
    
    def __init__(self, benchmark_file='data/cache/hs300_benchmark.csv'):
        """
        初始化
        
        Args:
            benchmark_file: 基准数据文件
        """
        self.benchmark_file = benchmark_file
        self.benchmark_data = None
        
    def load_benchmark(self):
        """加载基准数据"""
        if os.path.exists(self.benchmark_file):
            self.benchmark_data = pd.read_csv(self.benchmark_file, index_col='date', parse_dates=True)
            return True
        return False
    
    def calculate_benchmark_return(self, start_date=None, end_date=None):
        """计算基准收益率"""
        if self.benchmark_data is None:
            self.load_benchmark()
        
        if self.benchmark_data is None:
            return None
        
        df = self.benchmark_data
        
        if start_date:
            df = df[df.index >= start_date]
        if end_date:
            df = df[df.index <= end_date]
        
        if len(df) < 2:
            return None
        
        return (df['close'].iloc[-1] / df['close'].iloc[0]) - 1
    
    def calculate_excess_return(self, strategy_return, start_date=None, end_date=None):
        """计算超额收益"""
        benchmark_return = self.calculate_benchmark_return(start_date, end_date)
        
        if benchmark_return is None:
            return None
        
        return strategy_return - benchmark_return
    
    def calculate_information_ratio(self, strategy_returns, benchmark_returns):
        """计算信息比率"""
        excess_returns = strategy_returns - benchmark_returns
        
        if len(excess_returns) == 0:
            return 0
        
        tracking_error = excess_returns.std() * np.sqrt(252)
        
        if tracking_error == 0:
            return 0
        
        return excess_returns.mean() * 252 / tracking_error
    
    def compare_with_benchmark(self, strategy_return, strategy_name='Strategy'):
        """与基准对比"""
        benchmark_return = self.calculate_benchmark_return()
        
        if benchmark_return is None:
            print("基准数据不存在")
            return None
        
        excess_return = strategy_return - benchmark_return
        
        print("\n基准对比:")
        print("-" * 40)
        print(f"策略: {strategy_name}")
        print(f"策略收益率: {strategy_return:.2%}")
        print(f"基准收益率: {benchmark_return:.2%}")
        print(f"超额收益: {excess_return:.2%}")
        
        if excess_return > 0:
            print("结论: 策略跑赢基准")
        else:
            print("结论: 策略跑输基准")
        
        return {
            'strategy_return': strategy_return,
            'benchmark_return': benchmark_return,
            'excess_return': excess_return,
        }
