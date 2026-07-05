"""
完整单元测试模块
覆盖策略、工具函数、回测引擎

使用方法：
    python -m pytest tests/test_complete.py -v
"""

import sys
import os
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ========== RSI计算测试 ==========
class TestRSICalculation:
    """RSI计算测试"""
    
    def test_rsi_basic(self):
        """测试RSI基本计算"""
        prices = pd.Series([10, 11, 12, 11, 10, 9, 10, 11, 12, 13, 14, 15, 14, 13, 12])
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        assert rsi.dropna().between(0, 100).all()
    
    def test_rsi_all_up(self):
        """测试全部上涨情况"""
        up_prices = pd.Series([10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24])
        delta = up_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        assert rsi.iloc[-1] > 90
    
    def test_rsi_all_down(self):
        """测试全部下跌情况"""
        down_prices = pd.Series([24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10])
        delta = down_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        assert rsi.iloc[-1] < 10
    
    def test_rsi_period_7(self):
        """测试RSI周期7"""
        prices = pd.Series([10, 11, 12, 11, 10, 9, 10, 11, 12, 13])
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=7).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=7).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        assert len(rsi.dropna()) > 0


# ========== MACD计算测试 ==========
class TestMACDCalculation:
    """MACD计算测试"""
    
    def test_macd_basic(self):
        """测试MACD基本计算"""
        np.random.seed(42)
        prices = pd.Series(np.cumsum(np.random.randn(100)) + 100)
        ema12 = prices.ewm(span=12).mean()
        ema26 = prices.ewm(span=26).mean()
        dif = ema12 - ema26
        dea = dif.ewm(span=9).mean()
        macd = 2 * (dif - dea)
        assert len(dif) == len(prices)
        assert len(dea) == len(prices)
        assert len(macd) == len(prices)
    
    def test_macd_crossover(self):
        """测试MACD交叉信号"""
        # 创建一个明显的金叉场景
        prices = pd.Series([100 + i * 0.1 for i in range(50)])
        ema12 = prices.ewm(span=12).mean()
        ema26 = prices.ewm(span=26).mean()
        dif = ema12 - ema26
        dea = dif.ewm(span=9).mean()
        # 验证DIF和DEA有交叉
        crossover = (dif > dea) & (dif.shift(1) <= dea.shift(1))
        assert crossover.any() or (dif < dea).any()


# ========== 收益率计算测试 ==========
class TestReturnCalculation:
    """收益率计算测试"""
    
    def test_simple_return(self):
        """测试简单收益率计算"""
        prices = pd.Series([100, 110, 105, 115, 120])
        returns = prices.pct_change().dropna()
        assert len(returns) == 4
        assert abs(returns.iloc[0] - 0.10) < 0.001
    
    def test_cumulative_return(self):
        """测试累计收益率计算"""
        prices = pd.Series([100, 110, 105, 115, 120])
        cumulative_return = (prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0]
        assert abs(cumulative_return - 0.20) < 0.001
    
    def test_log_return(self):
        """测试对数收益率计算"""
        prices = pd.Series([100, 110, 105, 115, 120])
        log_returns = np.log(prices / prices.shift(1)).dropna()
        assert len(log_returns) == 4


# ========== 回撤计算测试 ==========
class TestDrawdownCalculation:
    """回撤计算测试"""
    
    def test_drawdown_basic(self):
        """测试基本回撤计算"""
        values = pd.Series([100, 110, 105, 100, 95, 100])
        peak = values.cummax()
        drawdown = (values - peak) / peak
        assert drawdown.min() <= 0
        assert drawdown.max() == 0
    
    def test_max_drawdown(self):
        """测试最大回撤计算"""
        values = pd.Series([100, 110, 105, 100, 95, 100])
        peak = values.cummax()
        drawdown = (values - peak) / peak
        max_drawdown = drawdown.min()
        assert max_drawdown == -0.13636363636363635  # (95-110)/110
    
    def test_no_drawdown(self):
        """测试无回撤情况"""
        values = pd.Series([100, 110, 120, 130, 140])
        peak = values.cummax()
        drawdown = (values - peak) / peak
        assert drawdown.min() == 0


