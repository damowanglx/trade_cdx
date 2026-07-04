"""
可视化工具模块
用于绘制K线图、均线、回测结果等
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import FancyBboxPatch
import numpy as np


class Visualizer:
    """可视化工具类"""
    
    def __init__(self, style='seaborn-v0_8-darkgrid'):
        """
        初始化可视化工具
        
        Args:
            style: matplotlib样式
        """
        try:
            plt.style.use(style)
        except:
            plt.style.use('default')
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
    
    def plot_kline(self, df, title='K线图', save_path=None):
        """
        绘制K线图（简化版，用柱状图表示）
        
        Args:
            df: DataFrame，需包含 open, high, low, close 列
            title: 图表标题
            save_path: 保存路径
        """
        fig, ax = plt.subplots(figsize=(14, 7))
        
        # 计算涨跌
        up = df[df['close'] >= df['open']]
        down = df[df['close'] < df['open']]
        
        # 绘制上涨K线（红色）
        ax.bar(up.index, up['close'] - up['open'], bottom=up['open'], 
               color='red', alpha=0.8, width=0.6)
        ax.bar(up.index, up['high'] - up['close'], bottom=up['close'], 
               color='red', alpha=0.3, width=0.1)
        ax.bar(up.index, up['open'] - up['low'], bottom=up['low'], 
               color='red', alpha=0.3, width=0.1)
        
        # 绘制下跌K线（绿色）
        ax.bar(down.index, down['close'] - down['open'], bottom=down['open'], 
               color='green', alpha=0.8, width=0.6)
        ax.bar(down.index, down['high'] - down['open'], bottom=down['open'], 
               color='green', alpha=0.3, width=0.1)
        ax.bar(down.index, down['close'] - down['low'], bottom=down['low'], 
               color='green', alpha=0.3, width=0.1)
        
        ax.set_title(title, fontsize=16)
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('价格', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # 格式化x轴日期
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"图表已保存到: {save_path}")
        
        plt.show()
    
    def plot_with_ma(self, df, ma_periods=[5, 20, 60], title='K线图与均线', save_path=None):
        """
        绘制K线图和均线
        
        Args:
            df: DataFrame，需包含 close 列
            ma_periods: 均线周期列表
            title: 图表标题
            save_path: 保存路径
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), 
                                        gridspec_kw={'height_ratios': [3, 1]})
        
        # 绘制收盘价
        ax1.plot(df.index, df['close'], label='收盘价', color='black', linewidth=1.5)
        
        # 绘制均线
        colors = ['blue', 'orange', 'purple', 'green']
        for i, period in enumerate(ma_periods):
            ma = df['close'].rolling(period).mean()
            ax1.plot(df.index, ma, label=f'MA{period}', 
                    color=colors[i % len(colors)], linewidth=1, alpha=0.8)
        
        ax1.set_title(title, fontsize=16)
        ax1.set_ylabel('价格', fontsize=12)
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # 绘制成交量
        if 'vol' in df.columns:
            ax2.bar(df.index, df['vol'], color='gray', alpha=0.5)
            ax2.set_ylabel('成交量', fontsize=12)
            ax2.grid(True, alpha=0.3)
        
        # 格式化x轴
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"图表已保存到: {save_path}")
        
        plt.show()
    
    def plot_backtest_result(self, portfolio_values, benchmark_values=None, 
                             title='回测结果', save_path=None):
        """
        绘制回测结果
        
        Args:
            portfolio_values: 策略净值序列
            benchmark_values: 基准净值序列（可选）
            title: 图表标题
            save_path: 保存路径
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10),
                                        gridspec_kw={'height_ratios': [3, 1]})
        
        # 绘制净值曲线
        ax1.plot(portfolio_values.index, portfolio_values, 
                label='策略净值', color='blue', linewidth=2)
        
        if benchmark_values is not None:
            ax1.plot(benchmark_values.index, benchmark_values, 
                    label='基准净值', color='gray', linewidth=1, alpha=0.7)
        
        ax1.set_title(title, fontsize=16)
        ax1.set_ylabel('净值', fontsize=12)
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # 计算并绘制回撤
        drawdown = (portfolio_values - portfolio_values.cummax()) / portfolio_values.cummax()
        ax2.fill_between(drawdown.index, drawdown, 0, color='red', alpha=0.3)
        ax2.set_ylabel('回撤', fontsize=12)
        ax2.set_xlabel('日期', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        # 格式化x轴
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"图表已保存到: {save_path}")
        
        plt.show()
    
    def plot_returns_distribution(self, returns, title='收益率分布', save_path=None):
        """
        绘制收益率分布图
        
        Args:
            returns: 收益率序列
            title: 图表标题
            save_path: 保存路径
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 绘制直方图
        ax.hist(returns, bins=50, color='blue', alpha=0.7, edgecolor='black')
        
        # 添加统计信息
        mean_return = returns.mean()
        std_return = returns.std()
        ax.axvline(mean_return, color='red', linestyle='--', linewidth=2, label=f'均值: {mean_return:.4f}')
        ax.axvline(mean_return + 2*std_return, color='orange', linestyle='--', 
                  linewidth=1, label=f'+2σ: {mean_return + 2*std_return:.4f}')
        ax.axvline(mean_return - 2*std_return, color='orange', linestyle='--', 
                  linewidth=1, label=f'-2σ: {mean_return - 2*std_return:.4f}')
        
        ax.set_title(title, fontsize=16)
        ax.set_xlabel('收益率', fontsize=12)
        ax.set_ylabel('频数', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"图表已保存到: {save_path}")
        
        plt.show()


# 使用示例
if __name__ == '__main__':
    # 创建示例数据
    dates = pd.date_range('2025-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    # 生成模拟价格数据
    close = 100 + np.cumsum(np.random.randn(100) * 2)
    open_price = close + np.random.randn(100)
    high = np.maximum(close, open_price) + abs(np.random.randn(100))
    low = np.minimum(close, open_price) - abs(np.random.randn(100))
    volume = np.random.randint(1000, 10000, 100)
    
    df = pd.DataFrame({
        'open': open_price,
        'high': high,
        'low': low,
        'close': close,
        'vol': volume
    }, index=dates)
    
    # 创建可视化工具
    viz = Visualizer()
    
    # 绘制K线图
    viz.plot_with_ma(df, ma_periods=[5, 20], title='示例股票K线图')

