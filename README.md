# 量化交易系统 - trade_cdx

一个完整的A股量化交易系统，支持数据获取、策略回测、参数优化、模拟交易。

## 功能特性

- **数据获取**: 支持Baostock、AKShare等免费数据源
- **策略开发**: 内置双均线、RSI、MACD等多种经典策略
- **参数优化**: 网格搜索优化策略参数
- **回测引擎**: 完整的回测框架，支持多策略比较
- **可视化报告**: 生成专业的回测报告
- **模拟交易**: 模拟真实交易环境测试策略
- **风控模块**: 内置止损、止盈、仓位管理

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行数据获取

```bash
python scripts/01_data_analysis_baostock.py
```

### 3. 运行策略回测

```bash
python scripts/run_full_backtest.py
```

### 4. 参数优化

```bash
python scripts/run_optimization.py
```

### 5. 模拟交易

```bash
python scripts/run_simulation.py
```

### 6. 生成报告

```bash
python scripts/generate_report.py
```

## 项目结构

```
trade_cdx/
├── config/                    # 配置文件
│   ├── settings.py           # 全局配置
│   └── credentials.py        # API密钥
│
├── data/                      # 数据层
│   ├── fetcher/              # 数据获取模块
│   │   ├── baostock_api.py   # Baostock数据源
│   │   ├── akshare_api.py    # AKShare数据源
│   │   └── visualizer.py     # 可视化工具
│   └── cache/                # 数据缓存
│
├── strategy/                  # 策略模块
│   ├── ma_cross.py           # 双均线策略
│   ├── rsi_strategy.py       # RSI策略
│   ├── macd_strategy.py      # MACD策略
│   ├── multi_factor.py       # 多因子选股
│   └── risk_manager.py       # 风控模块
│
├── backtest/                  # 回测模块
│   ├── engine.py             # 回测引擎
│   ├── optimizer.py          # 参数优化器
│   └── report.py             # 报告生成器
│
├── trading/                   # 交易模块
│   └── simulator.py          # 模拟交易系统
│
├── monitor/                   # 监控模块
│   └── trade_monitor.py      # 交易监控
│
├── scripts/                   # 运行脚本
│   ├── run_full_backtest.py  # 完整回测
│   ├── run_optimization.py   # 参数优化
│   ├── run_simulation.py     # 模拟交易
│   └── generate_report.py    # 生成报告
│
├── logs/                      # 日志目录
├── reports/                   # 报告目录
│
├── requirements.txt           # 依赖包
└── README.md                  # 项目说明
```

## 内置策略

### 1. 双均线策略 (ma_cross.py)
- **逻辑**: 短期均线上穿长期均线买入，下穿卖出
- **参数**: fast_period, slow_period
- **最优参数**: fast_period=3, slow_period=15 (收益率36.69%)

### 2. RSI策略 (rsi_strategy.py)
- **逻辑**: RSI低于超卖阈值买入，高于超买阈值卖出
- **参数**: rsi_period, rsi_oversold, rsi_overbought
- **最优参数**: rsi_period=7, rsi_oversold=25, rsi_overbought=80 (收益率27.51%)

### 3. MACD策略 (macd_strategy.py)
- **逻辑**: MACD金叉买入，死叉卖出
- **参数**: fast_period, slow_period, signal_period
- **最优参数**: fast_period=8, slow_period=20, signal_period=7 (收益率31.41%)

## 回测结果（平安银行 2024-2025）

| 策略 | 收益率 | 夏普比率 | 最优参数 |
|------|--------|----------|----------|
| 双均线 | 36.69% | 1.10 | (3, 15) |
| MACD | 31.41% | 1.12 | (8, 20, 7) |
| RSI | 27.51% | 1.14 | (7, 25, 80) |

## 学习资源

- [量化交易项目方案.md](./量化交易项目方案.md) - 详细方案文档
- [学习路线_4周入门.md](./学习路线_4周入门.md) - 学习路线图

## 数据源

### Baostock（推荐）
- 完全免费，无需注册
- 基于TCP连接，稳定可靠
- 支持A股日线、周线、月线数据

### AKShare
- 完全免费，无需注册
- 支持A股、港股、美股
- 数据丰富，接口友好

## 风险提示

1. 量化交易存在风险，回测结果不代表未来收益
2. 建议先用模拟盘测试，再投入实盘
3. 初期建议小资金测试，逐步增加
4. 策略需要定期优化，市场环境会变化

## 开发环境

- Python 3.9+
- 操作系统: Windows/macOS/Linux

## 依赖包

```
pandas>=1.5.0
numpy>=1.23.0
backtrader>=1.9.78
baostock>=0.8.8
akshare>=1.10.0
matplotlib>=3.6.0
loguru>=0.6.0
schedule>=1.2.0
```

## 许可证

MIT License

## 联系方式

如有问题，欢迎提Issue或PR。
