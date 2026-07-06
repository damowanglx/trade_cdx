"""
数据质量监控测试
测试数据完整性、准确性、及时性检查

使用方法：
    python scripts/test_data_quality.py
"""

import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.quality.data_quality_monitor import DataQualityMonitor


def main():
    """主函数"""
    print("="*60)
    print("数据质量监控测试")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 创建数据质量监控器
    monitor = DataQualityMonitor()
    
    # 测试1：使用真实数据
    print("=== 测试1：真实数据质量检查 ===")
    data_file = 'data/cache/000001_real_data.csv'
    
    if os.path.exists(data_file):
        df = pd.read_csv(data_file, index_col='date', parse_dates=True)
        print(f"数据文件: {data_file}")
        print(f"数据行数: {len(df)}")
        print(f"数据列数: {len(df.columns)}")
        print()
        
        # 生成质量报告
        report = monitor.generate_quality_report(
            df, 
            required_columns=['open', 'high', 'low', 'close', 'volume']
        )
        print(report)
    else:
        print("数据文件不存在，使用模拟数据测试")
    
    # 测试2：模拟数据质量检查
    print("\n=== 测试2：模拟数据质量检查 ===")
    
    # 创建包含问题的模拟数据
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    
    mock_data = pd.DataFrame({
        'open': np.random.uniform(10, 20, 100),
        'high': np.random.uniform(15, 25, 100),
        'low': np.random.uniform(5, 15, 100),
        'close': np.random.uniform(10, 20, 100),
        'volume': np.random.randint(1000, 10000, 100),
    }, index=dates)
    
    # 添加一些问题
    mock_data.iloc[10, 0] = np.nan  # 缺失值
    mock_data.iloc[20, 1] = -5      # 异常值（负数）
    mock_data.iloc[30, 2] = 100     # 异常值（过高）
    
    print("模拟数据预览:")
    print(mock_data.head())
    print()
    
    # 测试完整性
    print("=== 完整性检查 ===")
    completeness = monitor.check_data_completeness(
        mock_data, 
        required_columns=['open', 'high', 'low', 'close', 'volume']
    )
    print(f"完整性评分: {completeness['completeness_score']:.2%}")
    print(f"缺失列: {completeness['missing_columns']}")
    print(f"缺失值: {completeness['missing_values']}")
    print()
    
    # 测试准确性
    print("=== 准确性检查 ===")
    for col in ['open', 'high', 'low', 'close']:
        accuracy = monitor.check_data_accuracy(mock_data, col, min_value=0)
        print(f"{col}: 准确性评分 {accuracy['accuracy_score']:.2%}, 异常值数 {len(accuracy['outliers'])}")
    
    print()
    
    # 生成完整报告
    print("=== 完整质量报告 ===")
    report = monitor.generate_quality_report(
        mock_data,
        required_columns=['open', 'high', 'low', 'close', 'volume']
    )
    print(report)
    
    # 保存报告
    os.makedirs('reports', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    with open(f'reports/data_quality_report_{timestamp}.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n报告已保存到: reports/data_quality_report_{timestamp}.txt")
    print("="*60)
    print("数据质量监控测试完成！")
    print("="*60)


if __name__ == '__main__':
    main()
