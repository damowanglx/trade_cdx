"""
多因子选股策略
基于多个因子综合打分选股

因子类型：
- 价值因子：PE、PB、PS等
- 成长因子：营收增长率、净利润增长率
- 质量因子：ROE、毛利率
- 动量因子：近期收益率
"""

import backtrader as bt
import pandas as pd
import numpy as np


class MultiFactorStrategy(bt.Strategy):
    """
    多因子选股策略
    
    参数：
    - rebalance_days: 调仓周期（天）
    - top_n: 选择股票数量
    - pe_weight: 市盈率权重
    - pb_weight: 市净率权重
    - roe_weight: ROE权重
    """
    
    params = (
        ('rebalance_days', 20),  # 每20天调仓一次
        ('top_n', 5),            # 选择前5只股票
        ('pe_weight', -0.3),     # PE越低越好（负权重）
        ('pb_weight', -0.3),     # PB越低越好
        ('roe_weight', 0.4),     # ROE越高越好
        ('printlog', True),
    )
    
    def __init__(self):
        """初始化"""
        self.day_count = 0
        self.order_list = []
        
    def log(self, txt, dt=None):
        """日志"""
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt}: {txt}')
    
    def next(self):
        """策略逻辑"""
        self.day_count += 1
        
        # 到达调仓周期
        if self.day_count % self.params.rebalance_days == 0:
            self.rebalance()
    
    def rebalance(self):
        """调仓逻辑"""
        self.log(f'调仓日 - 第{self.day_count}天')
        
        # 这里简化处理，实际需要：
        # 1. 获取所有股票的因子数据
        # 2. 计算综合得分
        # 3. 选择top_n股票
        # 4. 卖出不在名单中的股票
        # 5. 买入新股票
        
        # 示例：简单均值回归策略
        for i, data in enumerate(self.datas):
            if i >= self.params.top_n:
                break
            
            if not self.getposition(data).size:
                # 买入
                size = int(self.broker.getcash() * 0.1 / data.close[0])
                if size > 0:
                    self.buy(data, size=size)
                    self.log(f'买入 {data._name} {size}股')
    
    def stop(self):
        """结束"""
        self.log(f'最终资金: {self.broker.getvalue():.2f}')
