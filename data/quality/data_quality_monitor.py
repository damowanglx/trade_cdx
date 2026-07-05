"""
数据质量监控模块
监控数据完整性、准确性、及时性

使用方法：
    from data.quality.data_quality_monitor import DataQualityMonitor
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging


class DataQualityMonitor:
    """数据质量监控器"""
    
    def __init__(self, logger_name: str = 'data_quality'):
        """
        初始化数据质量监控器
        
        Args:
            logger_name: 日志记录器名称
        """
        self.logger = logging.getLogger(logger_name)
        self.quality_metrics = {}
        
    def check_data_completeness(self, df: pd.DataFrame, 
                               required_columns: List[str]) -> Dict[str, Any]:
        """
        检查数据完整性
        
        Args:
            df: DataFrame数据
            required_columns: 必需的列名
            
        Returns:
            Dict: 完整性检查结果
        """
        result = {
            'is_complete': True,
            'missing_columns': [],
            'missing_values': {},
            'completeness_score': 1.0
        }
        
        # 检查必需列
        missing_cols = set(required_columns) - set(df.columns)
        if missing_cols:
            result['is_complete'] = False
            result['missing_columns'] = list(missing_cols)
            
        # 检查缺失值
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                result['missing_values'][col] = {
                    'count': int(missing_count),
                    'percentage': missing_count / len(df) * 100
                }
                
        # 计算完整性评分
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isnull().sum().sum()
        result['completeness_score'] = 1 - (missing_cells / total_cells) if total_cells > 0 else 1
        
        return result
        
    def check_data_accuracy(self, df: pd.DataFrame, 
                           column: str,
                           min_value: Optional[float] = None,
                           max_value: Optional[float] = None) -> Dict[str, Any]:
        """
        检查数据准确性
        
        Args:
            df: DataFrame数据
            column: 列名
            min_value: 最小值
            max_value: 最大值
            
        Returns:
            Dict: 准确性检查结果
        """
        result = {
            'is_accurate': True,
            'outliers': [],
            'accuracy_score': 1.0
        }
        
        if column not in df.columns:
            result['is_accurate'] = False
            return result
            
        values = df[column].dropna()
        
        # 检查范围
        if min_value is not None:
            below_min = values[values < min_value]
            if len(below_min) > 0:
                result['is_accurate'] = False
                result['outliers'].extend(below_min.index.tolist())
                
        if max_value is not None:
            above_max = values[values > max_value]
            if len(above_max) > 0:
                result['is_accurate'] = False
                result['outliers'].extend(above_max.index.tolist())
                
        # 检查异常值（使用IQR方法）
        Q1 = values.quantile(0.25)
        Q3 = values.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outlier_mask = (values < lower_bound) | (values > upper_bound)
        outliers = values[outlier_mask]
        
        if len(outliers) > 0:
            result['outliers'].extend(outliers.index.tolist())
            
        # 计算准确性评分
        total_count = len(values)
        outlier_count = len(set(result['outliers']))
        result['accuracy_score'] = 1 - (outlier_count / total_count) if total_count > 0 else 1
        
        return result
        
    def generate_quality_report(self, df: pd.DataFrame,
                               required_columns: List[str],
                               date_column: Optional[str] = None) -> str:
        """
        生成数据质量报告
        
        Args:
            df: DataFrame数据
            required_columns: 必需的列名
            date_column: 日期列名
            
        Returns:
            str: 质量报告
        """
        report = "=" * 60 + "\n"
        report += "数据质量报告\n"
        report += "=" * 60 + "\n\n"
        
        # 完整性检查
        completeness = self.check_data_completeness(df, required_columns)
        report += f"完整性检查:\n"
        report += f"  完整性评分: {completeness['completeness_score']:.2%}\n"
        if completeness['missing_columns']:
            report += f"  缺失列: {', '.join(completeness['missing_columns'])}\n"
        report += "\n"
        
        # 数值列检查
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        report += f"数值列检查:\n"
        for col in numeric_cols:
            accuracy = self.check_data_accuracy(df, col)
            report += f"  {col}: 准确性评分 {accuracy['accuracy_score']:.2%}\n"
            
        report += "\n" + "=" * 60
        
        return report
