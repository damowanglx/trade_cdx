"""
风控模块
控制交易风险，保护资金安全

风控规则：
- 最大回撤限制
- 单笔交易止损
- 单笔交易止盈
- 最大仓位限制
- 每日最大亏损
"""

import backtrader as bt


class RiskManager:
    """风控管理器"""
    
    def __init__(self, 
                 max_drawdown=0.15,
                 stop_loss=0.08,
                 take_profit=0.20,
                 max_position=0.5,
                 max_daily_loss=0.03):
        """
        初始化风控参数
        
        Args:
            max_drawdown: 最大回撤限制（15%）
            stop_loss: 止损比例（8%）
            take_profit: 止盈比例（20%）
            max_position: 最大仓位比例（50%）
            max_daily_loss: 每日最大亏损（3%）
        """
        self.max_drawdown = max_drawdown
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.max_position = max_position
        self.max_daily_loss = max_daily_loss
        
        self.peak_value = 0
        self.daily_start_value = 0
        self.current_date = None
        
    def update_peak(self, current_value):
        """更新峰值"""
        if current_value > self.peak_value:
            self.peak_value = current_value
    
    def check_drawdown(self, current_value):
        """检查回撤是否超限"""
        if self.peak_value == 0:
            return True
        
        drawdown = (self.peak_value - current_value) / self.peak_value
        return drawdown < self.max_drawdown
    
    def get_drawdown(self, current_value):
        """获取当前回撤"""
        if self.peak_value == 0:
            return 0
        return (self.peak_value - current_value) / self.peak_value
    
    def check_stop_loss(self, entry_price, current_price):
        """检查是否触发止损"""
        if entry_price == 0:
            return False
        loss = (entry_price - current_price) / entry_price
        return loss >= self.stop_loss
    
    def check_take_profit(self, entry_price, current_price):
        """检查是否触发止盈"""
        if entry_price == 0:
            return False
        profit = (current_price - entry_price) / entry_price
        return profit >= self.take_profit
    
    def check_position_size(self, position_value, total_value):
        """检查仓位是否超限"""
        if total_value == 0:
            return False
        position_pct = position_value / total_value
        return position_pct < self.max_position
    
    def get_max_position_size(self, total_value, price):
        """计算最大可买数量"""
        max_invest = total_value * self.max_position
        return int(max_invest / price)
    
    def check_daily_loss(self, current_value, date):
        """检查每日亏损是否超限"""
        if self.current_date != date:
            self.current_date = date
            self.daily_start_value = current_value
            return True
        
        if self.daily_start_value == 0:
            return True
        
        daily_loss = (self.daily_start_value - current_value) / self.daily_start_value
        return daily_loss < self.max_daily_loss


class RiskManagedStrategy(bt.Strategy):
    """带风控的策略基类"""
    
    params = (
        ('max_drawdown', 0.15),
        ('stop_loss', 0.08),
        ('take_profit', 0.20),
        ('max_position', 0.5),
        ('printlog', True),
    )
    
    def __init__(self):
        """初始化"""
        self.risk_manager = RiskManager(
            max_drawdown=self.params.max_drawdown,
            stop_loss=self.params.stop_loss,
            take_profit=self.params.take_profit,
            max_position=self.params.max_position
        )
        self.entry_prices = {}
        
    def log(self, txt, dt=None):
        """日志"""
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt}: {txt}')
    
    def buy_with_risk(self, data, size=None):
        """带风控的买入"""
        # 检查回撤
        current_value = self.broker.getvalue()
        if not self.risk_manager.check_drawdown(current_value):
            drawdown = self.risk_manager.get_drawdown(current_value)
            self.log(f'风控: 回撤超限 ({drawdown:.2%}), 暂停买入')
            return None
        
        # 检查仓位
        if not self.risk_manager.check_position_size(
            self.broker.getvalue() * self.params.max_position,
            self.broker.getvalue()
        ):
            self.log('风控: 仓位超限, 暂停买入')
            return None
        
        # 计算仓位大小
        if size is None:
            size = self.risk_manager.get_max_position_size(
                self.broker.getvalue(),
                data.close[0]
            )
        
        if size > 0:
            order = self.buy(data, size=size)
            self.entry_prices[data._name] = data.close[0]
            return order
        
        return None
    
    def sell_with_risk(self, data):
        """带风控的卖出"""
        position = self.getposition(data)
        if position.size > 0:
            # 检查止损
            entry_price = self.entry_prices.get(data._name, 0)
            if self.risk_manager.check_stop_loss(entry_price, data.close[0]):
                self.log(f'风控: 触发止损 - {data._name}')
                return self.sell(data, size=position.size)
            
            # 检查止盈
            if self.risk_manager.check_take_profit(entry_price, data.close[0]):
                self.log(f'风控: 触发止盈 - {data._name}')
                return self.sell(data, size=position.size)
        
        return None
    
    def next(self):
        """子类实现"""
        # 更新峰值
        self.risk_manager.update_peak(self.broker.getvalue())
        
        # 检查每日亏损
        current_date = self.datas[0].datetime.date(0)
        if not self.risk_manager.check_daily_loss(self.broker.getvalue(), current_date):
            self.log('风控: 每日亏损超限, 暂停交易')
            return
