"""
参数敏感性分析模块
分析策略对参数变化的敏感程度

使用方法：
    from backtest.sensitivity import SensitivityAnalyzer
"""

import numpy as np
import pandas as pd
import itertools


class SensitivityAnalyzer:
    """参数敏感性分析器"""
    
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
        
    def analyze(self, param_name, param_values, base_params=None):
        """
        分析参数敏感性
        
        Args:
            param_name: 参数名称
            param_values: 参数值列表
            base_params: 基础参数
            
        Returns:
            dict: 分析结果
        """
        if base_params is None:
            base_params = {}
        
        results = []
        
        for value in param_values:
            params = base_params.copy()
            params[param_name] = value
            
            result = self._test_params(params)
            if result:
                result['param_value'] = value
                results.append(result)
        
        return results
    
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
            }
        except:
            return None
    
    def generate_report(self, param_name, results):
        """生成报告"""
        report = "=" * 60 + "\n"
        report += f"参数敏感性分析 - {param_name}\n"
        report += "=" * 60 + "\n\n"
        
        report += f"{'参数值':<15} {'收益率':<12} {'夏普比率':<10}\n"
        report += "-" * 40 + "\n"
        
        for result in results:
            sharpe = f"{result['sharpe_ratio']:.2f}" if result['sharpe_ratio'] else "N/A"
            report += f"{result['param_value']:<15} {result['total_return']*100:<12.2f} {sharpe:<10}\n"
        
        report += "\n" + "=" * 60
        
        return report
