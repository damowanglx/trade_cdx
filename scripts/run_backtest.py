"""
运行回测脚本
用于执行策略回测并查看结果

使用方法：
    python scripts/run_backtest.py
"""

import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategy.ma_cross import run_backtest


def main():
    """主函数"""
    
    # 数据文件路径
    data_file = 'data/cache/000001.SZ_daily.csv'
    
    # 检查数据文件是否存在
    if not os.path.exists(data_file):
        print("="*60)
        print("错误: 数据文件不存在")
        print("="*60)
        print(f"\n请先运行数据获取脚本:")
        print(f"  python scripts/01_data_analysis.py")
        print(f"\n该脚本会获取平安银行(000001.SZ)的数据并保存到:")
        print(f"  {data_file}")
        return
    
    # 运行回测
    print("\n开始运行双均线策略回测...\n")
    
    results = run_backtest(
        data_file=data_file,
        initial_cash=200000,  # 初始资金20万
        commission=0.001,     # 手续费千分之一
        plot=True             # 显示图表
    )
    
    if results:
        print("\n" + "="*60)
        print("回测结果分析")
        print("="*60)
        
        # 评价策略表现
        print("\n策略评价:")
        
        # 1. 收益率评价
        if results['total_return'] > 0:
            print(f"  ✓ 总收益率为正: {results['total_return']:.2f}%")
        else:
            print(f"  ✗ 总收益率为负: {results['total_return']:.2f}%")
        
        # 2. 夏普比率评价
        sharpe = results['sharpe_ratio']
        if sharpe is not None:
            if sharpe > 2:
                print(f"  ✓ 夏普比率优秀: {sharpe:.2f}")
            elif sharpe > 1:
                print(f"  ○ 夏普比率良好: {sharpe:.2f}")
            else:
                print(f"  ✗ 夏普比率较低: {sharpe:.2f}")
        
        # 3. 最大回撤评价
        max_dd = results['max_drawdown']
        if max_dd is not None:
            if max_dd < 10:
                print(f"  ✓ 最大回撤较小: {max_dd:.2f}%")
            elif max_dd < 20:
                print(f"  ○ 最大回撤适中: {max_dd:.2f}%")
            else:
                print(f"  ✗ 最大回撤较大: {max_dd:.2f}%")
        
        print("\n" + "="*60)
        print("下一步学习:")
        print("="*60)
        print("  1. 查看生成的图表，理解买卖点")
        print("  2. 尝试修改策略参数（如均线周期）")
        print("  3. 学习其他策略（RSI、MACD等）")
        print("  4. 尝试多股票组合回测")


if __name__ == '__main__':
    main()

