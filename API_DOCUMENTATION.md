# 量化交易系统 API文档

## 目录

1. [数据模块](#数据模块)
2. [策略模块](#策略模块)
3. [回测模块](#回测模块)
4. [监控模块](#监控模块)
5. [工具模块](#工具模块)

---

## 数据模块

### DataUtils (data/utils/data_utils.py)

数据处理工具类，提供数据验证、清洗、转换功能。

#### 方法

##### validate_data(df, required_columns=None)
验证数据完整性

**参数：**
- `df` (DataFrame): 数据
- `required_columns` (list): 必需的列名列表

**返回：**
- `dict`: 验证结果，包含 is_valid, errors, warnings

**示例：**
```python
from data.utils.data_utils import DataUtils

df = pd.read_csv('data.csv')
result = DataUtils.validate_data(df, required_columns=['open', 'high', 'low', 'close'])
if result['is_valid']:
    print("数据验证通过")
```

---

## 策略模块

### RSIStrategy (strategy/rsi_strategy.py)

RSI策略，基于相对强弱指标进行交易。

**参数：**
- `rsi_period` (int): RSI周期，默认21
- `rsi_oversold` (int): 超卖阈值，默认30
- `rsi_overbought` (int): 超买阈值，默认70
- `stop_loss` (float): 止损比例，默认0.10
- `take_profit` (float): 止盈比例，默认0.30

**示例：**
```python
from strategy.rsi_strategy import RSIStrategy

cerebro.addstrategy(RSIStrategy, rsi_period=21, stop_loss=0.10)
```

---

## 回测模块

### BacktestEngine (backtest/engine.py)

回测引擎，支持滑点模拟和基准对比。

**参数：**
- `initial_cash` (float): 初始资金，默认200000
- `commission` (float): 手续费率，默认0.001
- `slippage` (float): 滑点率，默认0.002

**示例：**
```python
from backtest.engine import BacktestEngine

engine = BacktestEngine(initial_cash=100000, slippage=0.002)
engine.setup('data.csv', RSIStrategy)
result = engine.run()
```

---

## 监控模块

### AlertManager (monitor/alert_manager.py)

报警管理器，支持邮件和企业微信报警。

**方法：**
- `configure_email(sender, password, receiver)`: 配置邮箱
- `send_trade_signal(type, symbol, price, quantity, reason)`: 发送交易信号
- `send_risk_alert(type, message)`: 发送风险报警
- `send_daily_report(value, return, positions)`: 发送每日报告

**示例：**
```python
from monitor.alert_manager import AlertManager

alert = AlertManager()
alert.configure_email('xxx@163.com', 'password', 'xxx@163.com')
alert.send_trade_signal('买入', '000001.SZ', 10.5, 1000, 'RSI超卖')
```

---

## 工具模块

### SecurityUtils (utils/security.py)

安全工具类，提供敏感信息保护和输入验证。

**方法：**
- `mask_sensitive_info(text)`: 脱敏敏感信息
- `validate_input(value, type, min, max)`: 验证输入
- `hash_data(data)`: 数据哈希

**示例：**
```python
from utils.security import SecurityUtils

# 脱敏邮箱
masked = SecurityUtils.mask_sensitive_info("联系邮箱：test@example.com")
# 输出：联系邮箱：tes******om

# 验证输入
is_valid = SecurityUtils.validate_input(100, int, min_value=0, max_value=1000)
```

---

## 配置说明

### 邮箱配置 (config/email_config.py)

```python
EMAIL_CONFIG = {
    'smtp_server': 'smtp.163.com',
    'smtp_port': 465,
    'sender_email': 'xxx@163.com',
    'sender_password': '授权码',
    'receiver_email': 'xxx@163.com',
}
```

### 交易配置 (config/trading_100k.py)

```python
INITIAL_CAPITAL = 100000  # 初始资金
POSITION_CONFIG = {
    'max_position': 0.30,  # 单只股票最大仓位
    'max_stocks': 5,       # 最多持有股票数
}
RISK_CONFIG = {
    'max_drawdown': 0.15,  # 最大回撤限制
    'stop_loss': 0.10,     # 止损比例
    'take_profit': 0.30,   # 止盈比例
}
```
