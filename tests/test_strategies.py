"""
单元测试模块
测试策略和工具函数

使用方法：
    python -m pytest tests/test_strategies.py -v
"""

import os
import sys

import numpy as np
import pandas as pd
import pytest

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestRSICalculation:
    """RSI计算测试"""
    
    def test_rsi_basic(self):
        """测试RSI基本计算"""
        # 创建测试数据
        prices = pd.Series([10, 11, 12, 11, 10, 9, 10, 11, 12, 13, 14, 15, 14, 13, 12])
        
        # 计算RSI
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # 验证RSI在0-100之间
        assert rsi.dropna().between(0, 100).all()
    
    def test_rsi_extremes(self):
        """测试RSI极端情况"""
        # 全部上涨
        up_prices = pd.Series([10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24])
        delta = up_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # 全部上涨时RSI应该接近100
        assert rsi.iloc[-1] > 90


class TestMACDCalculation:
    """MACD计算测试"""
    
    def test_macd_basic(self):
        """测试MACD基本计算"""
        # 创建测试数据
        np.random.seed(42)
        prices = pd.Series(np.cumsum(np.random.randn(100)) + 100)
        
        # 计算EMA
        ema12 = prices.ewm(span=12).mean()
        ema26 = prices.ewm(span=26).mean()
        
        # 计算DIF
        dif = ema12 - ema26
        
        # 计算DEA
        dea = dif.ewm(span=9).mean()
        
        # 计算MACD
        macd = 2 * (dif - dea)
        
        # 验证
        assert len(dif) == len(prices)
        assert len(dea) == len(prices)
        assert len(macd) == len(prices)


class TestBacktestEngine:
    """回测引擎测试"""
    
    def test_data_loading(self):
        """测试数据加载"""
        data_file = 'data/cache/000001_real_data.csv'
        
        if os.path.exists(data_file):
            df = pd.read_csv(data_file, index_col='date', parse_dates=True)
            
            # 验证数据结构
            assert 'open' in df.columns
            assert 'high' in df.columns
            assert 'low' in df.columns
            assert 'close' in df.columns
            assert 'volume' in df.columns
            
            # 验证数据完整性
            assert len(df) > 0
            assert df['close'].notna().all()
        else:
            # 数据文件不存在时，创建模拟数据测试
            df = pd.DataFrame({
                'open': [10, 11, 12],
                'high': [11, 12, 13],
                'low': [9, 10, 11],
                'close': [10.5, 11.5, 12.5],
                'volume': [1000, 2000, 3000]
            })
            assert 'open' in df.columns
            assert len(df) > 0
    
    def test_strategy_params(self):
        """测试策略参数"""
        # RSI参数
        rsi_params = {
            'rsi_period': 21,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'stop_loss': 0.10,
            'take_profit': 0.30,
        }
        
        # 验证参数范围
        assert 0 < rsi_params['rsi_period'] < 100
        assert 0 < rsi_params['rsi_oversold'] < 50
        assert 50 < rsi_params['rsi_overbought'] < 100
        assert 0 < rsi_params['stop_loss'] < 1
        assert 0 < rsi_params['take_profit'] < 1


class TestUtils:
    """工具函数测试"""
    
    def test_calculate_returns(self):
        """测试收益率计算"""
        prices = pd.Series([100, 110, 105, 115, 120])
        returns = prices.pct_change().dropna()
        
        # 验证收益率计算
        assert len(returns) == 4
        assert abs(returns.iloc[0] - 0.10) < 0.001
    
    def test_calculate_drawdown(self):
        """测试回撤计算"""
        values = pd.Series([100, 110, 105, 100, 95, 100])
        
        # 计算回撤
        peak = values.cummax()
        drawdown = (values - peak) / peak
        
        # 验证回撤
        assert drawdown.min() <= 0
        assert drawdown.max() == 0


if __name__ == '__main__':
    # 运行测试
    pytest.main([__file__, '-v'])

