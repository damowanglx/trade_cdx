"""
数据处理工具模块
提供数据验证、清洗、转换功能

使用方法：
    from data.utils.data_utils import DataUtils
"""

import pandas as pd
import numpy as np


class DataUtils:
    """数据处理工具类"""
    
    @staticmethod
    def validate_data(df, required_columns=None):
        """
        验证数据完整性
        
        Args:
            df: DataFrame数据
            required_columns: 必需的列名列表
            
        Returns:
            dict: 验证结果
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # 检查是否为空
        if df.empty:
            result['is_valid'] = False
            result['errors'].append("数据为空")
            return result
        
        # 检查必需列
        if required_columns:
            missing_cols = set(required_columns) - set(df.columns)
            if missing_cols:
                result['is_valid'] = False
                result['errors'].append(f"缺少必需列: {missing_cols}")
        
        # 检查缺失值
        missing_count = df.isnull().sum().sum()
        if missing_count > 0:
            result['warnings'].append(f"存在 {missing_count} 个缺失值")
        
        # 检查数据类型
        for col in df.columns:
            if df[col].dtype == 'object':
                result['warnings'].append(f"列 {col} 是字符串类型，可能需要转换")
        
        return result
    
    @staticmethod
    def clean_data(df, fill_method='ffill'):
        """
        清洗数据
        
        Args:
            df: DataFrame数据
            fill_method: 填充方法（ffill向前填充，bfill向后填充）
            
        Returns:
            DataFrame: 清洗后的数据
        """
        # 复制数据
        df_clean = df.copy()
        
        # 填充缺失值
        if fill_method == 'ffill':
            df_clean = df_clean.fillna(method='ffill')
        elif fill_method == 'bfill':
            df_clean = df_clean.fillna(method='bfill')
        
        # 删除仍然有缺失值的行
        df_clean = df_clean.dropna()
        
        return df_clean
    
    @staticmethod
    def convert_types(df, type_mapping=None):
        """
        转换数据类型
        
        Args:
            df: DataFrame数据
            type_mapping: 类型映射字典
            
        Returns:
            DataFrame: 转换后的数据
        """
        if type_mapping is None:
            type_mapping = {
                'open': float,
                'high': float,
                'low': float,
                'close': float,
                'volume': float,
                'amount': float
            }
        
        df_converted = df.copy()
        
        for col, dtype in type_mapping.items():
            if col in df_converted.columns:
                df_converted[col] = pd.to_numeric(df_converted[col], errors='coerce')
        
        return df_converted
    
    @staticmethod
    def remove_outliers(df, column, method='iqr', threshold=1.5):
        """
        移除异常值
        
        Args:
            df: DataFrame数据
            column: 列名
            method: 方法（iqr或zscore）
            threshold: 阈值
            
        Returns:
            DataFrame: 移除异常值后的数据
        """
        df_clean = df.copy()
        
        if method == 'iqr':
            Q1 = df_clean[column].quantile(0.25)
            Q3 = df_clean[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            df_clean = df_clean[(df_clean[column] >= lower_bound) & (df_clean[column] <= upper_bound)]
        
        elif method == 'zscore':
            mean = df_clean[column].mean()
            std = df_clean[column].std()
            df_clean = df_clean[abs((df_clean[column] - mean) / std) <= threshold]
        
        return df_clean
    
    @staticmethod
    def add_basic_indicators(df):
        """
        添加基础技术指标
        
        Args:
            df: DataFrame数据（需要包含close列）
            
        Returns:
            DataFrame: 添加指标后的数据
        """
        df_indicators = df.copy()
        
        # 计算收益率
        df_indicators['return'] = df_indicators['close'].pct_change()
        
        # 计算移动平均
        df_indicators['ma5'] = df_indicators['close'].rolling(5).mean()
        df_indicators['ma10'] = df_indicators['close'].rolling(10).mean()
        df_indicators['ma20'] = df_indicators['close'].rolling(20).mean()
        
        # 计算波动率
        df_indicators['volatility'] = df_indicators['return'].rolling(20).std() * np.sqrt(252)
        
        return df_indicators
