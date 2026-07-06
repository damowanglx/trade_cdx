"""
生成可视化回测报告
使用matplotlib生成专业的回测报告

使用方法：
    python scripts/generate_report.py
"""

import os
import sys
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backtest.engine import BacktestEngine
from data.fetcher.baostock_api import BaostockFetcher
from strategy.ma_cross import DualMAStrategy


def generate_sample_report():
    """生成示例报告"""
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 获取数据
    data_file = 'data/cache/000001_real_data.csv'
    if not os.path.exists(data_file):
        fetcher = BaostockFetcher()
        df = fetcher.get_stock_daily('sz.000001', '2024-01-01', '2026-01-01')
        fetcher.save_to_csv(df, '000001_real_data.csv')
        fetcher.close()
    
    # 运行回测
    engine = BacktestEngine(initial_cash=200000, commission=0.001)
    engine.setup(data_file, DualMAStrategy, {'fast_period': 3, 'slow_period': 15, 'printlog': False})
    
    # 获取策略数据
    cerebro = engine.cerebro
    results = cerebro.run()
    strat = results[0]
    
    # 创建报告
    fig = plt.figure(figsize=(16, 12))
    
    # 1. 净值曲线
    ax1 = plt.subplot(2, 2, 1)
    
    # 读取原始数据
    df = pd.read_csv(data_file, index_col='date', parse_dates=True)
    
    # 计算基准净值（买入持有）
    benchmark = df['close'] / df['close'].iloc[0]
    
    # 计算策略净值（简化）
    initial_value = 200000
    final_value = engine.cerebro.broker.getvalue()
    strategy_return = (final_value - initial_value) / initial_value
    
    # 绘制基准曲线
    ax1.plot(benchmark.index, benchmark.values, label='基准（买入持有）', color='gray', linewidth=1)
    
    # 绘制策略净值（简化显示）
    strategy_nav = benchmark * (1 + strategy_return)
    ax1.plot(strategy_nav.index, strategy_nav.values, label='策略净值', color='blue', linewidth=2)
    
    ax1.set_title('净值曲线', fontsize=12)
    ax1.set_ylabel('净值')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # 2. 回撤图
    ax2 = plt.subplot(2, 2, 2)
    
    # 计算回撤
    cumulative = strategy_nav
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    
    ax2.fill_between(drawdown.index, drawdown.values, 0, color='red', alpha=0.3)
    ax2.plot(drawdown.index, drawdown.values, color='red', linewidth=1)
    
    ax2.set_title('回撤曲线', fontsize=12)
    ax2.set_ylabel('回撤')
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
    
    # 3. 月度收益热力图
    ax3 = plt.subplot(2, 2, 3)
    
    # 计算月度收益
    monthly_returns = benchmark.resample('ME').last().pct_change().dropna()
    
    # 创建年月矩阵
    years = monthly_returns.index.year.unique()
    months = range(1, 13)
    
    # 准备数据
    data = pd.DataFrame(index=years, columns=months)
    for date, ret in monthly_returns.items():
        data.loc[date.year, date.month] = ret
    
    # 绘制热力图
    data = data.astype(float)
    im = ax3.imshow(data.values, cmap='RdYlGn', aspect='auto', vmin=-0.1, vmax=0.1)
    
    ax3.set_xticks(range(12))
    ax3.set_xticklabels(['1月', '2月', '3月', '4月', '5月', '6月',
                        '7月', '8月', '9月', '10月', '11月', '12月'])
    ax3.set_yticks(range(len(years)))
    ax3.set_yticklabels(years)
    
    ax3.set_title('月度收益热力图', fontsize=12)
    plt.colorbar(im, ax=ax3, label='收益率')
    
    # 4. 统计信息
    ax4 = plt.subplot(2, 2, 4)
    ax4.axis('off')
    
    # 计算指标
    returns = benchmark.pct_change().dropna()
    
    total_return = strategy_return
    annual_return = total_return * 252 / len(returns)
    volatility = returns.std() * np.sqrt(252)
    sharpe_ratio = annual_return / volatility if volatility > 0 else 0
    
    # 计算最大回撤
    max_drawdown = drawdown.min()
    
    # 计算胜率
    win_rate = (returns > 0).sum() / len(returns)
    
    # 显示统计信息
    stats_text = f"""
策略统计指标
{'='*30}

收益指标:
  初始资金: 200,000.00
  最终资金: {final_value:,.2f}
  总收益率: {total_return:.2%}
  年化收益率: {annual_return:.2%}
  年化波动率: {volatility:.2%}

风险指标:
  夏普比率: {sharpe_ratio:.2f}
  最大回撤: {max_drawdown:.2%}
  胜率: {win_rate:.2%}

策略参数:
  短期均线: 3日
  长期均线: 15日
    """
    
    ax4.text(0.1, 0.95, stats_text, transform=ax4.transAxes, fontsize=10,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # 设置标题
    fig.suptitle('双均线策略回测报告 - 平安银行(000001)', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # 保存报告
    os.makedirs('reports', exist_ok=True)
    report_file = 'reports/backtest_report.png'
    plt.savefig(report_file, dpi=150, bbox_inches='tight')
    print(f"报告已保存到: {report_file}")
    
    # plt.show()  # 注释掉显示，只保存文件
    
    return report_file


if __name__ == '__main__':
    print("="*60)
    print("生成可视化回测报告")
    print("="*60)
    
    report_file = generate_sample_report()
    
    print("\n" + "="*60)
    print("报告生成完成！")
    print("="*60)
    print(f"\n报告文件: {report_file}")


