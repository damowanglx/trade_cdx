# 量化交易系统 - Quant Trading System

一个完整的A股量化交易系统，支持数据获取、策略回测、参数优化、信号预警。

## 功能特性

- **数据获取**: 支持Baostock、AKShare、ClickHouse等数据源
- **策略开发**: 内置RSI、MACD、海龟、布林带、KDJ等策略
- **参数优化**: 网格搜索、Walk-Forward验证
- **回测引擎**: 完整的回测框架，支持多策略比较
- **信号预警**: 自动扫描全市场，推送买卖信号
- **风控模块**: VaR风险价值、止损止盈、仓位管理

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行信号预警

```bash
# 使用本地数据扫描（推荐）
python scripts/run_local_scan_fast.py

# 使用ClickHouse扫描（需要数据服务）
python scripts/run_clickhouse_scan.py

# 精选推荐（只推荐5只）
python scripts/run_top_picks.py
```

### 3. 运行回测

```bash
# 单股票回测
python scripts/run_backtest.py

# 全量回测
python scripts/run_full_strategy_backtest.py

# 参数优化
python scripts/run_optimization.py
```

## 项目结构

```
trade_cdx/
├── config/                    # 配置文件
├── data/                      # 数据模块
│   ├── fetcher/              # 数据获取
│   ├── quality/              # 数据质量检查
│   ├── cache/                # 数据缓存
│   └── all_stocks/           # 全量股票数据
├── strategy/                  # 策略模块
│   ├── rsi_strategy.py       # RSI策略
│   ├── macd_strategy.py      # MACD策略
│   ├── turtle_strategy.py    # 海龟策略
│   ├── bollinger_strategy.py # 布林带策略
│   ├── kdj_strategy.py       # KDJ策略
│   └── optimizer/            # 策略优化
├── backtest/                  # 回测模块
│   ├── engine.py             # 回测引擎
│   ├── optimizer.py          # 参数优化器
│   ├── realism/              # 回测真实性
│   └── report/               # 报告生成
├── risk/                      # 风控模块
│   ├── var_calculator.py     # VaR风险价值
│   ├── stress_test.py        # 压力测试
│   └── risk_control.py       # 风险控制
├── trading/                   # 交易模块
│   ├── simulator.py          # 模拟交易
│   └── order/                # 订单管理
├── monitor/                   # 监控模块
│   ├── alert_manager.py      # 报警管理
│   └── trade_monitor.py      # 交易监控
├── utils/                     # 工具模块
│   ├── logger.py             # 日志模块
│   ├── security.py           # 安全模块
│   └── common.py             # 公共函数
├── scripts/                   # 运行脚本
├── tests/                     # 测试代码
├── logs/                      # 日志目录
└── reports/                   # 报告目录
```

## 策略说明

### RSI策略
- **参数**: RSI周期=21, 超卖=30, 超买=70
- **信号**: RSI<30买入, RSI>70卖出
- **止损**: 10%
- **止盈**: 30%

### MACD策略
- **参数**: 快线=12, 慢线=26, 信号线=9
- **信号**: 金叉买入, 死叉卖出
- **止损**: 10%
- **止盈**: 30%

### 海龟策略
- **参数**: 入场周期=20, 出场周期=10
- **信号**: 突破最高价买入, 跌破最低价卖出
- **仓位**: ATR动态仓位管理

## 数据源

### 本地数据
- 数据位置: `data/all_stocks/`
- 股票数量: 5,129只
- 时间范围: 2020-2025年

### ClickHouse
- 地址: http://localhost:8123
- 用户: quant
- 密码: quant123
- 库名: quant

## 风险控制

- **止损**: 10%
- **止盈**: 30%
- **最大回撤**: 15%
- **单只仓位**: 最大30%
- **总仓位**: 最大80%

## 邮箱配置

编辑 `config/email_config.py`:

```python
EMAIL_CONFIG = {
    'smtp_server': 'smtp.163.com',
    'smtp_port': 465,
    'sender_email': 'your_email@163.com',
    'sender_password': 'your_password',
    'receiver_email': 'your_email@163.com',
}
```

## 学习资源

- [量化交易项目方案.md](./量化交易项目方案.md)
- [学习路线_4周入门.md](./学习路线_4周入门.md)
- [50个优化点.md](./50个优化点.md)

## 风险提示

1. 量化交易存在风险，回测结果不代表未来收益
2. 建议先用模拟盘测试，再投入实盘
3. 初期建议小资金测试，逐步增加
4. 策略需要定期优化，市场环境会变化

## 许可证

MIT License
