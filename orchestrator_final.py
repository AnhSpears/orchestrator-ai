"""
ORCHESTRATOR FINAL - Phiên bản hoàn chỉnh, đã fix tất cả lỗi
"""
import sys
import os
import logging
import re
from datetime import datetime

# Thêm đường dẫn
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """Thiết lập logging"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, f"orchestrator_final_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def display_final_banner():
    """Hiển thị banner cuối cùng"""
    banner = """
╔══════════════════════════════════════════════════════════╗
║               ORCHESTRATOR AI - FINAL                    ║
║                Phiên bản 3.0 - Hoàn Chỉnh                ║
╚══════════════════════════════════════════════════════════╝

TÍNH NĂNG NỔI BẬT:
✅ Deepseek-coder: Dùng prompt tiếng Anh cho code
✅ Qwen2.5:14b: Chat tiếng Việt xuất sắc  
✅ Không lỗi _select_model
✅ Response KHÔNG bị lặp
✅ Xử lý command thông minh

📋 LỆNH ĐẶC BIỆT:
• 'thoát' / 'exit' - Dừng hệ thống
• 'model' / 'mô hình' - Xem thông tin model
• 'chế độ' / 'mode' - Trạng thái hệ thống
• 'help' / 'trợ giúp' - Hướng dẫn sử dụng
• 'test' / 'kiểm tra' - Kiểm tra hệ thống

💡 MẸO DÙNG:
• Code: Hỏi bằng tiếng Anh hoặc tiếng Việt đơn giản
• Chat: Tiếng Việt tự nhiên
• Research: Tiếng Việt hoặc Anh đều được
"""
    print(banner)

def clean_response_advanced(response: str) -> str:
    """
    Làm sạch response cực mạnh - loại bỏ hoàn toàn lặp
    """
    if not response:
        return ""
    
    # 1. Chia thành đoạn
    paragraphs = response.strip().split('\n\n')
    
    # 2. Loại bỏ đoạn trùng lặp
    unique_paragraphs = []
    seen_content = set()
    
    for para in paragraphs:
        para_clean = para.strip()
        if not para_clean:
            continue
        
        # Tạo "signature" của đoạn (lấy 100 ký tự đầu, bỏ khoảng trắng)
        if len(para_clean) > 100:
            sig = para_clean[:100].lower().replace(' ', '')
        else:
            sig = para_clean.lower().replace(' ', '')
        
        # Nếu chưa thấy signature này
        if sig not in seen_content:
            seen_content.add(sig)
            unique_paragraphs.append(para_clean)
    
    # 3. Ghép lại
    result = '\n\n'.join(unique_paragraphs)
    
    # 4. Loại bỏ dòng trùng trong cùng đoạn
    lines = result.split('\n')
    final_lines = []
    prev_line = ""
    
    for line in lines:
        line_stripped = line.strip()
        if line_stripped and line_stripped != prev_line:
            final_lines.append(line_stripped)
            prev_line = line_stripped
    
    return '\n'.join(final_lines)

def test_system():
    """Kiểm tra nhanh hệ thống"""
    print("\n🧪 KIỂM TRA NHANH HỆ THỐNG...")
    
    tests = [
        ("Kết nối Ollama", lambda: check_ollama()),
        ("Import modules", lambda: check_imports()),
        ("Config files", lambda: check_configs())
    ]
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"  ✅ {test_name}")
            else:
                print(f"  ❌ {test_name}")
        except Exception as e:
            print(f"  ❌ {test_name}: {str(e)[:50]}")

def check_ollama():
    """Kiểm tra Ollama"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_imports():
    """Kiểm tra import"""
    try:
        from core_ai.brain import Brain
        from chat_module.chat_router import ChatRouter
        return True
    except Exception as e:
        print(f"    Lỗi import: {e}")
        return False

def check_configs():
    """Kiểm tra config"""
    config_files = ['config/permissions.yaml', 'config/llm_profiles.yaml']
    for file in config_files:
        if not os.path.exists(file):
            return False
    return True

