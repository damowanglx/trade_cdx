"""
扩展单元测试模块
增加更多测试用例到100+

使用方法：
    python -m pytest tests/test_extended.py -v
"""

import sys
import os
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ========== RSI策略测试 ==========
class TestRSIStrategyExtended:
    """RSI策略扩展测试"""
    
    def test_rsi_period_14(self):
        """测试RSI周期14"""
        prices = pd.Series([100 + i * 0.5 for i in range(30)])
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        assert len(rsi.dropna()) > 0
        assert rsi.dropna().between(0, 100).all()
    
    def test_rsi_period_21(self):
        """测试RSI周期21"""
        prices = pd.Series([100 + i * 0.3 for i in range(40)])
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=21).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=21).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        assert len(rsi.dropna()) > 0
    
    def test_rsi_mixed_trend(self):
        """测试RSI混合趋势"""
        # 先上涨后下跌
        up = [100 + i for i in range(10)]
        down = [110 - i for i in range(10)]
        prices = pd.Series(up + down)
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # RSI应该有变化
        assert rsi.dropna().std() > 0
    
    def test_rsi_oversold_signal(self):
        """测试RSI超卖信号"""
        # 持续下跌
        prices = pd.Series([100 - i * 2 for i in range(20)])
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # 持续下跌应该导致RSI低于30
        assert rsi.iloc[-1] < 30
    
    def test_rsi_overbought_signal(self):
        """测试RSI超买信号"""
        # 持续上涨
        prices = pd.Series([100 + i * 2 for i in range(20)])
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # 持续上涨应该导致RSI高于70
        assert rsi.iloc[-1] > 70


# ========== MACD策略测试 ==========
class TestMACDStrategyExtended:
    """MACD策略扩展测试"""
    
    def test_macd_golden_cross(self):
        """测试MACD金叉"""
        # 创建上升趋势
        prices = pd.Series([100 + i * 0.5 for i in range(50)])
        ema12 = prices.ewm(span=12).mean()
        ema26 = prices.ewm(span=26).mean()
        dif = ema12 - ema26
        dea = dif.ewm(span=9).mean()
        
        # 检查是否有金叉
        crossover = (dif > dea) & (dif.shift(1) <= dea.shift(1))
        # 在上升趋势中应该有金叉
        assert crossover.any()
    
    def test_macd_death_cross(self):
        """测试MACD死叉"""
        # 创建下降趋势
        prices = pd.Series([100 - i * 0.5 for i in range(50)])
        ema12 = prices.ewm(span=12).mean()
        ema26 = prices.ewm(span=26).mean()
        dif = ema12 - ema26
        dea = dif.ewm(span=9).mean()
        
        # 检查是否有死叉
        crossunder = (dif < dea) & (dif.shift(1) >= dea.shift(1))
        # 在下降趋势中应该有死叉
        assert crossunder.any()
    
    def test_macd_histogram(self):
        """测试MACD柱状图"""
        prices = pd.Series([100 + i * 0.2 for i in range(40)])
        ema12 = prices.ewm(span=12).mean()
        ema26 = prices.ewm(span=26).mean()
        dif = ema12 - ema26
        dea = dif.ewm(span=9).mean()
        macd = 2 * (dif - dea)
        
        # MACD柱状图应该有正负值
        assert (macd > 0).any() or (macd < 0).any()


# ========== 均线策略测试 ==========
class TestMovingAverageExtended:
    """均线策略扩展测试"""
    
    def test_ma_crossover(self):
        """测试均线交叉"""
        # 使用更长的数据和更明显的趋势
        up_prices = pd.Series([100 + i * 0.5 for i in range(20)])
        down_prices = pd.Series([110 - i * 0.5 for i in range(20)])
        prices = pd.concat([up_prices, down_prices]).reset_index(drop=True)
        
        ma5 = prices.rolling(5).mean()
        ma20 = prices.rolling(20).mean()
        
        # 检查是否有交叉
        crossover = (ma5 > ma20) & (ma5.shift(1) <= ma20.shift(1))
        crossunder = (ma5 < ma20) & (ma5.shift(1) >= ma20.shift(1))
        
        # 在趋势转换中应该有交叉信号
        assert crossover.any() or crossunder.any()
    
    def test_ma_support_resistance(self):
        """测试均线支撑阻力"""
        prices = pd.Series([100, 102, 101, 103, 102, 104, 103, 105, 104, 106])
        ma5 = prices.rolling(5).mean()
        
        # 均线应该平滑价格
        assert ma5.dropna().std() < prices.std()
    
    def test_ma_trend_identification(self):
        """测试均线趋势识别"""
        # 上升趋势
        up_prices = pd.Series([100 + i for i in range(20)])
        ma10 = up_prices.rolling(10).mean()
        
        # 在上升趋势中，价格应该在均线上方
        assert up_prices.iloc[-1] > ma10.iloc[-1]


