"""
数据版本管理模块
管理数据版本和变更历史
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
import logging


class DataVersionManager:
    """数据版本管理器"""
    
    def __init__(self, data_dir='data/all_stocks', version_dir='data/versions'):
        self.data_dir = data_dir
        self.version_dir = version_dir
        self.logger = logging.getLogger('data_version')
        os.makedirs(version_dir, exist_ok=True)
        self.history_file = os.path.join(version_dir, 'version_history.json')
        self.history = self._load_history()
        
    def _load_history(self):
        """加载版本历史"""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
        
    def _save_history(self):
        """保存版本历史"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
            
    def create_version(self, description=""):
        """创建新版本"""
        version_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        files = {}
        if os.path.exists(self.data_dir):
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.csv'):
                    filepath = os.path.join(self.data_dir, filename)
                    with open(filepath, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                    files[filename] = {'hash': file_hash, 'size': os.path.getsize(filepath)}
        
        version = {
            'id': version_id,
            'timestamp': datetime.now().isoformat(),
            'description': description,
            'file_count': len(files),
            'files': files
        }
        
        self.history.append(version)
        self._save_history()
        
        self.logger.info(f"版本创建成功: {version_id}")
        return version
