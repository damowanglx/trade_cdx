"""
流动性风险评估模块
评估资产的流动性风险

使用方法：
    from risk.liquidity_analyzer import LiquidityAnalyzer
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging


class LiquidityAnalyzer:
    """流动性分析器"""
    
    def __init__(self):
        """初始化流动性分析器"""
        self.logger = logging.getLogger('liquidity_analyzer')
        
    def calculate_amihud_illiquidity(self, returns: pd.Series, volume: pd.Series) -> pd.Series:
        """
        计算Amihud非流动性指标
        
        Args:
            returns: 收益率序列
            volume: 成交量序列
            
        Returns:
            Series: Amihud非流动性指标
        """
        # Amihud = |收益率| / 成交额
        # 这里用成交量近似
        illiquidity = abs(returns) / volume
        return illiquidity
        
    def calculate_turnover_rate(self, volume: pd.Series, shares_outstanding: float) -> pd.Series:
        """
        计算换手率
        
        Args:
            volume: 成交量序列
            shares_outstanding: 流通股本
            
        Returns:
            Series: 换手率序列
        """
        return volume / shares_outstanding
        
    def calculate_bid_ask_spread(self, high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
        """
        计算买卖价差（近似）
        
        Args:
            high: 最高价
            low: 最低价
            close: 收盘价
            
        Returns:
            Series: 买卖价差
        """
        # 用日内波动近似买卖价差
        spread = (high - low) / close
        return spread
        
    def assess_liquidity_risk(self, df: pd.DataFrame) -> Dict:
        """
        评估流动性风险
        
        Args:
            df: 包含OHLCV数据的DataFrame
            
        Returns:
            Dict: 流动性风险评估结果
        """
        result = {
            'risk_level': 'low',
            'metrics': {},
            'warnings': []
        }
        
        # 计算指标
        if 'volume' in df.columns:
            avg_volume = df['volume'].mean()
            result['metrics']['avg_volume'] = avg_volume
            
            # 成交量过低风险
            if avg_volume < 1000000:  # 100万
                result['risk_level'] = 'high'
                result['warnings'].append(f"成交量过低: {avg_volume:,.0f}")
            elif avg_volume < 5000000:  # 500万
                result['risk_level'] = 'medium'
                result['warnings'].append(f"成交量较低: {avg_volume:,.0f}")
        
        if all(col in df.columns for col in ['high', 'low', 'close']):
            # 计算买卖价差
            spread = self.calculate_bid_ask_spread(df['high'], df['low'], df['close'])
            avg_spread = spread.mean()
            result['metrics']['avg_spread'] = avg_spread
            
            # 价差过大风险
            if avg_spread > 0.05:  # 5%
                result['risk_level'] = 'high'
                result['warnings'].append(f"买卖价差过大: {avg_spread:.2%}")
            elif avg_spread > 0.02:  # 2%
                if result['risk_level'] == 'low':
                    result['risk_level'] = 'medium'
                result['warnings'].append(f"买卖价差较大: {avg_spread:.2%}")
        
        if 'close' in df.columns:
            # 计算价格波动
            volatility = df['close'].pct_change().std()
            result['metrics']['volatility'] = volatility
            
            # 高波动风险
            if volatility > 0.05:  # 5%
                result['warnings'].append(f"价格波动较大: {volatility:.2%}")
        
        return result
        
    def calculate_position_size_limit(self, avg_volume: pd.Series, 
                                     max_volume_pct: float = 0.1) -> pd.Series:
        """
        计算仓位大小限制
        
        Args:
            avg_volume: 平均成交量
            max_volume_pct: 最大成交量占比
            
        Returns:
            Series: 仓位大小限制
        """
        return avg_volume * max_volume_pct
        
    def generate_liquidity_report(self, df: pd.DataFrame) -> str:
        """
        生成流动性报告
        
        Args:
            df: 包含OHLCV数据的DataFrame
            
        Returns:
            str: 流动性报告
        """
        assessment = self.assess_liquidity_risk(df)
        
        report = "=" * 60 + "\n"
        report += "流动性风险评估报告\n"
        report += "=" * 60 + "\n\n"
        
        report += f"风险等级: {assessment['risk_level'].upper()}\n\n"
        
        report += "指标:\n"
        for name, value in assessment['metrics'].items():
            if isinstance(value, float):
                report += f"  {name}: {value:.4f}\n"
            else:
                report += f"  {name}: {value}\n"
        
        if assessment['warnings']:
            report += "\n警告:\n"
            for warning in assessment['warnings']:
                report += f"  - {warning}\n"
        else:
            report += "\n无警告\n"
        
        report += "\n" + "=" * 60
        
        return report


class LiquidityRiskManager:
    """流动性风险管理器"""
    
    def __init__(self, min_volume: float = 1000000, max_spread: float = 0.05):
        """
        初始化流动性风险管理器
        
        Args:
            min_volume: 最小成交量
            max_spread: 最大买卖价差
        """
        self.min_volume = min_volume
        self.max_spread = max_spread
        self.analyzer = LiquidityAnalyzer()
        
    def check_liquidity(self, df: pd.DataFrame) -> Dict:
        """
        检查流动性
        
        Args:
            df: 包含OHLCV数据的DataFrame
            
        Returns:
            Dict: 流动性检查结果
        """
        assessment = self.analyzer.assess_liquidity_risk(df)
        
        return {
            'is_tradable': assessment['risk_level'] != 'high',
            'risk_level': assessment['risk_level'],
            'warnings': assessment['warnings']
        }
        
    def calculate_max_position(self, df: pd.DataFrame, 
                              portfolio_value: float,
                              max_volume_pct: float = 0.1) -> float:
        """
        计算最大仓位
        
        Args:
            df: 包含OHLCV数据的DataFrame
            portfolio_value: 组合价值
            max_volume_pct: 最大成交量占比
            
        Returns:
            float: 最大仓位金额
        """
        if 'volume' not in df.columns:
            return portfolio_value * 0.3  # 默认30%
        
        avg_volume = df['volume'].mean()
        avg_price = df['close'].mean()
        
        # 计算最大可买数量
        max_shares = avg_volume * max_volume_pct
        max_value = max_shares * avg_price
        
        # 限制在组合价值的30%以内
        return min(max_value, portfolio_value * 0.3)
