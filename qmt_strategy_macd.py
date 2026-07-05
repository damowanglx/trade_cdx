#coding:gbk
"""
MACD策略 - QMT实盘版本
基于最优参数 MACD(12, 20, 7)

使用方法：
    在QMT中加载此策略
"""

import time
import datetime
import numpy as np

# ========== 策略参数 ==========
FAST_PERIOD = 12
SLOW_PERIOD = 20
SIGNAL_PERIOD = 7
POSITION_RATIO = 0.9  # 仓位比例90%


def init(ContextInfo):
    """初始化函数"""
    ContextInfo.stockcode = ContextInfo.stockcode
    ContextInfo.market = ContextInfo.market
    
    # 策略状态
    ContextInfo.holdings = {}
    ContextInfo.position = 0  # 持仓状态：0=空仓，1=持仓
    ContextInfo.buy_price = 0
    ContextInfo.trade_count = 0
    
    print(f"MACD策略初始化完成")
    print(f"股票: {ContextInfo.stockcode}.{ContextInfo.market}")
    print(f"MACD参数: 快线={FAST_PERIOD}, 慢线={SLOW_PERIOD}, 信号线={SIGNAL_PERIOD}")


def calculate_ema(data, period):
    """计算EMA"""
    if len(data) < period:
        return None
    
    multiplier = 2 / (period + 1)
    ema = data[0]
    
    for price in data[1:]:
        ema = (price - ema) * multiplier + ema
    
    return ema


def calculate_macd(closes, fast=12, slow=26, signal=9):
    """计算MACD"""
    if len(closes) < slow + signal:
        return None, None, None
    
    # 计算快速EMA
    fast_ema = calculate_ema(closes, fast)
    
    # 计算慢速EMA
    slow_ema = calculate_ema(closes, slow)
    
    if fast_ema is None or slow_ema is None:
        return None, None, None
    
    # 计算DIF
    dif = fast_ema - slow_ema
    
    # 计算DEA（信号线）
    # 简化处理：使用最近的DIF值
    dif_values = []
    for i in range(signal):
        idx = len(closes) - signal + i
        fast_ema_i = calculate_ema(closes[:idx+1], fast)
        slow_ema_i = calculate_ema(closes[:idx+1], slow)
        if fast_ema_i and slow_ema_i:
            dif_values.append(fast_ema_i - slow_ema_i)
    
    if len(dif_values) < signal:
        return None, None, None
    
    dea = calculate_ema(dif_values, signal)
    
    # 计算MACD柱
    macd = 2 * (dif - dea)
    
    return dif, dea, macd


def handlebar(ContextInfo):
    """K线处理函数"""
    index = ContextInfo.barpos
    realtime = ContextInfo.get_bar_timetag(index)
    period = ContextInfo.period
    
    # 获取收盘价数据
    close = ContextInfo.get_market_data(['close'], period=period, dividend_type=ContextInfo.dividend_type)
    
    # 检查数据是否足够
    if len(close) < SLOW_PERIOD + SIGNAL_PERIOD:
        return
    
    # 计算MACD
    dif, dea, macd = calculate_macd(close, FAST_PERIOD, SLOW_PERIOD, SIGNAL_PERIOD)
    
    if dif is None or dea is None:
        return
    
    # 绘制MACD指标
    ContextInfo.paint('DIF', dif, -1, 0)
    ContextInfo.paint('DEA', dea, -1, 0)
    ContextInfo.paint('MACD', macd, -1, 0)
    
    # 获取当前价格
    current_price = close[-1]
    
    # 计算前一根K线的DIF和DEA
    if len(close) > SLOW_PERIOD + SIGNAL_PERIOD + 1:
        dif_prev, dea_prev, _ = calculate_macd(close[:-1], FAST_PERIOD, SLOW_PERIOD, SIGNAL_PERIOD)
    else:
        dif_prev, dea_prev = None, None
    
    # ========== 交易逻辑 ==========
    
    # 买入信号：DIF上穿DEA（金叉）且当前空仓
    if dif_prev is not None and dea_prev is not None:
        if dif_prev < dea_prev and dif > dea and ContextInfo.position == 0:
            # 计算可买数量
            cash = ContextInfo.get_cash()
            buy_amount = int(cash * POSITION_RATIO / current_price / 100) * 100
            
            if buy_amount >= 100:
                print(f"买入信号: MACD金叉, DIF={dif:.4f}, DEA={dea:.4f}, 价格={current_price:.2f}")
                order_shares(
                    ContextInfo.stockcode + '.' + ContextInfo.market,
                    buy_amount,
                    "FIX",
                    current_price,
                    ContextInfo,
                    "MACD策略"
                )
                ContextInfo.position = 1
                ContextInfo.buy_price = current_price
                ContextInfo.trade_count += 1
                ContextInfo.draw_text(1, 0.5, f'买入 {current_price:.2f}')
        
        # 卖出信号：DIF下穿DEA（死叉）且当前持仓
        elif dif_prev > dea_prev and dif < dea and ContextInfo.position == 1:
            # 获取持仓数量
            holdings = ContextInfo.get_holdings()
            sell_amount = holdings.get(ContextInfo.stockcode + '.' + ContextInfo.market, 0)
            
            if sell_amount > 0:
                print(f"卖出信号: MACD死叉, DIF={dif:.4f}, DEA={dea:.4f}, 价格={current_price:.2f}")
                order_shares(
                    ContextInfo.stockcode + '.' + ContextInfo.market,
                    -sell_amount,
                    "FIX",
                    current_price,
                    ContextInfo,
                    "MACD策略"
                )
                
                # 计算收益
                profit = (current_price - ContextInfo.buy_price) / ContextInfo.buy_price
                print(f"本次收益: {profit*100:.2f}%")
                
                ContextInfo.position = 0
                ContextInfo.buy_price = 0
                ContextInfo.draw_text(1, 0.6, f'卖出 {current_price:.2f}')
    
    # 绘制持仓状态
    ContextInfo.paint('持仓', ContextInfo.position, -1, 0)
