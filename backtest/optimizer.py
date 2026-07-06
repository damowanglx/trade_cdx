"""
策略参数优化模块
使用网格搜索优化策略参数

功能：
- 参数网格搜索
- 并行回测
- 结果排序
- 最优参数推荐
"""

import itertools
from datetime import datetime

import backtrader as bt
import pandas as pd


class ParameterOptimizer:
    """参数优化器"""
    
    def __init__(self, data_file, initial_cash=200000, commission=0.001, slippage=0.002):
        """
        初始化优化器
        
        Args:
            data_file: 数据文件路径
            initial_cash: 初始资金
            commission: 手续费率
            slippage: 滑点率
        """
        self.data_file = data_file
        self.initial_cash = initial_cash
        self.commission = commission
        self.slippage = slippage
        """
        初始化优化器
        
        Args:
            data_file: 数据文件路径
            initial_cash: 初始资金
            commission: 手续费率
        """
        self.data_file = data_file
        self.initial_cash = initial_cash
        self.commission = commission
        self.results = []
        
    def optimize(self, strategy_class, param_grid, print_log=True):
        """
        优化策略参数
        
        Args:
            strategy_class: 策略类
            param_grid: 参数网格，dict格式
                示例: {'fast_period': [5, 10, 15], 'slow_period': [20, 30, 40]}
            print_log: 是否打印日志
            
        Returns:
            list: 优化结果列表
        """
        # 生成参数组合
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        param_combinations = list(itertools.product(*param_values))
        
        total_combinations = len(param_combinations)
        
        if print_log:
            print("="*60)
            print(f"参数优化: {strategy_class.__name__}")
            print("="*60)
            print(f"参数组合数: {total_combinations}")
            print(f"参数网格: {param_grid}")
            print()
        
        self.results = []
        
        for i, values in enumerate(param_combinations):
            params = dict(zip(param_names, values))
            
            if print_log:
                print(f"[{i+1}/{total_combinations}] 测试参数: {params}")
            
            # 运行回测
            result = self._run_single_backtest(strategy_class, params)
            
            if result:
                result['params'] = params
                self.results.append(result)
                
                if print_log:
                    ret = result.get('total_return', 0)
                    sharpe = result.get('sharpe_ratio', None)
                    sharpe_str = f"{sharpe:.2f}" if sharpe else "N/A"
                    print(f"  -> 收益率: {ret:.2%}, 夏普: {sharpe_str}")
        
        # 按收益率排序
        self.results.sort(key=lambda x: x.get('total_return', 0), reverse=True)
        
        if print_log:
            self._print_optimization_results()
        
        return self.results
    
    def _run_single_backtest(self, strategy_class, params):
        """运行单次回测"""
        try:
            cerebro = bt.Cerebro()
            
            # 加载数据
            dataframe = pd.read_csv(self.data_file, index_col='date', parse_dates=True)
            data = bt.feeds.PandasData(dataname=dataframe)
            cerebro.adddata(data)
            
            # 添加策略
            cerebro.addstrategy(strategy_class, **params, printlog=False)
            
            # 设置资金和手续费
            cerebro.broker.setcash(self.initial_cash)
            cerebro.broker.setcommission(commission=self.commission)
            
            # 添加分析器
            cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
            cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
            cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
            cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
            
            # 运行回测
            results = cerebro.run()
            strat = results[0]
            
            # 获取结果
            final_value = cerebro.broker.getvalue()
            total_return = (final_value - self.initial_cash) / self.initial_cash
            
            sharpe = strat.analyzers.sharpe.get_analysis()
            drawdown = strat.analyzers.drawdown.get_analysis()
            returns = strat.analyzers.returns.get_analysis()
            trades = strat.analyzers.trades.get_analysis()
            
            result = {
                'initial_cash': self.initial_cash,
                'final_value': final_value,
                'total_return': total_return,
                'sharpe_ratio': sharpe.get('sharperatio', None),
                'max_drawdown': drawdown.get('max', {}).get('drawdown', None),
                'annual_return': returns.get('rnorm100', None),
                'total_trades': trades.get('total', {}).get('total', 0),
            }
            
            # 计算胜率
            if result['total_trades'] > 0:
                won = trades.get('won', {}).get('total', 0)
                result['win_rate'] = won / result['total_trades']
            else:
                result['win_rate'] = 0
            
            return result
            
        except Exception as e:
            print(f"  -> 回测失败: {e}")
            return None
    
    def _print_optimization_results(self):
        """打印优化结果"""
        print("\n" + "="*60)
        print("优化结果（按收益率排序）")
        print("="*60)
        
        # 表头
        print(f"{'排名':<4} {'收益率':<10} {'夏普比率':<10} {'最大回撤':<10} {'胜率':<10} {'参数'}")
        print("-"*80)
        
        # 前10个结果
        for i, result in enumerate(self.results[:10]):
            rank = i + 1
            ret = result.get('total_return', 0)
            sharpe = result.get('sharpe_ratio', None)
            sharpe_str = f"{sharpe:.2f}" if sharpe else "N/A"
            dd = result.get('max_drawdown', None)
            dd_str = f"{dd:.2%}" if dd else "N/A"
            wr = result.get('win_rate', 0)
            params = result.get('params', {})
            
            print(f"{rank:<4} {ret:<10.2%} {sharpe_str:<10} {dd_str:<10} {wr:<10.2%} {params}")
        
        # 最优参数
        if self.results:
            best = self.results[0]
            print("\n" + "="*60)
            print("最优参数推荐")
            print("="*60)
            print(f"参数: {best.get('params', {})}")
            print(f"收益率: {best.get('total_return', 0):.2%}")
            sharpe = best.get('sharpe_ratio', None)
            print(f"夏普比率: {sharpe:.2f}" if sharpe else "夏普比率: N/A")
            print("="*60)
    
    def get_best_params(self):
        """获取最优参数"""
        if self.results:
            return self.results[0].get('params', {})
        return {}
    
    def export_results(self, filename='optimization_results.csv'):
        """导出结果到CSV"""
        if self.results:
            df = pd.DataFrame(self.results)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"结果已导出到: {filename}")

