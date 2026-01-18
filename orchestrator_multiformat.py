"""
ORCHESTRATOR MULTIFORMAT - Hỗ trợ đa định dạng tài liệu
"""
import sys
import os
import logging
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, f"orchestrator_multiformat_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

class MultiFormatOrchestrator:
    """Orchestrator hỗ trợ đa định dạng"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Kiểm tra và import modules
        self.modules_status = self._check_modules()
        
        # Khởi tạo các module có sẵn
        self._init_modules()
        
        self.display_banner()
    
    def _check_modules(self) -> Dict[str, bool]:
        """Kiểm tra modules có sẵn"""
        modules = {
            "chat_router": False,
            "multiformat_processor": False,
            "advanced_ingestor": False,
            "memory_system": False
        }
        
        try:
            from chat_module.chat_router import ChatRouter
            modules["chat_router"] = True
        except ImportError:
            self.logger.warning("ChatRouter không có sẵn")
        
        try:
            from tools.multiformat_processor import MultiFormatProcessor
            modules["multiformat_processor"] = True
        except ImportError:
            self.logger.warning("MultiFormatProcessor không có sẵn")
        
        try:
            from tools.advanced_document_ingestor import AdvancedDocumentIngestor
            modules["advanced_ingestor"] = True
        except ImportError:
            self.logger.warning("AdvancedDocumentIngestor không có sẵn")
        
        try:
            from memory.memory_system import MemorySystem
            modules["memory_system"] = True
        except ImportError:
            self.logger.warning("MemorySystem không có sẵn")
        
        return modules
    
    def _init_modules(self):
        """Khởi tạo modules"""
        if self.modules_status["chat_router"]:
            from chat_module.chat_router import ChatRouter
            self.router = ChatRouter()
        else:
            self.router = None
        
        if self.modules_status["multiformat_processor"]:
            from tools.multiformat_processor import MultiFormatProcessor
            self.processor = MultiFormatProcessor()
        else:
            self.processor = None
        
        if self.modules_status["advanced_ingestor"]:
            from tools.advanced_document_ingestor import AdvancedDocumentIngestor
            self.ingestor = AdvancedDocumentIngestor()
        else:
            self.ingestor = None
        
        if self.modules_status["memory_system"]:
            from memory.memory_system import MemorySystem
            self.memory = MemorySystem()
        else:
            self.memory = None
    
    def display_banner(self):
        """Hiển thị banner"""
        banner = f"""
╔══════════════════════════════════════════════════════════╗
║              ORCHESTRATOR MULTIFORMAT                    ║
║            Phiên bản 5.0 - Đa Định Dạng                  ║
╚══════════════════════════════════════════════════════════╝

📋 ĐỊNH DẠNG ĐƯỢC HỖ TRỢ:

📄 VĂN BẢN: .txt, .md, .json, .yaml, .xml, .html
📊 EXCEL: .xlsx, .xls (đọc sheets, headers, data)
📈 POWERPOINT: .pptx, .ppt (extract text từ slides)
📝 WORD: .docx (extract paragraphs, tables)
📑 PDF: .pdf (extract text, page count)
🖼️ HÌNH ẢNH: .jpg, .png, .bmp, .gif, .tiff (OCR)
💻 CODE: .py, .js, .java, .cpp, .c, .html, .css
📊 DATA: .csv, .json, .xml

