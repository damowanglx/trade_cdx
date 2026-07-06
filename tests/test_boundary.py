"""
边界条件测试模块
测试边界值和异常情况

使用方法：
    python -m pytest tests/test_boundary.py -v
"""

import sys
import os
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestBoundaryConditions:
    """边界条件测试"""
    
    def test_empty_dataframe(self):
        """测试空DataFrame"""
        df = pd.DataFrame()
        assert len(df) == 0
    
    def test_single_row_dataframe(self):
        """测试单行DataFrame"""
        df = pd.DataFrame({'close': [100]})
        assert len(df) == 1
    
    def test_zero_price(self):
        """测试零价格"""
        prices = pd.Series([0, 100, 200])
        returns = prices.pct_change()
        # 零价格会导致无穷大
        assert np.isinf(returns.iloc[1]) or np.isnan(returns.iloc[1])
    
    def test_negative_price(self):
        """测试负价格"""
        prices = pd.Series([-10, 100, 200])
        returns = prices.pct_change()
        # 负价格应该被处理
        assert len(returns) == 3
    
    def test_extreme_values(self):
        """测试极端值"""
        prices = pd.Series([1e-10, 1e10, 1e-10])
        returns = prices.pct_change()
        # 极端值应该被处理
        assert len(returns) == 3
    
    def test_constant_price(self):
        """测试恒定价格"""
        prices = pd.Series([100, 100, 100, 100, 100])
        returns = prices.pct_change()
        # 恒定价格收益率应该为0
        assert (returns.dropna() == 0).all()
    
    def test_monotonic_increase(self):
        """测试单调递增"""
        prices = pd.Series([100, 110, 120, 130, 140])
        returns = prices.pct_change()
        # 单调递增应该有正收益率
        assert (returns.dropna() > 0).all()
    
    def test_monotonic_decrease(self):
        """测试单调递减"""
        prices = pd.Series([140, 130, 120, 110, 100])
        returns = prices.pct_change()
        # 单调递减应该有负收益率
        assert (returns.dropna() < 0).all()


class TestRSIBoundary:
    """RSI边界测试"""
    
    def test_rsi_with_constant_price(self):
        """测试恒定价格的RSI"""
        prices = pd.Series([100] * 20)
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # 恒定价格RSI应该是50
        assert abs(rsi.iloc[-1] - 50) < 0.01
    
    def test_rsi_with_all_up(self):
        """测试全部上涨的RSI"""
        prices = pd.Series([100 + i for i in range(20)])
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # 全部上涨RSI应该接近100
        assert rsi.iloc[-1] > 90
    
    def test_rsi_with_all_down(self):
        """测试全部下跌的RSI"""
        prices = pd.Series([100 - i for i in range(20)])
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # 全部下跌RSI应该接近0
        assert rsi.iloc[-1] < 10


class TestMACDBoundary:
    """MACD边界测试"""
    
    def test_macd_with_constant_price(self):
        """测试恒定价格的MACD"""
        prices = pd.Series([100] * 50)
        ema12 = prices.ewm(span=12).mean()
        ema26 = prices.ewm(span=26).mean()
        dif = ema12 - ema26
        dea = dif.ewm(span=9).mean()
        
        # 恒定价格DIF和DEA应该接近0
        assert abs(dif.iloc[-1]) < 0.01
        assert abs(dea.iloc[-1]) < 0.01


class TestStopLossBoundary:
    """止损边界测试"""
    
    def test_exact_stop_loss(self):
        """测试精确止损"""
        buy_price = 100
        stop_loss = 0.10
        current_price = 90  # 正好下跌10%
        
        profit_pct = (current_price - buy_price) / buy_price
        assert profit_pct == -stop_loss
    
    def test_just_above_stop_loss(self):
        """测试刚好不触发止损"""
        buy_price = 100
        stop_loss = 0.10
        current_price = 90.01  # 下跌9.99%
        
        profit_pct = (current_price - buy_price) / buy_price
        assert profit_pct > -stop_loss
    
    def test_just_below_stop_loss(self):
        """测试刚好触发止损"""
        buy_price = 100
        stop_loss = 0.10
        current_price = 89.99  # 下跌10.01%
        
        profit_pct = (current_price - buy_price) / buy_price
        assert profit_pct < -stop_loss


class TestTakeProfitBoundary:
    """止盈边界测试"""
    
    def test_exact_take_profit(self):
        """测试精确止盈"""
        buy_price = 100
        take_profit = 0.30
        current_price = 130  # 正好上涨30%
        
        profit_pct = (current_price - buy_price) / buy_price
        assert profit_pct == take_profit
    
    def test_just_above_take_profit(self):
        """测试刚好触发止盈"""
        buy_price = 100
        take_profit = 0.30
        current_price = 130.01  # 上涨30.01%
        
        profit_pct = (current_price - buy_price) / buy_price
        assert profit_pct > take_profit
    
    def test_just_below_take_profit(self):
        """测试刚好不触发止盈"""
        buy_price = 100
        take_profit = 0.30
        current_price = 129.99  # 上涨29.99%
        
        profit_pct = (current_price - buy_price) / buy_price
        assert profit_pct < take_profit


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
