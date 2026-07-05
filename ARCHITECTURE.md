# 量化交易系统架构文档

## 1. 系统概述

本系统是一个完整的量化交易系统，支持数据获取、策略开发、回测验证、实盘交易等全流程。

## 2. 模块划分

### 2.1 数据层（data/）

```
data/
├── fetcher/          # 数据获取
│   ├── baostock_api.py
│   ├── akshare_api.py
│   └── tushare_api.py
├── quality/          # 数据质量
│   └── data_quality_monitor.py
├── updater/          # 数据更新
│   └── data_updater.py
├── utils/            # 数据工具
│   └── data_utils.py
└── cache/            # 数据缓存
```

**职责：**
- 获取股票数据
- 数据质量监控
- 数据更新管理
- 数据清洗转换

### 2.2 策略层（strategy/）

```
strategy/
├── rsi_strategy.py           # RSI策略
├── macd_strategy.py          # MACD策略
├── ma_cross.py               # 均线策略
├── turtle_strategy.py        # 海龟策略
├── mean_reversion_strategy.py # 均值回归策略
├── bollinger_strategy.py     # 布林带策略
├── kdj_strategy.py           # KDJ策略
├── atr_strategy.py           # ATR策略
├── portfolio_strategy.py     # 策略组合
├── multi_factor.py           # 多因子策略
└── risk_manager.py           # 风险管理
```

**职责：**
- 实现交易策略
- 生成交易信号
- 仓位管理
- 风险控制

### 2.3 回测层（backtest/）

```
backtest/
├── engine.py           # 回测引擎
├── optimizer.py        # 参数优化器
├── performance.py      # 性能优化器
└── report.py           # 报告生成器
```

**职责：**
- 执行回测
- 参数优化
- 性能分析
- 报告生成

### 2.4 风控层（risk/）

```
risk/
├── var_calculator.py   # VaR风险价值
└── stress_test.py      # 压力测试
```

**职责：**
- 风险价值计算
- 压力测试
- 风险监控

### 2.5 监控层（monitor/）

```
monitor/
├── alert_manager.py    # 报警管理器
├── email_alert.py      # 邮件报警
└── trade_monitor.py    # 交易监控
```

**职责：**
- 实时监控
- 报警通知
- 日志记录

### 2.6 工具层（utils/）

```
utils/
├── security.py         # 安全工具
├── logger.py           # 日志工具
├── common.py           # 公共函数
└── error_handler.py    # 错误处理
```

**职责：**
- 安全管理
- 日志记录
- 公共函数
- 错误处理

### 2.7 配置层（config/）

```
config/
├── settings.py         # 全局设置
├── trading_100k.py     # 交易配置
├── email_config.py     # 邮箱配置
├── config_manager.py   # 配置管理器
└── validator/          # 配置验证
```

**职责：**
- 配置管理
- 配置验证
- 环境变量

## 3. 数据流

```
数据获取 → 数据清洗 → 策略计算 → 信号生成 → 风险检查 → 订单执行 → 监控报警
```

## 4. 模块依赖

```
config/ ← utils/ ← data/ ← strategy/ ← backtest/ ← risk/ ← monitor/
```

## 5. 扩展点

### 5.1 添加新策略
1. 在 `strategy/` 目录创建新文件
2. 继承 `bt.Strategy` 类
3. 实现 `__init__` 和 `next` 方法
4. 添加参数配置

### 5.2 添加新数据源
1. 在 `data/fetcher/` 目录创建新文件
2. 实现数据获取接口
3. 遵循统一的数据格式

### 5.3 添加新风控规则
1. 在 `risk/` 目录创建新文件
2. 实现风险计算接口
3. 集成到回测引擎

## 6. 测试策略

- **单元测试**：测试单个函数
- **集成测试**：测试模块间交互
- **性能测试**：测试系统性能
- **压力测试**：测试极端情况

## 7. 部署架构

```
┌─────────────────────────────────────┐
│           Docker Container          │
├─────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────┐ │
│  │  数据层  │  │  策略层  │  │监控层│ │
│  └─────────┘  └─────────┘  └─────┘ │
│  ┌─────────┐  ┌─────────┐  ┌─────┐ │
│  │  回测层  │  │  风控层  │  │工具层│ │
│  └─────────┘  └─────────┘  └─────┘ │
└─────────────────────────────────────┘
```