🚀 LỆNH HỆ THỐNG:
• nhập file: <đường_dẫn>     - Nhập file đơn
• nhập thư mục: <đường_dẫn>  - Nhập cả thư mục
• tìm tài liệu: <từ_khóa>    - Tìm kiếm
• thống kê                   - Xem thống kê
• định dạng hỗ trợ           - Xem định dạng hỗ trợ
• thoát                      - Kết thúc
"""
        print(banner)
        
        # Hiển thị trạng thái modules
        print("📊 TRẠNG THÁI MODULES:")
        for module, available in self.modules_status.items():
            status = "✅ Sẵn sàng" if available else "❌ Không có"
            print(f"  • {module:25s}: {status}")
        print()

def main():
    """Chương trình chính"""
    logger = setup_logging()
    
    try:
        orchestrator = MultiFormatOrchestrator()
        
        print("💬 BẮT ĐẦU CHAT (gõ 'thoát' để dừng)")
        
        while True:
            try:
                user_input = input("\n👤 Bạn: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['thoát', 'exit', 'quit']:
                    print("\n👋 Tạm biệt!")
                    break
                
                if user_input.lower() in ['trợ giúp', 'help']:
                    orchestrator.display_banner()
                    continue
                
                if user_input.lower() in ['định dạng hỗ trợ', 'supported formats']:
                    if orchestrator.processor:
                        print("\n📋 ĐỊNH DẠNG ĐƯỢC HỖ TRỢ:")
                        for ext in sorted(orchestrator.processor.supported_formats.keys()):
                            print(f"  • {ext}")
                        print(f"\nTổng cộng: {len(orchestrator.processor.supported_formats)} định dạng")
                    else:
                        print("❌ MultiFormatProcessor chưa có sẵn")
                    continue
                
                if user_input.lower() in ['thống kê', 'stats']:
                    if orchestrator.ingestor:
                        stats = orchestrator.ingestor.get_stats()
                        print(f"\n📊 THỐNG KÊ TÀI LIỆU:")
                        print(f"• Tổng tài liệu: {stats.get('total_documents', 0)}")
                        print(f"• Tổng kích thước: {stats.get('total_size_human', '0 MB')}")
                        
                        if stats.get('by_type'):
                            print(f"\n📄 Phân loại theo type:")
                            for doc_type, count in stats['by_type'].items():
                                print(f"  • {doc_type}: {count}")
                    else:
                        print("❌ AdvancedDocumentIngestor chưa có sẵn")
                    continue
                
                # Xử lý lệnh nhập tài liệu
                if user_input.startswith('nhập file:'):
                    if orchestrator.ingestor:
                        file_path = user_input.replace('nhập file:', '').strip()
                        if os.path.exists(file_path):
                            print(f"📥 Đang nhập file: {file_path}")
                            result = orchestrator.ingestor.ingest_file(file_path)
                            
                            if result.get('status') == 'success':
                                print(f"✅ Đã nhập: {result['document_id']}")
                                print(f"   Type: {result['type']}")
                                print(f"   Storage: {result['storage_type']}")
                            else:
                                print(f"❌ Lỗi: {result.get('error', 'unknown')}")
                        else:
                            print(f"❌ File không tồn tại: {file_path}")
                    else:
                        print("❌ AdvancedDocumentIngestor chưa có sẵn")
                    continue
                
                if user_input.startswith('nhập thư mục:'):
                    if orchestrator.ingestor:
                        folder_path = user_input.replace('nhập thư mục:', '').strip()
                        if os.path.isdir(folder_path):
                            print(f"📁 Đang nhập thư mục: {folder_path}")
                            result = orchestrator.ingestor.ingest_folder(folder_path)
                            
                            print(f"\n📊 KẾT QUẢ:")
                            print(f"   Tổng file: {result.get('total_files', 0)}")
                            print(f"   Thành công: {result.get('successful', 0)}")
                            print(f"   Thất bại: {result.get('failed', 0)}")
                            
                            if result.get('by_type'):
                                print(f"\n📂 Phân loại:")
                                for doc_type, count in result['by_type'].items():
                                    print(f"   • {doc_type}: {count}")
                        else:
                            print(f"❌ Thư mục không tồn tại: {folder_path}")
                    else:
                        print("❌ AdvancedDocumentIngestor chưa có sẵn")
                    continue
                
                if user_input.startswith('tìm tài liệu:'):
                    if orchestrator.ingestor:
                        query = user_input.replace('tìm tài liệu:', '').strip()
                        print(f"🔍 Đang tìm: '{query}'")
                        results = orchestrator.ingestor.search_documents(query)
                        
                        print(f"\n📄 Tìm thấy {len(results)} kết quả:")
                        for i, result in enumerate(results[:5], 1):
                            print(f"\n{i}. ID: {result['id']} ({result['type']})")
                            print(f"   Preview: {result['preview']}...")
                    else:
                        print("❌ AdvancedDocumentIngestor chưa có sẵn")
                    continue
                
                # Chat thông thường
                if orchestrator.router:
                    print("🤖 Đang xử lý...", end="", flush=True)
                    
                    result = orchestrator.router.route(user_input)
                    
                    print("\r" + " " * 50 + "\r", end="")
                    
                    if result.get('status') == 'success':
                        result_data = result.get('result', {})
                        if isinstance(result_data, dict):
                            response = result_data.get('response', '')
                            model = result_data.get('model', 'unknown')
                            
                            if model:
                                print(f"🤖 [{model}]:")
                            else:
                                print(f"🤖 ORCHESTRATOR:")
                            
                            if response:
                                print(f"{response}\n")
                        else:
                            print(f"🤖 ORCHESTRATOR: {result_data}\n")
                    else:
                        print(f"❌ Lỗi: {result.get('error', 'Không xác định')}\n")
                else:
                    print("❌ Chat Router chưa sẵn sàng. Vui lòng sử dụng lệnh nhập tài liệu.")
                
            except KeyboardInterrupt:
                print("\n\n🛑 Đã dừng bởi người dùng")
                break
            except Exception as e:
                print(f"\n⚠️ Lỗi: {str(e)[:100]}")
                logger.error(f"Lỗi: {e}")
    
    except Exception as e:
        logger.critical(f"Lỗi khởi động: {e}")
        print(f"❌ Lỗi nghiêm trọng: {e}")
        return 1
    
    logger.info("Hệ thống đã dừng")
    return 0

if __name__ == "__main__":
    sys.exit(main())