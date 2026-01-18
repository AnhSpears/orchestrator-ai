"""
MAIN FILE - Điểm khởi chạy hệ thống ORCHESTRATOR
"""
import os
import sys
import logging
from datetime import datetime

# Thêm đường dẫn hiện tại vào sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chat_module.chat_router import ChatRouter
from chat_module.response_formatter import format_response

def setup_logging():
    """Thiết lập hệ thống logging"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, f"orchestrator_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def display_banner():
    """Hiển thị banner hệ thống với thông tin chi tiết"""
    print("""
╔══════════════════════════════════════════════════════════╗
║                  ORCHESTRATOR AI SYSTEM                  ║
║                  Phiên bản 1.0 - Local                  ║
║           Ngôn ngữ tự nhiên - Kiến trúc bất biến         ║
╚══════════════════════════════════════════════════════════╝

Hướng dẫn:
- Gõ tin nhắn bình thường (tiếng Việt/Anh)
- Hệ thống tự động phát hiện ngôn ngữ và ý định
- Gõ 'thoát' hoặc 'exit' để kết thúc
- Gõ 'trợ giúp' hoặc 'help' để xem hướng dẫn
- Gõ 'chế độ' hoặc 'mode' để kiểm tra trạng thái
- Gõ 'model' để xem thông tin model
""")
    
    # Kiểm tra trạng thái hệ thống
    try:
        from core_ai.llm_dispatcher import LLMDispatcher
        dispatcher = LLMDispatcher()
        
        if dispatcher.use_mock:
            print("\n⚠️  CHẾ ĐỘ: DEMO (chưa kết nối Ollama)")
            print("   Chạy 'ollama serve' để kích hoạt LLM thực")
        else:
            print(f"\n✅ CHẾ ĐỘ: FULL (với Ollama)")
            print(f"📊 Model có sẵn: {', '.join(dispatcher.available_models)}")
            
        print("\n" + "="*60)
    except Exception as e:
        print(f"\n⚠️  Không thể kiểm tra trạng thái LLM: {e}")
        print("   Hệ thống sẽ chạy ở chế độ cơ bản")
        print("\n" + "="*60)



def main():
    """Hàm chính"""
    logger = setup_logging()
    
    try:
        display_banner()
        
        # Khởi tạo hệ thống
        logger.info("Khởi động hệ thống ORCHESTRATOR...")
        router = ChatRouter()
        logger.info("Hệ thống đã sẵn sàng!")
        
        print("\nHệ thống đã sẵn sàng. Bắt đầu chat...\n")
        
        # Vòng lặp chat
        while True:
            try:
                # Nhập input từ người dùng
                user_input = input("👤 Bạn: ").strip()
                if user_input.lower() in ['chế độ', 'mode', 'status']:
                    mode_status = "DEMO" if router.brain.llm_dispatcher.use_mock else "FULL (Ollama)"
                    print(f"\n📊 TRẠNG THÁI HỆ THỐNG:")
                    print(f"- Chế độ: {mode_status}")
                    print(f"- Model hiện tại: {router.brain.llm_dispatcher.model_priority.get('chat', 'llama3:8b')}")
                    print(f"- Kết nối Ollama: {'❌ Không kết nối' if router.brain.llm_dispatcher.use_mock else '✅ Đã kết nối'}")
                    if router.brain.llm_dispatcher.use_mock:
                        print(f"- Gợi ý: Chạy 'ollama serve' để sử dụng LLM thật")
                    continue
                # Kiểm tra lệnh đặc biệt
                if user_input.lower() in ['thoát', 'exit', 'quit']:
                    print("\n👋 Tạm biệt! Hẹn gặp lại.")
                    break
                # Trong phần xử lý input
                if user_input.lower() in ['chi tiết', 'detail', 'more']:
                    print("🤖 ORCHESTRATOR: Bạn muốn tôi cung cấp thông tin chi tiết hơn về chủ đề nào?")
                    continue
                # Trong vòng lặp chat, thêm lệnh 'model':
                if user_input.lower() in ['model', 'models', 'mô hình']:
                    try:
                        print(f"\n📊 THÔNG TIN MODEL HỆ THỐNG:")
                        print(f"- Model có sẵn: {', '.join(router.brain.llm_dispatcher.available_models)}")
                        print(f"- Model ưu tiên: {router.brain.llm_dispatcher.model_priority}")
                        print(f"- Chế độ: {'DEMO' if router.brain.llm_dispatcher.use_mock else 'FULL'}")
                        
                        if router.brain.llm_dispatcher.use_mock:
                            print(f"\n💡 GỢI Ý:")
                            print(f"1. Chạy 'ollama serve' để khởi động Ollama")
                            print(f"2. Chạy 'ollama pull qwen2.5:14b' để tải model tiếng Việt tốt")
                            print(f"3. Khởi động lại hệ thống")
                    except:
                        print("🤖 ORCHESTRATOR: Không thể lấy thông tin model lúc này")
                    continue
                if user_input.lower() in ['trợ giúp', 'help']:
                    print("\n📖 HỆ THỐNG ORCHESTRATOR - TRỢ GIÚP")
                    print("Hệ thống hỗ trợ các loại yêu cầu:")
                    print("- Chat thông thường (tiếng Việt/Anh)")
                    print("- Tìm kiếm web: 'tìm thông tin về...'")
                    print("- Lập trình: 'viết code python...'")
                    print("- Phân tích: 'phân tích vấn đề...'")
                    print("- Nghiên cứu: 'thông tin về AI...'")
                    print("\nMọi yêu cầu đều xử lý tự nhiên, không cần lệnh đặc biệt.")
                    continue
                
                if not user_input:
                    print("🤖 ORCHESTRATOR: Bạn muốn hỏi gì?")
                    continue
                
                # Xử lý input
                print("🤖 ORCHESTRATOR: Đang xử lý...", end="\r")
                
                result = router.route(user_input)
                response = format_response(result)
                # Kiểm tra nếu user muốn thêm chi tiết
                if 'chi tiết' in user_input.lower() or 'detail' in user_input.lower():
                    # Thêm marker yêu cầu response dài hơn
                    if 'result' in result and isinstance(result['result'], dict):
                        result['result']['require_detail'] = True

                
                # Hiển thị response
                print(" " * 50, end="\r")  # Xóa dòng "đang xử lý"
                # Kiểm tra và xử lý response trước khi in
                if response.strip():
                    # Chia response thành các dòng
                    lines = response.strip().split('\n')
                    
                    # Loại bỏ các dòng trống và trùng lặp liền kề
                    unique_lines = []
                    for i, line in enumerate(lines):
                        line_stripped = line.strip()
                        if line_stripped and (i == 0 or line_stripped != lines[i-1].strip()):
                            unique_lines.append(line_stripped)
                    
                    # Ghép lại thành response duy nhất
                    clean_response = '\n'.join(unique_lines)
                    
                    # Chỉ in một lần
                    print(f"🤖 ORCHESTRATOR: {clean_response}\n")
                else:
                    print("🤖 ORCHESTRATOR: Không có phản hồi.\n")
                
                # Log kết quả
                logger.info(f"Input: {user_input[:50]}... | Status: {result.get('status', 'unknown')}")
                
            except KeyboardInterrupt:
                print("\n\n⏹️  Dừng hệ thống...")
                break
            except Exception as e:
                logger.error(f"Lỗi trong vòng lặp chat: {e}")
                print(f"🤖 ORCHESTRATOR: Xin lỗi, có lỗi xảy ra: {str(e)}")
    
    except Exception as e:
        logger.critical(f"Lỗi khởi động hệ thống: {e}")
        print(f"❌ Lỗi nghiêm trọng: {e}")
        return 1
    
    logger.info("Hệ thống đã dừng.")
    return 0

if __name__ == "__main__":
    sys.exit(main())