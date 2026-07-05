"""
安全模块
提供敏感信息保护、输入验证、日志脱敏功能

使用方法：
    from utils.security import SecurityUtils
"""

import re
import hashlib
import logging
from typing import Any, Dict, Optional


class SecurityUtils:
    """安全工具类"""
    
    # 敏感信息模式
    SENSITIVE_PATTERNS = {
        'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        'phone': r'1[3-9]\d{9}',
        'password': r'(?i)(password|passwd|pwd)\s*[:=]\s*\S+',
        'token': r'(?i)(token|key|secret)\s*[:=]\s*\S+',
    }
    
    @staticmethod
    def mask_sensitive_info(text: str) -> str:
        """
        脱敏敏感信息
        
        Args:
            text: 原始文本
            
        Returns:
            str: 脱敏后的文本
        """
        masked_text = text
        
        for info_type, pattern in SecurityUtils.SENSITIVE_PATTERNS.items():
            matches = re.findall(pattern, masked_text)
            for match in matches:
                # 保留前3位和后3位，中间用*替代
                if len(match) > 6:
                    masked = match[:3] + '*' * (len(match) - 6) + match[-3:]
                else:
                    masked = '*' * len(match)
                masked_text = masked_text.replace(match, masked)
        
        return masked_text
    
    @staticmethod
    def validate_input(value: Any, expected_type: type, 
                      min_value: Optional[float] = None,
                      max_value: Optional[float] = None) -> bool:
        """
        验证输入
        
        Args:
            value: 输入值
            expected_type: 期望类型
            min_value: 最小值
            max_value: 最大值
            
        Returns:
            bool: 验证是否通过
        """
        # 类型检查
        if not isinstance(value, expected_type):
            return False
        
        # 范围检查（仅对数值类型）
        if isinstance(value, (int, float)):
            if min_value is not None and value < min_value:
                return False
            if max_value is not None and value > max_value:
                return False
        
        return True
    
    @staticmethod
    def hash_data(data: str) -> str:
        """
        对数据进行哈希
        
        Args:
            data: 原始数据
            
        Returns:
            str: 哈希值
        """
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        清理文件名，移除危险字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            str: 清理后的文件名
        """
        # 移除路径分隔符和特殊字符
        dangerous_chars = ['/', '\\', '..', ';', '|', '&', '$', '`']
        sanitized = filename
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '_')
        
        return sanitized


class SecureLogger:
    """安全日志记录器"""
    
    def __init__(self, logger_name: str):
        """
        初始化安全日志记录器
        
        Args:
            logger_name: 日志记录器名称
        """
        self.logger = logging.getLogger(logger_name)
    
    def info(self, message: str, mask: bool = True):
        """记录信息日志"""
        if mask:
            message = SecurityUtils.mask_sensitive_info(message)
        self.logger.info(message)
    
    def error(self, message: str, mask: bool = True):
        """记录错误日志"""
        if mask:
            message = SecurityUtils.mask_sensitive_info(message)
        self.logger.error(message)
    
    def warning(self, message: str, mask: bool = True):
        """记录警告日志"""
        if mask:
            message = SecurityUtils.mask_sensitive_info(message)
        self.logger.warning(message)
