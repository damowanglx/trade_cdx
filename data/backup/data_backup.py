"""
数据备份模块
备份和恢复股票数据
"""

import os
import shutil
import pandas as pd
from datetime import datetime
from typing import List, Optional
import logging


class DataBackup:
    """数据备份器"""
    
    def __init__(self, data_dir='data/all_stocks', backup_dir='data/backups'):
        self.data_dir = data_dir
        self.backup_dir = backup_dir
        self.logger = logging.getLogger('data_backup')
        os.makedirs(backup_dir, exist_ok=True)
        
    def create_backup(self, backup_name=None):
        """创建备份"""
        if backup_name is None:
            backup_name = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        try:
            shutil.copytree(self.data_dir, backup_path)
            self.logger.info(f"备份创建成功: {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"备份创建失败: {e}")
            return ""
            
    def list_backups(self):
        """列出所有备份"""
        backups = []
        if os.path.exists(self.backup_dir):
            for name in os.listdir(self.backup_dir):
                backup_path = os.path.join(self.backup_dir, name)
                if os.path.isdir(backup_path):
                    file_count = len([f for f in os.listdir(backup_path) if f.endswith('.csv')])
                    backups.append({'name': name, 'file_count': file_count})
        return backups
