"""
配置管理模块
统一管理所有配置文件

使用方法：
    from config.config_manager import ConfigManager
"""

import os
import sys
from typing import Any, Dict, Optional


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir='config'):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置文件目录
        """
        self.config_dir = config_dir
        self.configs = {}
        
    def load_config(self, config_name: str) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            config_name: 配置文件名（不含.py扩展名）
            
        Returns:
            Dict: 配置字典
        """
        config_file = os.path.join(self.config_dir, f"{config_name}.py")
        
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"配置文件不存在: {config_file}")
        
        # 动态导入配置模块
        import importlib.util
        spec = importlib.util.spec_from_file_location(config_name, config_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # 提取配置
        config = {}
        for attr_name in dir(module):
            if not attr_name.startswith('_'):
                attr_value = getattr(module, attr_name)
                if isinstance(attr_value, (dict, list, str, int, float, bool)):
                    config[attr_name] = attr_value
        
        self.configs[config_name] = config
        return config
    
    def get(self, config_name: str, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            config_name: 配置名称
            key: 配置键
            default: 默认值
            
        Returns:
            Any: 配置值
        """
        if config_name not in self.configs:
            self.load_config(config_name)
        
        return self.configs.get(config_name, {}).get(key, default)
    
    def validate_config(self, config_name: str, required_keys: list) -> bool:
        """
        验证配置完整性
        
        Args:
            config_name: 配置名称
            required_keys: 必需的配置键列表
            
        Returns:
            bool: 验证是否通过
        """
        if config_name not in self.configs:
            self.load_config(config_name)
        
        config = self.configs.get(config_name, {})
        
        for key in required_keys:
            if key not in config:
                print(f"配置缺失: {config_name}.{key}")
                return False
        
        return True
    
    def merge_configs(self, *config_names) -> Dict[str, Any]:
        """
        合并多个配置
        
        Args:
            *config_names: 配置名称列表
            
        Returns:
            Dict: 合并后的配置
        """
        merged = {}
        
        for name in config_names:
            if name not in self.configs:
                self.load_config(name)
            
            merged.update(self.configs.get(name, {}))
        
        return merged


# 全局配置管理器实例
config_manager = ConfigManager()


def get_config(key: str, default: Any = None) -> Any:
    """
    获取配置值（快捷函数）
    
    Args:
        key: 配置键，格式为 "config_name.key"
        default: 默认值
        
    Returns:
        Any: 配置值
    """
    parts = key.split('.', 1)
    if len(parts) == 2:
        config_name, config_key = parts
        return config_manager.get(config_name, config_key, default)
    return default
