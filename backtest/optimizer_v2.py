"""
参数优化器
支持网格搜索、随机搜索、贝叶斯优化

使用方法：
    from backtest.optimizer_v2 import ParameterOptimizerV2
"""

import itertools
import random
import numpy as np
import pandas as pd
from datetime import datetime


class ParameterOptimizerV2:
    """参数优化器"""
    
    def __init__(self, data_file, strategy_class, initial_cash=200000):
        """
        初始化
        
        Args:
            data_file: 数据文件
            strategy_class: 策略类
            initial_cash: 初始资金
        """
        self.data_file = data_file
        self.strategy_class = strategy_class
        self.initial_cash = initial_cash
        self.results = []
        
    def grid_search(self, param_grid, max_combinations=100):
        """
        网格搜索
        
        Args:
            param_grid: 参数网格
            max_combinations: 最大组合数
            
        Returns:
            list: 优化结果
        """
        # 生成参数组合
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        param_combinations = list(itertools.product(*param_values))
        
        # 限制组合数
        if len(param_combinations) > max_combinations:
            random.shuffle(param_combinations)
            param_combinations = param_combinations[:max_combinations]
        
        print(f"参数组合数: {len(param_combinations)}")
        
        # 测试每个组合
        for i, values in enumerate(param_combinations):
            params = dict(zip(param_names, values))
            
            if (i + 1) % 10 == 0:
                print(f"进度: {i+1}/{len(param_combinations)}")
            
            result = self._test_params(params)
            if result:
                result['params'] = params
                self.results.append(result)
        
        # 按收益率排序
        self.results.sort(key=lambda x: x.get('total_return', 0), reverse=True)
        
        return self.results
    
    def random_search(self, param_ranges, n_iterations=50):
        """
        随机搜索
        
        Args:
            param_ranges: 参数范围
            n_iterations: 迭代次数
            
        Returns:
            list: 优化结果
        """
        print(f"随机搜索迭代: {n_iterations} 次")
        
        for i in range(n_iterations):
            if (i + 1) % 10 == 0:
                print(f"进度: {i+1}/{n_iterations}")
            
            # 随机生成参数
            params = {}
            for name, (min_val, max_val) in param_ranges.items():
                if isinstance(min_val, int):
                    params[name] = random.randint(min_val, max_val)
                else:
                    params[name] = random.uniform(min_val, max_val)
            
            result = self._test_params(params)
            if result:
                result['params'] = params
                self.results.append(result)
        
        # 按收益率排序
        self.results.sort(key=lambda x: x.get('total_return', 0), reverse=True)
        
        return self.results
    
    def _test_params(self, params):
        """测试参数"""
        try:
            import backtrader as bt
            
            df = pd.read_csv(self.data_file, index_col='date', parse_dates=True)
            
            cerebro = bt.Cerebro()
            data = bt.feeds.PandasData(dataname=df)
            cerebro.adddata(data)
            cerebro.addstrategy(self.strategy_class, **params)
            cerebro.broker.setcash(self.initial_cash)
            cerebro.broker.setcommission(commission=0.001)
            cerebro.broker.set_slippage_perc(0.002)
            
            cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
            cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
            
            results = cerebro.run()
            strat = results[0]
            
            final_value = cerebro.broker.getvalue()
            total_return = (final_value - self.initial_cash) / self.initial_cash
            sharpe = strat.analyzers.sharpe.get_analysis()
            
            return {
                'total_return': total_return,
                'sharpe_ratio': sharpe.get('sharperatio', None),
                'final_value': final_value,
            }
        except:
            return None
    
    def get_best_params(self):
        """获取最优参数"""
        if self.results:
            return self.results[0].get('params', {})
        return {}
    
    def print_top_results(self, n=10):
        """打印前N个结果"""
        print(f"\n前{n}个最优参数:")
        print("-" * 80)
        print(f"{'排名':<5} {'收益率':<10} {'夏普比率':<10} {'参数'}")
        print("-" * 80)
        
        for i, result in enumerate(self.results[:n]):
            sharpe = f"{result['sharpe_ratio']:.2f}" if result['sharpe_ratio'] else "N/A"
            print(f"{i+1:<5} {result['total_return']*100:<10.2f} {sharpe:<10} {result['params']}")
