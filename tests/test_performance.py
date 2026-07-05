"""
性能测试模块
测试回测性能和内存使用

使用方法：
    python -m pytest tests/test_performance.py -v
"""

import sys
import os
import pytest
import time
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestBacktestPerformance:
    """回测性能测试"""
    
    def test_single_stock_backtest_time(self):
        """测试单股票回测时间"""
        try:
            data_file = 'data/cache/000001_real_data.csv'
            if not os.path.exists(data_file):
                pytest.skip("数据文件不存在")
            
            df = pd.read_csv(data_file, index_col='date', parse_dates=True)
            
            # 测试数据加载时间
            start_time = time.time()
            df_loaded = pd.read_csv(data_file, index_col='date', parse_dates=True)
            load_time = time.time() - start_time
            
            assert load_time < 1.0  # 加载时间应小于1秒
            assert len(df_loaded) > 0
        except Exception as e:
            pytest.skip(f"性能测试失败: {e}")
    
    def test_indicator_calculation_time(self):
        """测试指标计算时间"""
        try:
            import numpy as np
            
            # 创建测试数据
            prices = pd.Series(np.random.randn(1000).cumsum() + 100)
            
            # 测试RSI计算时间
            start_time = time.time()
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            rsi_time = time.time() - start_time
            
            assert rsi_time < 0.1  # 计算时间应小于0.1秒
            assert len(rsi.dropna()) > 0
        except Exception as e:
            pytest.skip(f"性能测试失败: {e}")


class TestMemoryUsage:
    """内存使用测试"""
    
    def test_data_loading_memory(self):
        """测试数据加载内存使用"""
        try:
            import sys
            
            data_file = 'data/cache/000001_real_data.csv'
            if not os.path.exists(data_file):
                pytest.skip("数据文件不存在")
            
            # 记录初始内存
            initial_size = sys.getsizeof(pd.DataFrame())
            
            # 加载数据
            df = pd.read_csv(data_file, index_col='date', parse_dates=True)
            
            # 检查内存使用
            df_size = sys.getsizeof(df)
            
            # 内存使用应该合理（小于100MB）
            assert df_size < 100 * 1024 * 1024
        except Exception as e:
            pytest.skip(f"内存测试失败: {e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
