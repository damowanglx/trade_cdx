#coding:gbk
"""
RSI策略 - QMT实盘版本
基于最优参数 RSI(21, 30, 70)

使用方法：
    在QMT中加载此策略
"""

import time
import datetime
import numpy as np

# ========== 策略参数 ==========
RSI_PERIOD = 21
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
POSITION_RATIO = 0.9  # 仓位比例90%


def init(ContextInfo):
    """初始化函数"""
    # 设置交易股票
    ContextInfo.stockcode = ContextInfo.stockcode
    ContextInfo.market = ContextInfo.market
    
    # 策略状态
    ContextInfo.holdings = {}
    ContextInfo.position = 0  # 持仓状态：0=空仓，1=持仓
    ContextInfo.buy_price = 0
    ContextInfo.trade_count = 0
    
    # RSI计算缓存
    ContextInfo.rsi_values = []
    
    print(f"RSI策略初始化完成")
    print(f"股票: {ContextInfo.stockcode}.{ContextInfo.market}")
    print(f"RSI参数: 周期={RSI_PERIOD}, 超卖={RSI_OVERSOLD}, 超买={RSI_OVERBOUGHT}")


def calculate_rsi(closes, period=14):
    """计算RSI指标"""
    if len(closes) < period + 1:
        return None
    
    # 计算价格变化
    deltas = np.diff(closes)
    
    # 分离上涨和下跌
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    # 计算平均上涨和下跌
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    
    # 避免除零
    if avg_loss == 0:
        return 100
    
    # 计算RS和RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def handlebar(ContextInfo):
    """K线处理函数"""
    # 获取当前K线索引
    index = ContextInfo.barpos
    realtime = ContextInfo.get_bar_timetag(index)
    period = ContextInfo.period
    
    # 获取收盘价数据
    close = ContextInfo.get_market_data(['close'], period=period, dividend_type=ContextInfo.dividend_type)
    
    # 检查数据是否足够
    if len(close) < RSI_PERIOD + 1:
        return
    
    # 计算RSI
    rsi = calculate_rsi(close, RSI_PERIOD)
    
    if rsi is None:
        return
    
    # 绘制RSI指标
    ContextInfo.paint('RSI', rsi, -1, 0)
    ContextInfo.paint('超卖线', RSI_OVERSOLD, -1, 0)
    ContextInfo.paint('超买线', RSI_OVERBOUGHT, -1, 0)
    
    # 获取当前价格
    current_price = close[-1]
    
    # ========== 交易逻辑 ==========
    
    # 买入信号：RSI低于超卖阈值且当前空仓
    if rsi < RSI_OVERSOLD and ContextInfo.position == 0:
        # 计算可买数量
        cash = ContextInfo.get_cash()
        buy_amount = int(cash * POSITION_RATIO / current_price / 100) * 100
        
        if buy_amount >= 100:
            print(f"买入信号: RSI={rsi:.2f}, 价格={current_price:.2f}, 数量={buy_amount}")
            order_shares(
                ContextInfo.stockcode + '.' + ContextInfo.market,
                buy_amount,
                "FIX",
                current_price,
                ContextInfo,
                "RSI策略"
            )
            ContextInfo.position = 1
            ContextInfo.buy_price = current_price
            ContextInfo.trade_count += 1
            ContextInfo.draw_text(1, 0.5, f'买入 {current_price:.2f}')
    
    # 卖出信号：RSI高于超买阈值且当前持仓
    elif rsi > RSI_OVERBOUGHT and ContextInfo.position == 1:
        # 获取持仓数量
        holdings = ContextInfo.get_holdings()
        sell_amount = holdings.get(ContextInfo.stockcode + '.' + ContextInfo.market, 0)
        
        if sell_amount > 0:
            print(f"卖出信号: RSI={rsi:.2f}, 价格={current_price:.2f}, 数量={sell_amount}")
            order_shares(
                ContextInfo.stockcode + '.' + ContextInfo.market,
                -sell_amount,
                "FIX",
                current_price,
                ContextInfo,
                "RSI策略"
            )
            
            # 计算收益
            profit = (current_price - ContextInfo.buy_price) / ContextInfo.buy_price
            print(f"本次收益: {profit*100:.2f}%")
            
            ContextInfo.position = 0
            ContextInfo.buy_price = 0
            ContextInfo.draw_text(1, 0.6, f'卖出 {current_price:.2f}')
    
    # 绘制持仓状态
    ContextInfo.paint('持仓', ContextInfo.position, -1, 0)