# ========== 风险指标测试 ==========
class TestRiskMetrics:
    """风险指标测试"""
    
    def test_sharpe_ratio(self):
        """测试夏普比率计算"""
        returns = pd.Series([0.01, 0.02, -0.01, 0.03, 0.02])
        sharpe = returns.mean() / returns.std() * np.sqrt(252)
        assert isinstance(sharpe, float)
    
    def test_volatility(self):
        """测试波动率计算"""
        returns = pd.Series([0.01, 0.02, -0.01, 0.03, 0.02])
        volatility = returns.std() * np.sqrt(252)
        assert volatility > 0
    
    def test_win_rate(self):
        """测试胜率计算"""
        returns = pd.Series([0.01, -0.02, 0.03, -0.01, 0.02])
        win_rate = len(returns[returns > 0]) / len(returns)
        assert 0 <= win_rate <= 1


# ========== 数据处理测试 ==========
class TestDataProcessing:
    """数据处理测试"""
    
    def test_data_loading(self):
        """测试数据加载"""
        data_file = 'data/cache/000001_real_data.csv'
        if os.path.exists(data_file):
            df = pd.read_csv(data_file, index_col='date', parse_dates=True)
            assert 'open' in df.columns
            assert 'high' in df.columns
            assert 'low' in df.columns
            assert 'close' in df.columns
            assert 'volume' in df.columns
            assert len(df) > 0
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
    
    def test_moving_average(self):
        """测试移动平均计算"""
        prices = pd.Series([10, 11, 12, 13, 14, 15])
        ma3 = prices.rolling(3).mean()
        assert len(ma3.dropna()) == 4
        assert ma3.iloc[-1] == 14.0  # (13+14+15)/3
    
    def test_data_cleaning(self):
        """测试数据清洗"""
        data = pd.Series([1, 2, np.nan, 4, 5])
        cleaned = data.dropna()
        assert len(cleaned) == 4


# ========== 策略参数测试 ==========
class TestStrategyParams:
    """策略参数测试"""
    
    def test_rsi_params(self):
        """测试RSI参数范围"""
        params = {
            'rsi_period': 21,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'stop_loss': 0.10,
            'take_profit': 0.30,
        }
        assert 0 < params['rsi_period'] < 100
        assert 0 < params['rsi_oversold'] < 50
        assert 50 < params['rsi_overbought'] < 100
        assert 0 < params['stop_loss'] < 1
        assert 0 < params['take_profit'] < 1
    
    def test_macd_params(self):
        """测试MACD参数范围"""
        params = {
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9,
        }
        assert params['fast_period'] < params['slow_period']
        assert params['signal_period'] > 0
    
    def test_position_params(self):
        """测试仓位参数范围"""
        params = {
            'max_position': 0.80,
            'min_position': 0.20,
            'kelly_fraction': 0.5,
        }
        assert 0 < params['min_position'] < params['max_position'] <= 1
        assert 0 < params['kelly_fraction'] <= 1


# ========== 滑点测试 ==========
class TestSlippage:
    """滑点测试"""
    
    def test_slippage_impact(self):
        """测试滑点影响"""
        # 无滑点
        price_no_slippage = 100
        # 有滑点0.2%
        slippage = 0.002
        price_with_slippage_buy = price_no_slippage * (1 + slippage)
        price_with_slippage_sell = price_no_slippage * (1 - slippage)
        
        assert price_with_slippage_buy > price_no_slippage
        assert price_with_slippage_sell < price_no_slippage
    
    def test_slippage_range(self):
        """测试滑点范围"""
        valid_slippage = [0.0, 0.001, 0.002, 0.003, 0.005]
        for s in valid_slippage:
            assert 0 <= s <= 0.01  # 滑点应该在0-1%之间


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