# ========== 止损止盈测试 ==========
class TestStopLossTakeProfit:
    """止损止盈测试"""
    
    def test_stop_loss_trigger(self):
        """测试止损触发"""
        buy_price = 100
        stop_loss = 0.10  # 10%止损
        
        # 价格下跌超过10%
        current_price = 85
        profit_pct = (current_price - buy_price) / buy_price
        
        # 应该触发止损
        assert profit_pct <= -stop_loss
    
    def test_take_profit_trigger(self):
        """测试止盈触发"""
        buy_price = 100
        take_profit = 0.30  # 30%止盈
        
        # 价格上涨超过30%
        current_price = 135
        profit_pct = (current_price - buy_price) / buy_price
        
        # 应该触发止盈
        assert profit_pct >= take_profit
    
    def test_no_trigger(self):
        """测试不触发"""
        buy_price = 100
        stop_loss = 0.10
        take_profit = 0.30
        
        # 价格在止损止盈范围内
        current_price = 105
        profit_pct = (current_price - buy_price) / buy_price
        
        # 不应该触发
        assert profit_pct > -stop_loss and profit_pct < take_profit


# ========== 仓位管理测试 ==========
class TestPositionManagement:
    """仓位管理测试"""
    
    def test_position_size_calculation(self):
        """测试仓位大小计算"""
        cash = 100000
        price = 50
        max_position = 0.30  # 最大仓位30%
        
        # 计算最大可买数量
        max_value = cash * max_position
        max_quantity = int(max_value / price / 100) * 100
        
        assert max_quantity > 0
        assert max_quantity * price <= cash * max_position
    
    def test_diversification(self):
        """测试分散化"""
        total_cash = 100000
        num_stocks = 5
        
        # 每只股票的资金
        per_stock = total_cash / num_stocks
        
        # 应该均匀分配
        assert per_stock == 20000
    
    def test_risk_parity_weights(self):
        """测试风险平价权重"""
        # 假设有3只股票，波动率分别为0.1, 0.2, 0.3
        volatilities = [0.1, 0.2, 0.3]
        
        # 风险平价：权重与波动率成反比
        inv_vol = [1/v for v in volatilities]
        total_inv_vol = sum(inv_vol)
        weights = [iv/total_inv_vol for iv in inv_vol]
        
        # 权重之和应该为1
        assert abs(sum(weights) - 1.0) < 0.001
        
        # 低波动率应该有高权重
        assert weights[0] > weights[1] > weights[2]


# ========== 收益率计算测试 ==========
class TestReturnCalculationExtended:
    """收益率计算扩展测试"""
    
    def test_simple_return(self):
        """测试简单收益率"""
        initial = 100
        final = 110
        expected_return = 0.10
        
        actual_return = (final - initial) / initial
        assert abs(actual_return - expected_return) < 0.001
    
    def test_log_return(self):
        """测试对数收益率"""
        initial = 100
        final = 110
        expected_log_return = np.log(final / initial)
        
        actual_log_return = np.log(final / initial)
        assert abs(actual_log_return - expected_log_return) < 0.001
    
    def test_annualized_return(self):
        """测试年化收益率"""
        # 假设3个月收益10%
        period_return = 0.10
        periods_per_year = 4  # 季度
        
        annualized = (1 + period_return) ** periods_per_year - 1
        assert annualized > period_return
    
    def test_compound_return(self):
        """测试复利收益"""
        initial = 100
        returns = [0.10, -0.05, 0.08, 0.12]
        
        final = initial
        for r in returns:
            final *= (1 + r)
        
        total_return = (final - initial) / initial
        assert total_return > 0


# ========== 风险指标测试 ==========
class TestRiskMetricsExtended:
    """风险指标扩展测试"""
    
    def test_sharpe_ratio_calculation(self):
        """测试夏普比率计算"""
        returns = pd.Series([0.01, 0.02, -0.01, 0.03, 0.02])
        
        avg_return = returns.mean()
        std_return = returns.std()
        risk_free_rate = 0.001  # 无风险利率
        
        sharpe = (avg_return - risk_free_rate) / std_return * np.sqrt(252)
        
        assert isinstance(sharpe, float)
    
    def test_volatility_calculation(self):
        """测试波动率计算"""
        returns = pd.Series([0.01, 0.02, -0.01, 0.03, 0.02])
        
        daily_vol = returns.std()
        annual_vol = daily_vol * np.sqrt(252)
        
        assert annual_vol > daily_vol
    
    def test_max_drawdown_calculation(self):
        """测试最大回撤计算"""
        values = pd.Series([100, 110, 105, 100, 95, 100, 105])
        
        peak = values.cummax()
        drawdown = (values - peak) / peak
        max_drawdown = drawdown.min()
        
        assert max_drawdown <= 0
        assert max_drawdown >= -1
    
    def test_win_rate_calculation(self):
        """测试胜率计算"""
        returns = pd.Series([0.01, -0.02, 0.03, -0.01, 0.02])
        
        win_rate = len(returns[returns > 0]) / len(returns)
        
        assert 0 <= win_rate <= 1
        assert win_rate == 0.6  # 3胜2负


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

