#coding:gbk
"""
RSI策略 - QMT完整版
包含完整的风控、仓位管理、日志记录

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
STOP_LOSS = 0.10          # 止损10%
TAKE_PROFIT = 0.30        # 止盈30%
MAX_POSITION = 0.80       # 最大仓位80%
MIN_POSITION = 0.20       # 最小仓位20%


def init(ContextInfo):
    """初始化函数"""
    # 股票信息
    ContextInfo.stockcode = ContextInfo.stockcode
    ContextInfo.market = ContextInfo.market
    
    # 策略状态
    ContextInfo.position = 0  # 持仓状态：0=空仓，1=持仓
    ContextInfo.buy_price = 0
    ContextInfo.buy_date = None
    ContextInfo.trade_count = 0
    
    # 风控参数
    ContextInfo.stop_loss = STOP_LOSS
    ContextInfo.take_profit = TAKE_PROFIT
    ContextInfo.max_position = MAX_POSITION
    ContextInfo.min_position = MIN_POSITION
    
    # 日志
    ContextInfo.log_file = f"D:\\workspace\\trade_cdx\\logs\\trade_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    log_message(ContextInfo, "策略初始化完成")
    log_message(ContextInfo, f"股票: {ContextInfo.stockcode}.{ContextInfo.market}")
    log_message(ContextInfo, f"RSI参数: 周期={RSI_PERIOD}, 超卖={RSI_OVERSOLD}, 超买={RSI_OVERBOUGHT}")
    log_message(ContextInfo, f"风控参数: 止损={STOP_LOSS*100}%, 止盈={TAKE_PROFIT*100}%")
    log_message(ContextInfo, f"仓位范围: {MIN_POSITION*100}% - {MAX_POSITION*100}%")


def log_message(ContextInfo, message):
    """记录日志"""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {message}\n"
    
    # 打印到控制台
    print(log_line.strip())
    
    # 写入文件
    try:
        with open(ContextInfo.log_file, 'a', encoding='utf-8') as f:
            f.write(log_line)
    except:
        pass


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


def calculate_position_size(ContextInfo, current_price):
    """计算仓位大小"""
    # 获取凯利公式仓位（简化版）
    kelly_fraction = 0.5  # 默认50%
    
    # 根据RSI强度调整
    rsi = calculate_rsi_from_context(ContextInfo)
    if rsi is not None:
        if rsi < 20:  # 极度超卖，加大仓位
            kelly_fraction = 0.7
        elif rsi < 30:  # 超卖
            kelly_fraction = 0.6
        elif rsi > 80:  # 极度超买，减小仓位
            kelly_fraction = 0.3
        elif rsi > 70:  # 超买
            kelly_fraction = 0.4
    
    # 限制仓位范围
    kelly_fraction = max(ContextInfo.min_position, 
                        min(kelly_fraction, ContextInfo.max_position))
    
    # 计算可买数量
    cash = ContextInfo.get_cash()
    size = int(cash * kelly_fraction / current_price / 100) * 100
    
    return size, kelly_fraction


def calculate_rsi_from_context(ContextInfo):
    """从ContextInfo计算RSI"""
    try:
        close = ContextInfo.get_market_data(['close'], period=ContextInfo.period, 
                                           dividend_type=ContextInfo.dividend_type)
        if len(close) > RSI_PERIOD + 1:
            return calculate_rsi(close, RSI_PERIOD)
    except:
        pass
    return None


def handlebar(ContextInfo):
    """K线处理函数"""
    # 获取当前K线索引
    index = ContextInfo.barpos
    realtime = ContextInfo.get_bar_timetag(index)
    period = ContextInfo.period
    
    # 获取收盘价数据
    close = ContextInfo.get_market_data(['close'], period=period, 
                                       dividend_type=ContextInfo.dividend_type)
    
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
    
    # 持仓检查：止损止盈
    if ContextInfo.position == 1:
        # 计算收益率
        profit_pct = (current_price - ContextInfo.buy_price) / ContextInfo.buy_price
        
        # 止损检查
        if profit_pct <= -ContextInfo.stop_loss:
            log_message(ContextInfo, f"触发止损: {profit_pct*100:.2f}% <= -{ContextInfo.stop_loss*100}%")
            sell_all(ContextInfo, current_price, "止损")
            return
        
        # 止盈检查
        if profit_pct >= ContextInfo.take_profit:
            log_message(ContextInfo, f"触发止盈: {profit_pct*100:.2f}% >= {ContextInfo.take_profit*100}%")
            sell_all(ContextInfo, current_price, "止盈")
            return
        
        # RSI超买卖出
        if rsi > RSI_OVERBOUGHT:
            log_message(ContextInfo, f"RSI超买: {rsi:.2f} > {RSI_OVERBOUGHT}")
            sell_all(ContextInfo, current_price, "RSI超买")
            return
    
    # 空仓检查：买入信号
    elif ContextInfo.position == 0:
        if rsi < RSI_OVERSOLD:
            # 计算仓位
            size, position_fraction = calculate_position_size(ContextInfo, current_price)
            
            if size >= 100:
                log_message(ContextInfo, f"RSI超卖买入: RSI={rsi:.2f}, 价格={current_price:.2f}, "
                           f"数量={size}, 仓位={position_fraction*100:.1f}%")
                buy_stock(ContextInfo, current_price, size)
                return
    
    # 绘制持仓状态
    ContextInfo.paint('持仓', ContextInfo.position, -1, 0)


def buy_stock(ContextInfo, price, size):
    """买入股票"""
    symbol = ContextInfo.stockcode + '.' + ContextInfo.market
    order_shares(symbol, size, "FIX", price, ContextInfo, "RSI策略")
    
    ContextInfo.position = 1
    ContextInfo.buy_price = price
    ContextInfo.buy_date = datetime.datetime.now()
    ContextInfo.trade_count += 1
    
    log_message(ContextInfo, f"买入成功: {symbol} @ {price:.2f} x {size}")


def sell_all(ContextInfo, price, reason):
    """卖出所有持仓"""
    symbol = ContextInfo.stockcode + '.' + ContextInfo.market
    holdings = ContextInfo.get_holdings()
    sell_amount = holdings.get(symbol, 0)
    
    if sell_amount > 0:
        order_shares(symbol, -sell_amount, "FIX", price, ContextInfo, "RSI策略")
        
        # 计算收益
        profit = (price - ContextInfo.buy_price) / ContextInfo.buy_price
        
        log_message(ContextInfo, f"卖出成功: {symbol} @ {price:.2f} x {sell_amount}")
        log_message(ContextInfo, f"卖出原因: {reason}")
        log_message(ContextInfo, f"本次收益: {profit*100:.2f}%")
        
        ContextInfo.position = 0
        ContextInfo.buy_price = 0
        ContextInfo.buy_date = None
