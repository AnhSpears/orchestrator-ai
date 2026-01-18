"""
MEMORY SYSTEM - Hệ thống bộ nhớ thông minh
"""
import os
import json
import pickle
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
from pathlib import Path

class MemorySystem:
    """Hệ thống quản lý bộ nhớ thông minh"""
    
    def __init__(self, base_path: str = "memory"):
        self.logger = logging.getLogger(__name__)
        self.base_path = Path(base_path)
        self._init_memory_structure()
        
    def _init_memory_structure(self):
        """Khởi tạo cấu trúc thư mục memory"""
        # Tạo các thư mục con
        dirs = ['short_term', 'long_term', 'vector_store', 'documents', 'knowledge']
        for dir_name in dirs:
            dir_path = self.base_path / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Tạo file index
        index_file = self.base_path / "memory_index.json"
        if not index_file.exists():
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "total_entries": 0,
                    "last_updated": datetime.now().isoformat(),
                    "categories": {
                        "short_term": 0,
                        "long_term": 0,
                        "vector": 0,
                        "documents": 0,
                        "knowledge": 0
                    }
                }, f, indent=2)
    
    def save_short_term(self, session_id: str, data: Dict[str, Any]) -> str:
        """Lưu bộ nhớ ngắn hạn (session-based)"""
        try:
            session_file = self.base_path / "short_term" / f"{session_id}.json"
            
            # Đọc dữ liệu cũ nếu có
            existing_data = {}
            if session_file.exists():
                with open(session_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            
            # Merge dữ liệu
            existing_data.update(data)
            existing_data['_last_updated'] = datetime.now().isoformat()
            
            # Lưu file
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
            
            self._update_index("short_term")
            return f"Đã lưu {len(data)} mục vào bộ nhớ ngắn hạn"
            
        except Exception as e:
            self.logger.error(f"Lỗi lưu short term memory: {e}")
            return f"Lỗi: {e}"
    
    def save_long_term(self, key: str, data: Dict[str, Any], category: str = "general") -> str:
        """Lưu bộ nhớ dài hạn"""
        try:
            # Tạo hash từ key
            key_hash = hashlib.md5(key.encode()).hexdigest()
            
            # Tạo thư mục category nếu chưa có
            category_dir = self.base_path / "long_term" / category
            category_dir.mkdir(parents=True, exist_ok=True)
            
            # Tạo file lưu trữ
            memory_file = category_dir / f"{key_hash}.json"
            
            memory_data = {
                "key": key,
                "key_hash": key_hash,
                "data": data,
                "category": category,
                "created_at": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "access_count": 1
            }
            
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2, ensure_ascii=False)
            
            self._update_index("long_term")
            return f"Đã lưu '{key}' vào bộ nhớ dài hạn ({category})"
            
        except Exception as e:
            self.logger.error(f"Lỗi lưu long term memory: {e}")
            return f"Lỗi: {e}"
    
    def retrieve_long_term(self, key: str = None, category: str = None, 
                          keyword: str = None) -> List[Dict[str, Any]]:
        """Truy xuất bộ nhớ dài hạn"""
        try:
            results = []
            base_dir = self.base_path / "long_term"
            
            if not base_dir.exists():
                return results
            
            # Tìm theo key chính xác
            if key:
                key_hash = hashlib.md5(key.encode()).hexdigest()
                for category_dir in base_dir.iterdir():
                    if category_dir.is_dir():
                        memory_file = category_dir / f"{key_hash}.json"
                        if memory_file.exists():
                            with open(memory_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                data['last_accessed'] = datetime.now().isoformat()
                                data['access_count'] += 1
                                results.append(data)
                            
                            # Cập nhật access time
                            with open(memory_file, 'w', encoding='utf-8') as f:
                                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Tìm theo category
            elif category:
                category_dir = base_dir / category
                if category_dir.exists():
                    for memory_file in category_dir.glob("*.json"):
                        with open(memory_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            
                            # Kiểm tra keyword nếu có
                            if keyword:
                                if (keyword.lower() in data['key'].lower() or 
                                    keyword.lower() in str(data['data']).lower()):
                                    results.append(data)
                            else:
                                results.append(data)
            
            # Tìm toàn bộ
            else:
                for category_dir in base_dir.iterdir():
                    if category_dir.is_dir():
                        for memory_file in category_dir.glob("*.json"):
                            with open(memory_file, 'r', encoding='utf-8') as f:
                                results.append(json.load(f))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Lỗi truy xuất memory: {e}")
            return []
    
    def save_document(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """Lưu tài liệu học tập"""
        try:
            # Tạo ID từ nội dung
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Tạo metadata
            if metadata is None:
                metadata = {}
            
            doc_data = {
                "id": content_hash,
                "content": content,
                "metadata": metadata,
                "created_at": datetime.now().isoformat(),
                "type": "document",
                "source": "user_upload"
            }
            
            # Lưu file
            doc_file = self.base_path / "documents" / f"{content_hash}.json"
            with open(doc_file, 'w', encoding='utf-8') as f:
                json.dump(doc_data, f, indent=2, ensure_ascii=False)
            
            self._update_index("documents")
            return f"Đã lưu tài liệu (ID: {content_hash[:8]})"
            
        except Exception as e:
            self.logger.error(f"Lỗi lưu document: {e}")
            return f"Lỗi: {e}"
    
    def search_documents(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Tìm kiếm tài liệu theo từ khóa"""
        try:
            results = []
            docs_dir = self.base_path / "documents"
            
            if not docs_dir.exists():
                return results
            
            query_lower = query.lower()
            
            for doc_file in docs_dir.glob("*.json"):
                with open(doc_file, 'r', encoding='utf-8') as f:
                    doc_data = json.load(f)
                    
                    # Tìm kiếm trong content và metadata
                    content = doc_data.get('content', '').lower()
                    metadata = str(doc_data.get('metadata', {})).lower()
                    
                    if query_lower in content or query_lower in metadata:
                        results.append(doc_data)
                
                if len(results) >= max_results:
                    break
            
            return results
            
        except Exception as e:
            self.logger.error(f"Lỗi tìm kiếm documents: {e}")
            return []
    
    def _update_index(self, category: str):
        """Cập nhật memory index"""
        try:
            index_file = self.base_path / "memory_index.json"
            
            if index_file.exists():
                with open(index_file, 'r', encoding='utf-8') as f:
                    index = json.load(f)
            else:
                index = {
                    "total_entries": 0,
                    "last_updated": datetime.now().isoformat(),
                    "categories": {}
                }
            
            # Đếm file trong category
            if category in ["short_term", "long_term", "documents", "knowledge"]:
                category_dir = self.base_path / category
                if category_dir.exists():
                    if category == "long_term":
                        count = sum(1 for _ in category_dir.rglob("*.json"))
                    else:
                        count = sum(1 for _ in category_dir.glob("*.json"))
                    
                    index["categories"][category] = count
            
            # Tính tổng
            total = sum(index["categories"].values())
            index["total_entries"] = total
            index["last_updated"] = datetime.now().isoformat()
            
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Lỗi update index: {e}")