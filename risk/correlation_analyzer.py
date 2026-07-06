"""
相关性分析模块
分析投资组合中资产的相关性

使用方法：
    from risk.correlation_analyzer import CorrelationAnalyzer
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging


class CorrelationAnalyzer:
    """相关性分析器"""
    
    def __init__(self):
        """初始化相关性分析器"""
        self.logger = logging.getLogger('correlation_analyzer')
        
    def calculate_correlation_matrix(self, returns_dict: Dict[str, pd.Series]) -> pd.DataFrame:
        """
        计算相关性矩阵
        
        Args:
            returns_dict: 各资产收益率字典
            
        Returns:
            DataFrame: 相关性矩阵
        """
        df = pd.DataFrame(returns_dict)
        return df.corr()
        
    def calculate_rolling_correlation(self, returns1: pd.Series, returns2: pd.Series, 
                                     window: int = 20) -> pd.Series:
        """
        计算滚动相关性
        
        Args:
            returns1: 资产1收益率
            returns2: 资产2收益率
            window: 窗口大小
            
        Returns:
            Series: 滚动相关性序列
        """
        return returns1.rolling(window).corr(returns2)
        
    def find_high_correlation_pairs(self, returns_dict: Dict[str, pd.Series], 
                                   threshold: float = 0.7) -> List[Dict]:
        """
        找出高相关性的资产对
        
        Args:
            returns_dict: 各资产收益率字典
            threshold: 相关性阈值
            
        Returns:
            List: 高相关性资产对列表
        """
        corr_matrix = self.calculate_correlation_matrix(returns_dict)
        
        high_corr_pairs = []
        symbols = list(returns_dict.keys())
        
        for i in range(len(symbols)):
            for j in range(i + 1, len(symbols)):
                corr = corr_matrix.iloc[i, j]
                if abs(corr) >= threshold:
                    high_corr_pairs.append({
                        'symbol1': symbols[i],
                        'symbol2': symbols[j],
                        'correlation': corr,
                        'risk_level': 'high' if abs(corr) > 0.8 else 'medium'
                    })
        
        # 按相关性排序
        high_corr_pairs.sort(key=lambda x: abs(x['correlation']), reverse=True)
        
        return high_corr_pairs
        
    def calculate_portfolio_correlation(self, returns_dict: Dict[str, pd.Series],
                                       weights: Dict[str, float]) -> float:
        """
        计算组合整体相关性
        
        Args:
            returns_dict: 各资产收益率字典
            weights: 各资产权重
            
        Returns:
            float: 组合相关性
        """
        corr_matrix = self.calculate_correlation_matrix(returns_dict)
        
        symbols = list(returns_dict.keys())
        n = len(symbols)
        
        # 计算加权平均相关性
        total_corr = 0
        total_weight = 0
        
        for i in range(n):
            for j in range(i + 1, n):
                w_i = weights.get(symbols[i], 0)
                w_j = weights.get(symbols[j], 0)
                corr = corr_matrix.iloc[i, j]
                
                total_corr += w_i * w_j * corr
                total_weight += w_i * w_j
        
        if total_weight > 0:
            return total_corr / total_weight
        return 0
        
    def generate_correlation_report(self, returns_dict: Dict[str, pd.Series],
                                   weights: Optional[Dict[str, float]] = None) -> str:
        """
        生成相关性报告
        
        Args:
            returns_dict: 各资产收益率字典
            weights: 各资产权重（可选）
            
        Returns:
            str: 相关性报告
        """
        corr_matrix = self.calculate_correlation_matrix(returns_dict)
        
        report = "=" * 60 + "\n"
        report += "相关性分析报告\n"
        report += "=" * 60 + "\n\n"
        
        # 相关性矩阵
        report += "相关性矩阵:\n"
        report += corr_matrix.to_string() + "\n\n"
        
        # 高相关性资产对
        high_corr_pairs = self.find_high_correlation_pairs(returns_dict, threshold=0.5)
        
        if high_corr_pairs:
            report += "高相关性资产对:\n"
            report += "-" * 40 + "\n"
            for pair in high_corr_pairs:
                report += f"{pair['symbol1']} - {pair['symbol2']}: {pair['correlation']:.3f} ({pair['risk_level']})\n"
        else:
            report += "未发现高相关性资产对\n"
        
        # 组合相关性
        if weights:
            portfolio_corr = self.calculate_portfolio_correlation(returns_dict, weights)
            report += f"\n组合整体相关性: {portfolio_corr:.3f}\n"
        
        report += "\n" + "=" * 60
        
        return report


class CorrelationRiskManager:
    """相关性风险管理器"""
    
    def __init__(self, max_correlation: float = 0.7):
        """
        初始化相关性风险管理器
        
        Args:
            max_correlation: 最大允许相关性
        """
        self.max_correlation = max_correlation
        self.analyzer = CorrelationAnalyzer()
        
    def check_portfolio_correlation(self, returns_dict: Dict[str, pd.Series],
                                   weights: Dict[str, float]) -> Dict:
        """
        检查组合相关性风险
        
        Args:
            returns_dict: 各资产收益率字典
            weights: 各资产权重
            
        Returns:
            Dict: 风险检查结果
        """
        result = {
            'is_safe': True,
            'warnings': [],
            'high_corr_pairs': []
        }
        
        # 检查高相关性资产对
        high_corr_pairs = self.analyzer.find_high_correlation_pairs(returns_dict, self.max_correlation)
        
        if high_corr_pairs:
            result['is_safe'] = False
            result['high_corr_pairs'] = high_corr_pairs
            
            for pair in high_corr_pairs:
                result['warnings'].append(
                    f"高相关性风险: {pair['symbol1']} - {pair['symbol2']} = {pair['correlation']:.3f}"
                )
        
        # 检查组合整体相关性
        portfolio_corr = self.analyzer.calculate_portfolio_correlation(returns_dict, weights)
        
        if portfolio_corr > self.max_correlation:
            result['is_safe'] = False
            result['warnings'].append(
                f"组合整体相关性过高: {portfolio_corr:.3f} > {self.max_correlation}"
            )
        
        return result
        
    def suggest_diversification(self, returns_dict: Dict[str, pd.Series],
                               current_weights: Dict[str, float]) -> Dict[str, float]:
        """
        建议分散化配置
        
        Args:
            returns_dict: 各资产收益率字典
            current_weights: 当前权重
            
        Returns:
            Dict: 建议的权重
        """
        # 计算相关性矩阵
        corr_matrix = self.analyzer.calculate_correlation_matrix(returns_dict)
        
        # 找出低相关性资产
        symbols = list(returns_dict.keys())
        low_corr_assets = []
        
        for symbol in symbols:
            avg_corr = corr_matrix[symbol].drop(symbol).abs().mean()
            if avg_corr < 0.5:
                low_corr_assets.append(symbol)
        
        # 重新分配权重
        if low_corr_assets:
            new_weight = 1.0 / len(low_corr_assets)
            suggested_weights = {symbol: new_weight for symbol in low_corr_assets}
        else:
            # 等权重分配
            new_weight = 1.0 / len(symbols)
            suggested_weights = {symbol: new_weight for symbol in symbols}
        
        return suggested_weights
