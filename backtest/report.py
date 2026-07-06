"""
可视化报告模块
生成专业的回测报告

功能：
- 净值曲线
- 回撤图
- 月度收益热力图
- 交易统计图
- 综合报告
"""

import os
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, output_dir='reports'):
        """
        初始化
        
        Args:
            output_dir: 报告输出目录
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
    def generate_full_report(self, portfolio_values, benchmark_values=None, 
                             trades=None, title='策略回测报告'):
        """
        生成完整报告
        
        Args:
            portfolio_values: 策略净值序列（pandas Series）
            benchmark_values: 基准净值序列（可选）
            trades: 交易记录列表（可选）
            title: 报告标题
        """
        # 创建图表
        fig = plt.figure(figsize=(16, 20))
        
        # 1. 净值曲线
        ax1 = plt.subplot(3, 2, 1)
        self._plot_equity_curve(ax1, portfolio_values, benchmark_values)
        
        # 2. 回撤图
        ax2 = plt.subplot(3, 2, 2)
        self._plot_drawdown(ax2, portfolio_values)
        
        # 3. 月度收益热力图
        ax3 = plt.subplot(3, 2, (3, 4))
        self._plot_monthly_returns(ax3, portfolio_values)
        
        # 4. 收益分布
        ax4 = plt.subplot(3, 2, 5)
        self._plot_returns_distribution(ax4, portfolio_values)
        
        # 5. 统计信息
        ax5 = plt.subplot(3, 2, 6)
        self._plot_statistics(ax5, portfolio_values)
        
        # 设置标题
        fig.suptitle(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        # 保存报告
        filename = os.path.join(self.output_dir, f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"报告已保存到: {filename}")
        
        plt.show()
        
        return filename
    
    def _plot_equity_curve(self, ax, portfolio_values, benchmark_values=None):
        """绘制净值曲线"""
        # 计算净值
        portfolio_nav = portfolio_values / portfolio_values.iloc[0]
        
        ax.plot(portfolio_nav.index, portfolio_nav.values, 
                label='策略净值', color='blue', linewidth=2)
        
        if benchmark_values is not None:
            benchmark_nav = benchmark_values / benchmark_values.iloc[0]
            ax.plot(benchmark_nav.index, benchmark_nav.values, 
                    label='基准净值', color='gray', linewidth=1, alpha=0.7)
        
        ax.set_title('净值曲线', fontsize=12)
        ax.set_ylabel('净值')
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    def _plot_drawdown(self, ax, portfolio_values):
        """绘制回撤图"""
        # 计算回撤
        cumulative = portfolio_values / portfolio_values.iloc[0]
        peak = cumulative.cummax()
        drawdown = (cumulative - peak) / peak
        
        ax.fill_between(drawdown.index, drawdown.values, 0, 
                        color='red', alpha=0.3)
        ax.plot(drawdown.index, drawdown.values, 
                color='red', linewidth=1)
        
        ax.set_title('回撤曲线', fontsize=12)
        ax.set_ylabel('回撤')
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # 标注最大回撤
        max_dd_idx = drawdown.idxmin()
        max_dd_value = drawdown.min()
        ax.annotate(f'最大回撤: {max_dd_value:.2%}', 
                   xy=(max_dd_idx, max_dd_value),
                   xytext=(max_dd_idx, max_dd_value * 0.8),
                   arrowprops=dict(facecolor='black', shrink=0.05))
    
    def _plot_monthly_returns(self, ax, portfolio_values):
        """绘制月度收益热力图"""
        # 计算月度收益
        monthly_returns = portfolio_values.resample('ME').last().pct_change().dropna()
        
        # 创建年月矩阵
        years = monthly_returns.index.year.unique()
        months = range(1, 13)
        
        # 准备数据
        data = pd.DataFrame(index=years, columns=months)
        for date, ret in monthly_returns.items():
            data.loc[date.year, date.month] = ret
        
        # 绘制热力图
        data = data.astype(float)
        im = ax.imshow(data.values, cmap='RdYlGn', aspect='auto', 
                      vmin=-0.1, vmax=0.1)
        
        # 设置标签
        ax.set_xticks(range(12))
        ax.set_xticklabels(['1月', '2月', '3月', '4月', '5月', '6月',
                           '7月', '8月', '9月', '10月', '11月', '12月'])
        ax.set_yticks(range(len(years)))
        ax.set_yticklabels(years)
        
        ax.set_title('月度收益热力图', fontsize=12)
        
        # 添加数值
        for i in range(len(years)):
            for j in range(12):
                value = data.iloc[i, j]
                if pd.notna(value):
                    text = f'{value:.1%}'
                    ax.text(j, i, text, ha='center', va='center', fontsize=8)
        
        plt.colorbar(im, ax=ax, label='收益率')
    
    def _plot_returns_distribution(self, ax, portfolio_values):
        """绘制收益分布图"""
        # 计算日收益率
        returns = portfolio_values.pct_change().dropna()
        
        # 绘制直方图
        ax.hist(returns.values, bins=50, color='blue', alpha=0.7, edgecolor='black')
        
        # 添加统计信息
        mean_return = returns.mean()
        std_return = returns.std()
        ax.axvline(mean_return, color='red', linestyle='--', linewidth=2, 
                  label=f'均值: {mean_return:.4f}')
        ax.axvline(mean_return + 2*std_return, color='orange', linestyle='--', 
                  linewidth=1, label=f'+2σ: {mean_return + 2*std_return:.4f}')
        ax.axvline(mean_return - 2*std_return, color='orange', linestyle='--', 
                  linewidth=1, label=f'-2σ: {mean_return - 2*std_return:.4f}')
        
        ax.set_title('日收益率分布', fontsize=12)
        ax.set_xlabel('收益率')
        ax.set_ylabel('频数')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    
    def _plot_statistics(self, ax, portfolio_values):
        """绘制统计信息"""
        ax.axis('off')
        
        # 计算指标
        returns = portfolio_values.pct_change().dropna()
        
        total_return = (portfolio_values.iloc[-1] / portfolio_values.iloc[0]) - 1
        annual_return = total_return * 252 / len(returns)
        volatility = returns.std() * np.sqrt(252)
        sharpe_ratio = annual_return / volatility if volatility > 0 else 0
        
        # 计算最大回撤
        cumulative = portfolio_values / portfolio_values.iloc[0]
        peak = cumulative.cummax()
        drawdown = (cumulative - peak) / peak
        max_drawdown = drawdown.min()
        
        # 计算胜率
        win_rate = (returns > 0).sum() / len(returns)
        
        # 显示统计信息
        stats_text = f"""
