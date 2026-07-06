"""
性能优化模块
提供缓存、并行计算、增量计算功能

使用方法：
    from backtest.performance import PerformanceOptimizer
"""

import hashlib
import os
import pickle
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import lru_cache

import pandas as pd


class PerformanceOptimizer:
    """性能优化器"""
    
    def __init__(self, cache_dir='data/cache'):
        """
        初始化性能优化器
        
        Args:
            cache_dir: 缓存目录
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_cache_key(self, func_name, *args, **kwargs):
        """生成缓存键"""
        key_data = f"{func_name}_{args}_{kwargs}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def load_from_cache(self, cache_key):
        """从缓存加载数据"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        return None
    
    def save_to_cache(self, cache_key, data):
        """保存数据到缓存"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        with open(cache_file, 'wb') as f:
            pickle.dump(data, f)
    
    def parallel_backtest(self, backtest_func, data_files, max_workers=None):
        """
        并行回测
        
        Args:
            backtest_func: 回测函数
            data_files: 数据文件列表
            max_workers: 最大进程数
            
        Returns:
            list: 回测结果列表
        """
        if max_workers is None:
            max_workers = os.cpu_count() or 4
        
        results = []
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_file = {
                executor.submit(backtest_func, f): f 
                for f in data_files
            }
            
            # 收集结果
            for future in as_completed(future_to_file):
                file = future_to_file[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    print(f"回测失败 {file}: {e}")
        
        return results
    
    def incremental_calculation(self, new_data, previous_result, calc_func):
        """
        增量计算
        
        Args:
            new_data: 新数据
            previous_result: 之前的结果
            calc_func: 计算函数
            
        Returns:
            计算结果
        """
        # 合并数据
        if previous_result is not None:
            combined_data = pd.concat([previous_result, new_data])
        else:
            combined_data = new_data
        
        # 计算新结果
        result = calc_func(combined_data)
        
        return result
