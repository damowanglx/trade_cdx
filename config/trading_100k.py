"""
10万资金实盘配置
"""

# ========== 资金配置 ==========
INITIAL_CAPITAL = 100000  # 初始资金10万

# ========== 策略参数 ==========
# RSI策略最优参数
RSI_CONFIG = {
    'rsi_period': 21,
    'rsi_oversold': 30,
    'rsi_overbought': 70,
    'stop_loss': 0.10,      # 止损10%
    'take_profit': 0.30,    # 止盈30%
}

# MACD策略最优参数
MACD_CONFIG = {
    'fast_period': 12,
    'slow_period': 20,
    'signal_period': 7,
    'stop_loss': 0.10,
    'take_profit': 0.30,
}

# ========== 仓位管理 ==========
POSITION_CONFIG = {
    'max_position': 0.30,      # 单只股票最大仓位30%（3万）
    'min_position': 0.10,      # 单只股票最小仓位10%（1万）
    'max_stocks': 5,           # 最多持有5只股票
    'min_stocks': 3,           # 最少持有3只股票
    'kelly_fraction': 0.5,     # 凯利公式保守系数
}

# ========== 风险控制 ==========
RISK_CONFIG = {
    'max_drawdown': 0.15,      # 最大回撤15%（1.5万）
    'daily_loss_limit': 0.03,  # 每日最大亏损3%（3000）
    'slippage': 0.002,         # 滑点0.2%
    'commission': 0.001,       # 手续费0.1%
}

# ========== 交易股票池 ==========
# 选择流动性好、市值大的蓝筹股
STOCK_POOL = [
    # 银行股
    'sz.000001',  # 平安银行
    'sh.600036',  # 招商银行
    'sh.601398',  # 工商银行
    
    # 白酒股
    'sh.600519',  # 贵州茅台
    'sz.000858',  # 五粮液
    
    # 科技股
    'sz.000725',  # 京东方A
    'sz.002415',  # 海康威视
    
    # 新能源
    'sz.300750',  # 宁德时代
    'sz.002594',  # 比亚迪
    
    # 医药
    'sh.600276',  # 恒瑞医药
]

# ========== 调仓配置 ==========
REBALANCE_CONFIG = {
    'rebalance_days': 20,      # 调仓周期20天
    'rebalance_time': '15:00', # 调仓时间（收盘前）
}

# ========== 监控配置 ==========
MONITOR_CONFIG = {
    'enable_email': True,      # 启用邮件报警
    'enable_wechat': False,    # 暂不启用微信
    'email_receiver': 'your_email@example.com',  # 接收邮箱
}

# ========== QMT配置 ==========
QMT_CONFIG = {
    'qmt_path': r'D:\国金QMT\国金证券QMT交易端',
    'strategy_file': 'qmt_strategy_rsi_complete.py',
}
