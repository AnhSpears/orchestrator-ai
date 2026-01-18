"""
ADVANCED DOCUMENT INGESTOR - Nhập đa định dạng vào Memory System
"""
import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List
import logging
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.multiformat_processor import MultiFormatProcessor

class AdvancedDocumentIngestor:
    """Nhập đa định dạng vào Memory System"""
    
    def __init__(self, memory_path: str = "memory"):
        self.logger = logging.getLogger(__name__)
        self.processor = MultiFormatProcessor()
        self.memory_path = Path(memory_path)
        self.documents_path = self.memory_path / "documents"
        self.documents_path.mkdir(parents=True, exist_ok=True)
        
        # Tạo thư mục theo loại
        self.type_folders = {
            'text': self.documents_path / "text",
            'office': self.documents_path / "office", 
            'pdf': self.documents_path / "pdf",
            'image': self.documents_path / "image",
            'code': self.documents_path / "code",
            'data': self.documents_path / "data"
        }
        
        for folder in self.type_folders.values():
            folder.mkdir(exist_ok=True)
    
    def ingest_file(self, file_path: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Nhập file đa định dạng"""
        try:
            # Xử lý file
            processing_result = self.processor.process_file(file_path)
            
            if "error" in processing_result:
                return {"status": "error", "error": processing_result["error"]}
            
            # Tạo document data
            doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(file_path) % 10000:04d}"
            
            doc_type = processing_result.get("type", "unknown")
            if doc_type in ['excel', 'powerpoint', 'word']:
                storage_type = 'office'
            elif doc_type == 'pdf':
                storage_type = 'pdf'
            elif doc_type == 'image':
                storage_type = 'image'
            elif 'code' in doc_type:
                storage_type = 'code'
            elif doc_type in ['json', 'csv', 'xml', 'yaml']:
                storage_type = 'data'
            else:
                storage_type = 'text'
            
            # Tạo metadata
            if metadata is None:
                metadata = {}
            
            full_metadata = {
                **metadata,
                "original_file": file_path,
                "ingested_at": datetime.now().isoformat(),
                "processor": "advanced_document_ingestor",
                "file_type": processing_result.get("type"),
                "file_size": processing_result.get("file_size", 0)
            }
            
            # Thêm processing result vào metadata
            processing_metadata = {k: v for k, v in processing_result.items() 
                                 if k not in ['content', 'error']}
            full_metadata["processing_info"] = processing_metadata
            
            # Tạo document
            document = {
                "id": doc_id,
                "content": processing_result.get("content", "")[:20000],  # Giới hạn
                "metadata": full_metadata,
                "type": doc_type,
                "storage_type": storage_type,
                "created_at": datetime.now().isoformat(),
                "source_file": file_path
            }
            
            # Lưu vào thư mục phù hợp
            storage_folder = self.type_folders.get(storage_type, self.documents_path)
            doc_file = storage_folder / f"{doc_id}.json"
            
            with open(doc_file, 'w', encoding='utf-8') as f:
                json.dump(document, f, indent=2, ensure_ascii=False)
            
            # Tạo file summary riêng
            summary_file = storage_folder / f"{doc_id}_summary.txt"
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"DOCUMENT ID: {doc_id}\n")
                f.write(f"Type: {doc_type}\n")
                f.write(f"Original: {file_path}\n")
                f.write(f"Size: {processing_result.get('file_size', 0)} bytes\n")
                f.write(f"Ingested: {datetime.now().isoformat()}\n")
                f.write("\n" + "="*50 + "\n\n")
                f.write(processing_result.get("content", "")[:2000])
            
            return {
                "status": "success",
                "document_id": doc_id,
                "type": doc_type,
                "storage_type": storage_type,
                "content_preview": processing_result.get("content", "")[:500],
                "file_info": {k: v for k, v in processing_result.items() 
                            if k not in ['content', 'error']}
            }
            
        except Exception as e:
            self.logger.error(f"Lỗi ingest file {file_path}: {e}")
            return {"status": "error", "error": str(e)}
    
    def ingest_folder(self, folder_path: str, extensions: List[str] = None) -> Dict[str, Any]:
        """Nhập cả thư mục"""
        results = {
            "total_files": 0,
            "successful": 0,
            "failed": 0,
            "by_type": {},
            "errors": []
        }
        
        folder = Path(folder_path)
        if not folder.exists():
            return {"status": "error", "error": f"Thư mục không tồn tại: {folder_path}"}
        
        # Tìm tất cả file hỗ trợ
        all_extensions = list(self.processor.supported_formats.keys())
        target_extensions = extensions or all_extensions
        
        for ext in target_extensions:
            for file_path in folder.rglob(f"*{ext}"):
                if file_path.is_file():
                    results["total_files"] += 1
                    
                    try:
                        file_result = self.ingest_file(str(file_path))
                        
                        if file_result["status"] == "success":
                            results["successful"] += 1
                            
                            # Thống kê theo type
                            doc_type = file_result.get("type", "unknown")
                            if doc_type not in results["by_type"]:
                                results["by_type"][doc_type] = 0
                            results["by_type"][doc_type] += 1
                            
                            print(f"✅ {file_path.name} -> {doc_type}")
                        else:
                            results["failed"] += 1
                            results["errors"].append({
                                "file": file_path.name,
                                "error": file_result.get("error", "unknown")
                            })
                            print(f"❌ {file_path.name}: {file_result.get('error', 'unknown')}")
                            
                    except Exception as e:
                        results["failed"] += 1
                        results["errors"].append({
                            "file": file_path.name,
                            "error": str(e)
                        })
                        print(f"❌ {file_path.name}: {e}")
        
        return results
    
    def search_documents(self, query: str, doc_type: str = None) -> List[Dict[str, Any]]:
        """Tìm kiếm tài liệu"""
        results = []
        query_lower = query.lower()
        
        # Duyệt qua tất cả thư mục
        search_folders = [self.documents_path] + list(self.type_folders.values())
        
        for folder in search_folders:
            if not folder.exists():
                continue
                
            for doc_file in folder.glob("*.json"):
                try:
                    with open(doc_file, 'r', encoding='utf-8') as f:
                        doc_data = json.load(f)
                    
                    # Lọc theo type nếu có
                    if doc_type and doc_data.get("type") != doc_type:
                        continue
                    
                    # Tìm kiếm trong content và metadata
                    content = doc_data.get("content", "").lower()
                    metadata = str(doc_data.get("metadata", {})).lower()
                    
                    if query_lower in content or query_lower in metadata:
                        results.append({
                            "id": doc_data.get("id", "unknown"),
                            "type": doc_data.get("type", "unknown"),
                            "preview": doc_data.get("content", "")[:200],
                            "metadata": doc_data.get("metadata", {}),
                            "score": content.count(query_lower) + metadata.count(query_lower),
                            "file_path": str(doc_file)
                        })
                        
                except Exception as e:
                    continue
        
        # Sắp xếp theo score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Lấy thống kê"""
        stats = {
            "total_documents": 0,
            "by_type": {},
            "by_storage": {},
            "total_size_bytes": 0
        }
        
        for folder_name, folder_path in self.type_folders.items():
            if folder_path.exists():
                json_files = list(folder_path.glob("*.json"))
                stats["by_storage"][folder_name] = len(json_files)
                stats["total_documents"] += len(json_files)
                
                # Tính tổng kích thước
                for json_file in json_files:
                    stats["total_size_bytes"] += json_file.stat().st_size
                    
                    # Đọc để phân loại theo type
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            doc_data = json.load(f)
                        
                        doc_type = doc_data.get("type", "unknown")
                        if doc_type not in stats["by_type"]:
                            stats["by_type"][doc_type] = 0
                        stats["by_type"][doc_type] += 1
                    except:
                        pass
        
        # Convert size to human readable
        size_gb = stats["total_size_bytes"] / (1024**3)
        stats["total_size_human"] = f"{size_gb:.2f} GB" if size_gb >= 1 else f"{stats['total_size_bytes'] / (1024**2):.2f} MB"
        
        return stats

def main():
    """CLI cho Advanced Document Ingestor"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Nhập đa định dạng tài liệu")
    parser.add_argument("command", choices=["ingest", "batch", "search", "stats", "list"],
                       help="Lệnh thực hiện")
    parser.add_argument("--source", help="File hoặc thư mục nguồn")
    parser.add_argument("--query", help="Từ khóa tìm kiếm")
    parser.add_argument("--type", help="Loại tài liệu (excel, pdf, word, image, etc.)")
    parser.add_argument("--extensions", help="Các đuôi file, cách nhau bằng dấu phẩy")
    parser.add_argument("--limit", type=int, default=10, help="Số kết quả hiển thị")
    
    args = parser.parse_args()
    
    ingestor = AdvancedDocumentIngestor()
    
    if args.command == "ingest":
        if not args.source:
            print("❌ Cần cung cấp --source")
            return
        
        result = ingestor.ingest_file(args.source)
        if result["status"] == "success":
            print(f"✅ Đã nhập: {result['document_id']}")
            print(f"   Type: {result['type']}")
            print(f"   Preview: {result['content_preview'][:200]}...")
        else:
            print(f"❌ Lỗi: {result.get('error', 'unknown')}")
    
    elif args.command == "batch":
        if not args.source:
            print("❌ Cần cung cấp --source")
            return
        
        extensions = None
        if args.extensions:
            extensions = [ext.strip() for ext in args.extensions.split(',')]
        
        print(f"📁 Đang xử lý thư mục: {args.source}")
        result = ingestor.ingest_folder(args.source, extensions)
        
        print(f"\n📊 KẾT QUẢ:")
        print(f"   Tổng file: {result['total_files']}")
        print(f"   Thành công: {result['successful']}")
        print(f"   Thất bại: {result['failed']}")
        
        if result['by_type']:
            print(f"\n📂 Phân loại:")
            for doc_type, count in result['by_type'].items():
                print(f"   • {doc_type}: {count}")
    
    elif args.command == "search":
        if not args.query:
            print("❌ Cần cung cấp --query")
            return
        
        results = ingestor.search_documents(args.query, args.type)
        print(f"\n🔍 KẾT QUẢ TÌM KIẾM '{args.query}' ({len(results)}):")
        
        for i, result in enumerate(results[:args.limit], 1):
            print(f"\n{i}. ID: {result['id']} ({result['type']})")
            print(f"   Preview: {result['preview']}...")
            print(f"   Score: {result['score']}")
    
    elif args.command == "stats":
        stats = ingestor.get_stats()
        print(f"\n📊 THỐNG KÊ HỆ THỐNG:")
        print(f"• Tổng tài liệu: {stats['total_documents']}")
        print(f"• Tổng kích thước: {stats['total_size_human']}")
        
        if stats['by_storage']:
            print(f"\n📂 Theo storage type:")
            for storage_type, count in stats['by_storage'].items():
                print(f"   • {storage_type}: {count}")
        
        if stats['by_type']:
            print(f"\n📄 Theo document type:")
            for doc_type, count in stats['by_type'].items():
                print(f"   • {doc_type}: {count}")
    
    elif args.command == "list":
        # Simple list of recent documents
        import glob
        doc_files = list(Path("memory/documents").rglob("*.json"))
        doc_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        print(f"\n📚 TÀI LIỆU GẦN ĐÂY ({min(args.limit, len(doc_files))}):")
        
        for i, doc_file in enumerate(doc_files[:args.limit], 1):
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    doc_data = json.load(f)
                
                doc_id = doc_data.get("id", "unknown")
                doc_type = doc_data.get("type", "unknown")
                created = doc_data.get("created_at", "unknown")
                
                print(f"{i}. {doc_id} ({doc_type})")
                print(f"   Created: {created}")
                print(f"   File: {doc_file}")
                
            except:
                print(f"{i}. {doc_file.name} (error reading)")

if __name__ == "__main__":
    main()