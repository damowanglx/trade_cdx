# 全局配置文件

# Tushare API配置
TUSHARE_TOKEN = "你的token"  # 请替换为你的Tushare Pro Token

# 数据库配置
DATABASE_URL = "sqlite:///data/trade.db"

# 回测配置
BACKTEST_CONFIG = {
    "initial_cash": 200000,  # 初始资金20万
    "commission": 0.001,     # 手续费千分之一
    "slippage": 0.001,       # 滑点千分之一
}

# 风控配置
RISK_CONFIG = {
    "max_drawdown": 0.15,    # 最大回撤15%
    "max_position": 0.5,     # 最大仓位50%
    "stop_loss": 0.08,       # 止损8%
    "take_profit": 0.20,     # 止盈20%
}

# 策略参数
STRATEGY_CONFIG = {
    "ma_short": 5,           # 短期均线周期
    "ma_long": 20,           # 长期均线周期
    "rsi_period": 14,        # RSI周期
    "rsi_oversold": 30,      # RSI超卖阈值
    "rsi_overbought": 70,    # RSI超买阈值
}

