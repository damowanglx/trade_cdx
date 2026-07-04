"""
实盘交易准备模块
提供券商接口对接和实盘交易功能

使用方法：
    python scripts/prepare_live_trading.py
"""

import sys
import os
import pandas as pd
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def show_broker_options():
    """显示券商接口选项"""
    print("="*60)
    print("实盘交易 - 券商接口选择")
    print("="*60)
    
    print("\n可用的券商接口：\n")
    
    brokers = [
        {
            'name': 'QMT (迅投)',
            'description': '券商官方量化接口，稳定可靠',
            'requirements': '需要开通量化权限，资金门槛低',
            'advantages': ['官方接口，稳定', '支持股票、期货', '有技术支持'],
            'disadvantages': ['需要开通权限', '部分券商不支持'],
        },
        {
            'name': 'PTrade',
            'description': '恒生电子量化平台',
            'requirements': '部分券商支持',
            'advantages': ['功能强大', '支持多策略'],
            'disadvantages': ['券商支持有限'],
        },
        {
            'name': 'easytrader',
            'description': '模拟键鼠操作，非官方接口',
            'requirements': '无门槛',
            'advantages': ['无需开通权限', '免费开源'],
            'disadvantages': ['不稳定', '可能违反券商规定'],
        },
    ]
    
    for i, broker in enumerate(brokers, 1):
        print(f"{i}. {broker['name']}")
        print(f"   描述: {broker['description']}")
        print(f"   要求: {broker['requirements']}")
        print(f"   优点: {', '.join(broker['advantages'])}")
        print(f"   缺点: {', '.join(broker['disadvantages'])}")
        print()
    
    print("="*60)


def show_trading_checklist():
    """显示实盘交易检查清单"""
    print("\n" + "="*60)
    print("实盘交易检查清单")
    print("="*60)
    
    checklist = [
        ("开通券商账户", "选择支持量化交易的券商"),
        ("开通量化权限", "联系券商客户经理申请"),
        ("安装交易软件", "QMT/PTrade等"),
        ("配置API密钥", "在credentials.py中配置"),
        ("小资金测试", "先用1-2万测试"),
        ("监控交易", "设置报警，及时处理异常"),
        ("逐步增加资金", "验证稳定后再增加"),
    ]
    
    print("\n请完成以下步骤：\n")
    for i, (step, desc) in enumerate(checklist, 1):
        print(f"[ ] {i}. {step}")
        print(f"      {desc}")
    
    print("\n" + "="*60)


def show_risk_warning():
    """显示风险提示"""
    print("\n" + "="*60)
    print("风险提示")
    print("="*60)
    
    warnings = [
        "量化交易存在风险，回测结果不代表未来收益",
        "建议先用模拟盘测试，再投入实盘",
        "初期建议小资金测试，逐步增加",
        "策略需要定期优化，市场环境会变化",
        "设置止损止盈，控制风险",
        "不要把所有资金投入单一策略",
    ]
    
    print("\n重要提醒：\n")
    for warning in warnings:
        print(f"* {warning}")
    
    print("\n" + "="*60)


def create_live_config():
    """创建实盘配置文件"""
    print("\n" + "="*60)
    print("创建实盘配置文件")
    print("="*60)
    
    config_content = '''"""
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
'''
    
    os.makedirs('config', exist_ok=True)
    with open('config/live_trading.py', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("\n配置文件已创建: config/live_trading.py")
    print("\n请修改配置文件中的券商信息和交易参数")


def main():
    """主函数"""
    print("="*60)
    print("量化交易系统 - 实盘准备")
    print("="*60)
    
    # 显示券商选项
    show_broker_options()
    
    # 显示检查清单
    show_trading_checklist()
    
    # 显示风险提示
    show_risk_warning()
    
    # 创建配置文件
    create_live_config()
    
    print("\n" + "="*60)
    print("下一步操作")
    print("="*60)
    print("""
1. 选择券商并开通量化权限
2. 修改 config/live_trading.py 配置文件
3. 先用模拟盘测试1-2周
4. 小资金实盘测试（1-2万）
5. 验证稳定后逐步增加资金
    """)
    
    print("="*60)
    print("实盘准备完成！")
    print("="*60)


if __name__ == '__main__':
    main()
