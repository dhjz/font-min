import os
import json
from datetime import datetime
from typing import Dict, Optional

class FileManager:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.mapping_file = os.path.join(base_dir, 'file_mapping.json')
        self.mapping: Dict[str, dict] = {}
        self._load_mapping()

    def _load_mapping(self):
        if os.path.exists(self.mapping_file):
            try:
                with open(self.mapping_file, 'r', encoding='utf-8') as f:
                    self.mapping = json.load(f)
            except Exception:
                self.mapping = {}

    def _save_mapping(self):
        with open(self.mapping_file, 'w', encoding='utf-8') as f:
            json.dump(self.mapping, f, ensure_ascii=False, indent=2)

    def save_file_info(self, file_id: str, original_filename: str, file_type: str = 'upload'):
        self.mapping[file_id] = {
            'original_filename': original_filename,
            'file_type': file_type,
            'timestamp': datetime.now().isoformat()
        }
        self._save_mapping()

    def get_file_info(self, file_id: str) -> Optional[dict]:
        return self.mapping.get(file_id)

    def get_original_filename(self, file_id: str) -> Optional[str]:
        info = self.get_file_info(file_id)
        return info['original_filename'] if info else None

    def delete_file_info(self, file_id: str):
        if file_id in self.mapping:
            del self.mapping[file_id]
            self._save_mapping()

    def cleanup_old_files(self, days: int = 1):
        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
        to_delete = []
        
        for file_id, info in self.mapping.items():
            try:
                file_time = datetime.fromisoformat(info['timestamp']).timestamp()
                if file_time < cutoff_time:
                    to_delete.append(file_id)
            except Exception:
                continue
        
        for file_id in to_delete:
            self.delete_file_info(file_id)
        
        return len(to_delete)