策略统计指标
{'='*30}

收益指标:
  总收益率: {total_return:.2%}
  年化收益率: {annual_return:.2%}
  年化波动率: {volatility:.2%}

风险指标:
  夏普比率: {sharpe_ratio:.2f}
  最大回撤: {max_drawdown:.2%}
  胜率: {win_rate:.2%}

交易统计:
  交易天数: {len(returns)}
  平均日收益: {returns.mean():.4%}
  收益标准差: {returns.std():.4%}
        """
        
        ax.text(0.1, 0.95, stats_text, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', fontfamily='monospace',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    def generate_trade_report(self, trades, filename=None):
        """
        生成交易报告
        
        Args:
            trades: 交易记录列表
            filename: 输出文件名
        """
        if not trades:
            print("没有交易记录")
            return
        
        df = pd.DataFrame(trades)
        
        # 计算统计信息
        total_trades = len(df)
        buy_trades = len(df[df['action'] == 'buy'])
        sell_trades = len(df[df['action'] == 'sell'])
        
        total_profit = df['profit'].sum() if 'profit' in df.columns else 0
        avg_profit = df['profit'].mean() if 'profit' in df.columns else 0
        
        print("\n" + "="*60)
        print("交易报告")
        print("="*60)
        print(f"总交易次数: {total_trades}")
        print(f"买入次数: {buy_trades}")
        print(f"卖出次数: {sell_trades}")
        print(f"总利润: {total_profit:.2f}")
        print(f"平均利润: {avg_profit:.2f}")
        print("="*60)
        
        # 保存到文件
        if filename is None:
            filename = os.path.join(self.output_dir, f'trades_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
        
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"交易记录已保存到: {filename}")
        
        return df

