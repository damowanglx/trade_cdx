"""
实盘交易准备脚本
准备1-2万资金的小资金实盘测试

使用方法：
    python scripts/prepare_live_trading_v2.py
"""

import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_live_trading_config():
    """创建实盘交易配置"""
    print("=== 创建实盘交易配置 ===")
    
    config = {
        'version': '1.0',
        'created_at': datetime.now().isoformat(),
        
        # 资金配置
        'capital': {
            'initial': 20000,  # 初始资金2万
            'max_position_pct': 0.30,  # 单只股票最大仓位30%
            'max_stocks': 5,  # 最多持有5只股票
        },
        
        # 策略配置
        'strategy': {
            'name': 'RSI',
            'params': {
                'rsi_period': 21,
                'rsi_oversold': 30,
                'rsi_overbought': 70,
                'stop_loss': 0.10,
                'take_profit': 0.30,
            }
        },
        
        # 风控配置
        'risk': {
            'max_drawdown': 0.15,  # 最大回撤15%
            'daily_loss_limit': 0.03,  # 每日最大亏损3%
            'position_limit': 0.30,  # 单只股票仓位限制
        },
        
        # 股票池
        'stock_pool': [
            '000001.SZ',  # 平安银行
            '600036.SH',  # 招商银行
            '600519.SH',  # 贵州茅台
            '000858.SZ',  # 五粮液
            '300750.SZ',  # 宁德时代
        ],
        
        # 监控配置
        'monitor': {
            'email_alert': True,
            'alert_on_trade': True,
            'alert_on_risk': True,
            'daily_report': True,
        },
        
        # 交易时间
        'trading_hours': {
            'start': '09:30',
            'end': '15:00',
            'timezone': 'Asia/Shanghai',
        }
    }
    
    # 保存配置
    os.makedirs('config', exist_ok=True)
    with open('config/live_trading_v2.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print("[OK] 实盘配置已创建: config/live_trading_v2.json")
    
    # 打印配置摘要
    print("\n配置摘要:")
    print(f"  初始资金: {config['capital']['initial']:,}")
    print(f"  策略: {config['strategy']['name']}")
    print(f"  参数: {config['strategy']['params']}")
    print(f"  股票池: {len(config['stock_pool'])}只")
    print(f"  最大回撤: {config['risk']['max_drawdown']*100}%")
    
    return config


def create_trading_checklist():
    """创建交易检查清单"""
    print("\n=== 交易检查清单 ===")
    
    checklist = """
# 实盘交易检查清单

## 交易前检查
- [ ] QMT交易端已启动
- [ ] 已登录国金证券账户
- [ ] 资金已到位（2万）
- [ ] 策略配置正确
- [ ] 风控参数设置
- [ ] 邮箱报警配置

## 股票选择
- [ ] 流动性好（日均成交额>1亿）
- [ ] 市值大（>100亿）
- [ ] 波动适中（年化波动率20-40%）
- [ ] 基本面良好

## 策略配置
- [ ] RSI参数：21/30/70
- [ ] 止损：10%
- [ ] 止盈：30%
- [ ] 仓位：单只最大30%

## 风控设置
- [ ] 最大回撤：15%
- [ ] 每日亏损限制：3%
- [ ] 单笔亏损限制：10%

## 监控配置
- [ ] 邮箱报警开启
- [ ] 交易信号报警
- [ ] 风险报警
- [ ] 每日报告

## 交易记录
- [ ] 记录每笔交易
- [ ] 分析盈亏原因
- [ ] 定期复盘总结
"""
    
    with open('config/trading_checklist.md', 'w', encoding='utf-8') as f:
        f.write(checklist)
    
    print("[OK] 交易检查清单已创建: config/trading_checklist.md")
    print("\n请按照清单逐项检查！")


def main():
    """主函数"""
    print("="*60)
    print("实盘交易准备")
    print("="*60)
    print(f"准备时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 创建配置
    config = create_live_trading_config()
    
    # 创建检查清单
    create_trading_checklist()
    
    print("\n" + "="*60)
    print("实盘交易准备完成！")
    print("="*60)
    print("\n下一步：")
    print("1. 按照检查清单逐项检查")
    print("2. 启动QMT交易端")
    print("3. 加载RSI策略")
    print("4. 配置交易股票")
    print("5. 开始小资金测试")
    print("\n风险提醒：")
    print("- 初期投入1-2万资金")
    print("- 设置止损止盈")
    print("- 监控策略运行")
    print("- 记录交易日志")


if __name__ == '__main__':
    main()
