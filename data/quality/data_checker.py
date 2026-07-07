"""
数据质量检查模块
检查数据完整性、准确性、及时性

使用方法：
    from data.quality.data_checker import DataChecker
"""

import pandas as pd
import numpy as np


class DataChecker:
    """数据质量检查器"""
    
    def __init__(self):
        """初始化"""
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = []
        
    def check_completeness(self, df, required_columns):
        """检查数据完整性"""
        missing_cols = set(required_columns) - set(df.columns)
        if missing_cols:
            self.checks_failed += 1
            self.warnings.append(f"缺少列: {missing_cols}")
            return False
        
        missing_values = df[required_columns].isnull().sum()
        if missing_values.sum() > 0:
            self.checks_failed += 1
            self.warnings.append(f"存在缺失值: {missing_values[missing_values > 0].to_dict()}")
            return False
        
        self.checks_passed += 1
        return True
    
    def check_accuracy(self, df, column, min_value=None, max_value=None):
        """检查数据准确性"""
        if column not in df.columns:
            self.checks_failed += 1
            self.warnings.append(f"列不存在: {column}")
            return False
        
        values = df[column].dropna()
        
        if min_value is not None:
            below_min = values[values < min_value]
            if len(below_min) > 0:
                self.checks_failed += 1
                self.warnings.append(f"{column} 存在低于 {min_value} 的值: {len(below_min)} 个")
                return False
        
        if max_value is not None:
            above_max = values[values > max_value]
            if len(above_max) > 0:
                self.checks_failed += 1
                self.warnings.append(f"{column} 存在高于 {max_value} 的值: {len(above_max)} 个")
                return False
        
        self.checks_passed += 1
        return True
    
    def check_timeliness(self, df, date_column, max_delay_days=1):
        """检查数据及时性"""
        if date_column not in df.columns:
            self.checks_failed += 1
            self.warnings.append(f"日期列不存在: {date_column}")
            return False
        
        latest_date = pd.to_datetime(df[date_column]).max()
        current_date = pd.Timestamp.now()
        delay_days = (current_date - latest_date).days
        
        if delay_days > max_delay_days:
            self.checks_failed += 1
            self.warnings.append(f"数据延迟 {delay_days} 天，超过限制 {max_delay_days} 天")
            return False
        
        self.checks_passed += 1
        return True
    
    def check_price_validity(self, df):
        """检查价格有效性"""
        required_cols = ['open', 'high', 'low', 'close']
        
        if not self.check_completeness(df, required_cols):
            return False
        
        # 检查价格关系
        invalid = df[df['high'] < df['low']]
        if len(invalid) > 0:
            self.checks_failed += 1
            self.warnings.append(f"存在最高价低于最低价的记录: {len(invalid)} 条")
            return False
        
        # 检查价格范围
        for col in required_cols:
            if not self.check_accuracy(df, col, min_value=0):
                return False
        
        self.checks_passed += 1
        return True
    
    def check_volume_validity(self, df):
        """检查成交量有效性"""
        if 'volume' not in df.columns:
            self.checks_failed += 1
            self.warnings.append("成交量列不存在")
            return False
        
        negative_volume = df[df['volume'] < 0]
        if len(negative_volume) > 0:
            self.checks_failed += 1
            self.warnings.append(f"存在负成交量: {len(negative_volume)} 条")
            return False
        
        self.checks_passed += 1
        return True
    
    def generate_report(self):
        """生成检查报告"""
        report = "=" * 60 + "\n"
        report += "数据质量检查报告\n"
        report += "=" * 60 + "\n\n"
        
        report += f"检查通过: {self.checks_passed}\n"
        report += f"检查失败: {self.checks_failed}\n"
        report += f"总检查数: {self.checks_passed + self.checks_failed}\n\n"
        
        if self.warnings:
            report += "警告:\n"
            for warning in self.warnings:
                report += f"  - {warning}\n"
        else:
            report += "无警告\n"
        
        report += "\n" + "=" * 60
        
        return report