def main():
    """Hàm chính phiên bản FINAL"""
    logger = setup_logging()
    
    try:
        display_final_banner()
        test_system()
        
        # Import
        from chat_module.chat_router import ChatRouter
        
        # Khởi tạo
        logger.info("🚀 Khởi động ORCHESTRATOR FINAL...")
        router = ChatRouter()
        
        # Hiển thị thông tin hệ thống
        print(f"\n{'='*60}")
        print("📊 THÔNG TIN HỆ THỐNG")
        print(f"{'='*60}")
        print(f"• Model có sẵn: {len(router.brain.llm_dispatcher.available_models)} model")
        print(f"• Coding model: {router.brain.llm_dispatcher.model_priority['coding']}")
        print(f"• Chat model: {router.brain.llm_dispatcher.model_priority['chat']}")
        print(f"• Chế độ: {'DEMO' if router.brain.llm_dispatcher.use_mock else 'FULL'}")
        print(f"{'='*60}")
        
        print("\n💬 CHAT ĐÃ SẴN SÀNG (gõ 'thoát' để dừng)")
        
        # Biến để kiểm tra lặp
        last_response = ""
        repeat_count = 0
        
        while True:
            try:
                # Nhập input
                user_input = input("\n👤 Bạn: ").strip()
                
                # Xử lý empty input
                if not user_input:
                    continue
                
                # Command đặc biệt
                if user_input.lower() in ['thoát', 'exit', 'quit']:
                    print("\n👋 Tạm biệt! Hẹn gặp lại.")
                    break
                
                if user_input.lower() in ['model', 'models', 'mô hình']:
                    print(f"\n🤖 THÔNG TIN MODEL:")
                    models = router.brain.llm_dispatcher.available_models
                    print(f"• Tổng số: {len(models)} model")
                    print(f"• Coding: {router.brain.llm_dispatcher.model_priority['coding']}")
                    print(f"• Chat: {router.brain.llm_dispatcher.model_priority['chat']}")
                    print(f"• Research: {router.brain.llm_dispatcher.model_priority['research']}")
                    print(f"\n💡 Gợi ý:")
                    print(f"  - Code: Dùng {router.brain.llm_dispatcher.model_priority['coding']} (tiếng Anh)")
                    print(f"  - Chat: Dùng {router.brain.llm_dispatcher.model_priority['chat']} (tiếng Việt)")
                    continue
                
                if user_input.lower() in ['chế độ', 'mode', 'status']:
                    mode = "DEMO" if router.brain.llm_dispatcher.use_mock else "FULL"
                    print(f"\n⚙️ TRẠNG THÁI HỆ THỐNG:")
                    print(f"• Chế độ: {mode}")
                    print(f"• Model hiện tại: {router.brain.llm_dispatcher.model_priority}")
                    print(f"• Kết nối Ollama: {'❌ Chưa kết nối' if router.brain.llm_dispatcher.use_mock else '✅ Đã kết nối'}")
                    continue
                
                if user_input.lower() in ['help', 'trợ giúp', 'hướng dẫn']:
                    print(f"\n📖 HƯỚNG DẪN SỬ DỤNG ORCHESTRATOR:")
                    print("1. Chat thông thường: Tiếng Việt/Anh tự nhiên")
                    print("2. Viết code: Dùng tiếng Anh hoặc tiếng Việt đơn giản")
                    print("   Ví dụ: 'Write Python function to read CSV'")
                    print("3. Nghiên cứu: Hỏi bằng tiếng Việt hoặc Anh")
                    print("4. Lệnh: 'model', 'chế độ', 'thoát', 'help'")
                    print("\n⚠️ LƯU Ý: deepseek-coder chỉ hiểu tiếng Anh cho code")
                    continue
                
                # Xử lý chat
                print("🤖 Đang xử lý...", end="", flush=True)
                
                # Gọi router
                result = router.route(user_input)
                
                # Xóa dòng "đang xử lý"
                print("\r" + " " * 50 + "\r", end="")
                
                if result.get('status') == 'success':
                    llm_result = result.get('result', {})
                    response_text = llm_result.get('response', '')
                    model = llm_result.get('model', 'unknown')
                    mode = llm_result.get('mode', 'real')
                    
                    # Làm sạch response cực mạnh
                    cleaned_response = clean_response_advanced(response_text)
                    
                    # Kiểm tra lặp với response trước đó
                    if cleaned_response == last_response:
                        repeat_count += 1
                        if repeat_count >= 2:
                            print("⚠️  Phát hiện response lặp, bỏ qua...")
                            continue
                    else:
                        repeat_count = 0
                        last_response = cleaned_response
                    
                    # Hiển thị
                    if 'coder' in model.lower():
                        print(f"🤖 [{model} - Coding Assistant]:")
                    elif mode == 'mock':
                        print(f"🤖 [Demo Mode]:")
                    else:
                        print(f"🤖 [{model}]:")
                    
                    print(f"{cleaned_response}\n")
                    
                    # Log
                    logger.info(f"Input: {user_input[:50]}... | Model: {model} | Len: {len(response_text)}")
                    
                else:
                    print(f"❌ Lỗi: {result.get('error', 'Không xác định')}\n")
                    logger.error(f"Error: {result.get('error')}")
                
            except KeyboardInterrupt:
                print("\n\n🛑 Đã dừng bởi người dùng")
                break
            except Exception as e:
                print(f"\n⚠️  Lỗi hệ thống: {str(e)[:100]}")
                logger.error(f"Lỗi trong chat: {e}")
    
    except Exception as e:
        logger.critical(f"Lỗi khởi động hệ thống: {e}")
        print(f"❌ Lỗi nghiêm trọng: {e}")
        return 1
    
    logger.info("Hệ thống đã dừng")
    return 0

if __name__ == "__main__":
    sys.exit(main())