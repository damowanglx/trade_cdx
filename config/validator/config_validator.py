"""
配置验证模块
验证配置文件的完整性和正确性

使用方法：
    from config.validator.config_validator import ConfigValidator
"""

import os
import sys
from typing import Dict, List, Any, Optional
import logging


class ConfigValidator:
    """配置验证器"""
    
    def __init__(self):
        """初始化配置验证器"""
        self.logger = logging.getLogger('config_validator')
        self.errors = []
        self.warnings = []
        
    def validate_trading_config(self, config: Dict[str, Any]) -> bool:
        """
        验证交易配置
        
        Args:
            config: 交易配置
            
        Returns:
            bool: 验证是否通过
        """
        self.errors = []
        self.warnings = []
        
        # 检查必需字段
        required_fields = ['INITIAL_CAPITAL', 'POSITION_CONFIG', 'RISK_CONFIG']
        for field in required_fields:
            if field not in config:
                self.errors.append(f"缺少必需配置: {field}")
                
        # 验证初始资金
        if 'INITIAL_CAPITAL' in config:
            capital = config['INITIAL_CAPITAL']
            if not isinstance(capital, (int, float)) or capital <= 0:
                self.errors.append(f"初始资金无效: {capital}")
            elif capital < 10000:
                self.warnings.append(f"初始资金较低: {capital}")
                
        # 验证仓位配置
        if 'POSITION_CONFIG' in config:
            pos_config = config['POSITION_CONFIG']
            
            if 'max_position' in pos_config:
                max_pos = pos_config['max_position']
                if not 0 < max_pos <= 1:
                    self.errors.append(f"最大仓位无效: {max_pos}")
                    
        # 验证风险配置
        if 'RISK_CONFIG' in config:
            risk_config = config['RISK_CONFIG']
            
            if 'max_drawdown' in risk_config:
                max_dd = risk_config['max_drawdown']
                if not 0 < max_dd < 1:
                    self.errors.append(f"最大回撤无效: {max_dd}")
                    
        return len(self.errors) == 0
        
    def get_errors(self) -> List[str]:
        """获取错误列表"""
        return self.errors
        
    def get_warnings(self) -> List[str]:
        """获取警告列表"""
        return self.warnings
