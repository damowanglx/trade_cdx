"""
实盘交易配置
请根据实际情况修改以下配置
"""

# ========== 券商配置 ==========
# QMT配置（示例）
QMT_CONFIG = {
    'account': '你的资金账号',
    'password': '你的密码',
    'broker': '你的券商名称',
}

# ========== 策略配置 ==========
# RSI策略最优参数
RSI_CONFIG = {
    'rsi_period': 21,
    'rsi_oversold': 30,
    'rsi_overbought': 70,
}

# MACD策略最优参数
MACD_CONFIG = {
    'fast_period': 12,
    'slow_period': 20,
    'signal_period': 7,
}

# ========== 风控配置 ==========
RISK_CONFIG = {
    'max_position': 0.5,      # 最大仓位50%
    'stop_loss': 0.08,        # 止损8%
    'take_profit': 0.20,      # 止盈20%
    'max_daily_loss': 0.03,   # 每日最大亏损3%
}

# ========== 交易股票列表 ==========
# 选择流动性好、市值大的股票
STOCK_LIST = [
    'sz.000001',  # 平安银行
    'sh.600036',  # 招商银行
    'sh.600519',  # 贵州茅台
    'sz.000858',  # 五粮液
    'sz.300750',  # 宁德时代
]
