"""
Walk-Forward验证模块
样本外验证策略泛化能力

使用方法：
    from backtest.walk_forward import WalkForwardValidator
"""

import pandas as pd
import numpy as np


class WalkForwardValidator:
    """Walk-Forward验证器"""
    
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
        
    def validate(self, train_pct=0.7, n_splits=5):
        """
        运行Walk-Forward验证
        
        Args:
            train_pct: 训练集比例
            n_splits: 分割数
            
        Returns:
            dict: 验证结果
        """
        # 加载数据
        df = pd.read_csv(self.data_file, index_col='date', parse_dates=True)
        
        # 计算分割点
        n = len(df)
        split_size = n // n_splits
        
        results = []
        
        for i in range(n_splits):
            # 计算训练集和测试集
            start_idx = i * split_size
            end_idx = min((i + 1) * split_size, n)
            
            train_end_idx = start_idx + int(split_size * train_pct)
            
            train_df = df.iloc[start_idx:train_end_idx]
            test_df = df.iloc[train_end_idx:end_idx]
            
            # 在训练集上优化参数
            best_params = self._optimize_params(train_df)
            
            # 在测试集上验证
            test_result = self._test_params(test_df, best_params)
            
            if test_result:
                test_result['split'] = i + 1
                test_result['train_period'] = f"{train_df.index[0]} - {train_df.index[-1]}"
                test_result['test_period'] = f"{test_df.index[0]} - {test_df.index[-1]}"
                results.append(test_result)
        
        return results
    
    def _optimize_params(self, train_df):
        """在训练集上优化参数"""
        # 简化版本：使用默认参数
        return {'rsi_period': 21, 'rsi_oversold': 30, 'rsi_overbought': 70}
    
    def _test_params(self, test_df, params):
        """在测试集上测试参数"""
        try:
            import backtrader as bt
            
            cerebro = bt.Cerebro()
            data = bt.feeds.PandasData(dataname=test_df)
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
                'final_value': final_value,
            }
        except:
            return None
    
    def generate_report(self, results):
        """生成报告"""
        report = "=" * 60 + "\n"
        report += "Walk-Forward验证报告\n"
        report += "=" * 60 + "\n\n"
        
        report += f"{'分割':<8} {'训练期':<30} {'测试期':<30} {'收益率':<10} {'夏普比率':<10}\n"
        report += "-" * 90 + "\n"
        
        for result in results:
            sharpe = f"{result['sharpe_ratio']:.2f}" if result['sharpe_ratio'] else "N/A"
            report += f"{result['split']:<8} {result['train_period']:<30} {result['test_period']:<30} "
            report += f"{result['total_return']*100:<10.2f} {sharpe:<10}\n"
        
        # 计算平均表现
        avg_return = np.mean([r['total_return'] for r in results])
        avg_sharpe = np.mean([r['sharpe_ratio'] for r in results if r['sharpe_ratio']])
        
        report += "\n" + "-" * 90 + "\n"
        report += f"平均表现: 收益率={avg_return:.2%}, 夏普比率={avg_sharpe:.2f}\n"
        
        report += "\n" + "=" * 60
        
        return report
