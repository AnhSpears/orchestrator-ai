"""
ORCHESTRATOR WITH AI-AGENT - Phiên bản tích hợp AI Agent thông minh
"""
import sys
import os
import logging
from datetime import datetime
from typing import Dict, Any  # THÊM DÒNG NÀY

# Thêm đường dẫn
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """Thiết lập logging"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, f"orchestrator_ai_agent_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def display_ai_agent_banner():
    """Hiển thị banner AI Agent"""
    banner = """
╔══════════════════════════════════════════════════════════╗
║              ORCHESTRATOR AI WITH AI-AGENT               ║
║                Phiên bản 4.0 - Thông Minh                ║
╚══════════════════════════════════════════════════════════╝

TÍNH NĂNG AI-AGENT MỚI:
🧠 BỘ NHỚ THÔNG MINH: Học và ghi nhớ mọi thứ
📚 HỌC TỪ TÀI LIỆU: Đọc, phân tích, lưu trữ kiến thức
💻 TỰ HỌC CODE: Phân tích pattern, đề xuất cải tiến
🔍 TỰ TEST & NÂNG CẤP: Kiểm tra chất lượng tự động
🤖 6 SUB-AGENT: Planner, Researcher, Coder, Reviewer, Security, Learner

📋 LỆNH ĐẶC BIỆT AI-AGENT:
• 'học tài liệu: <nội dung>' - Học từ tài liệu
• 'học code: <code>' - Học từ code mẫu
• 'tạo kế hoạch: <mục tiêu>' - Lập kế hoạch thông minh
• 'nghiên cứu: <chủ đề>' - Nghiên cứu thông minh
• 'kiểm tra bộ nhớ' - Xem thống kê memory
• 'lịch sử học tập' - Xem lịch sử học

💡 MẸO SỬ DỤNG:
1. AI-Agent tự động học từ mọi tương tác
2. Hệ thống memory lưu trữ vĩnh viễn
3. Có thể học không giới hạn tài liệu
4. Tự đề xuất cải tiến code
5. Tự test và đánh giá chất lượng
"""
    print(banner)

class OrchestratorWithAIAgent:
    """Orchestrator với AI Agent tích hợp"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Import các module
        try:
            from chat_module.chat_router import ChatRouter
            self.router = ChatRouter()
            self.logger.info("✅ Đã khởi tạo ChatRouter")
        except ImportError as e:
            self.logger.error(f"❌ Lỗi import ChatRouter: {e}")
            self.router = None
        
        try:
            # Thử import AI Agent (có thể chưa tồn tại)
            from agents.ai_agent import AIAgent
            self.ai_agent = AIAgent()
            self.logger.info("✅ Đã khởi tạo AI Agent")
        except ImportError as e:
            self.logger.warning(f"⚠️ Chưa có AI Agent module: {e}")
            self.ai_agent = None
        
        try:
            from memory.memory_system import MemorySystem
            self.memory = MemorySystem()
            self.logger.info("✅ Đã khởi tạo Memory System")
        except ImportError as e:
            self.logger.warning(f"⚠️ Chưa có Memory System module: {e}")
            self.memory = None
    
    def process_user_input(self, user_input: str, session_id: str = "default") -> Dict[str, Any]:
        """Xử lý input người dùng với AI Agent"""
        try:
            # Kiểm tra lệnh đặc biệt AI Agent
            if user_input.startswith('học tài liệu:'):
                content = user_input.replace('học tài liệu:', '').strip()
                return self._process_learning(content, "document", session_id)
            
            elif user_input.startswith('học code:'):
                content = user_input.replace('học code:', '').strip()
                return self._process_learning(content, "code", session_id)
            
            elif user_input.startswith('tạo kế hoạch:'):
                goal = user_input.replace('tạo kế hoạch:', '').strip()
                return self._process_planning(goal, session_id)
            
            elif user_input.startswith('nghiên cứu:'):
                topic = user_input.replace('nghiên cứu:', '').strip()
                return self._process_research(topic, session_id)
            
            elif user_input in ['kiểm tra bộ nhớ', 'memory stats']:
                return self._check_memory_stats()
            
            elif user_input in ['lịch sử học tập', 'learning history']:
                return self._get_learning_history()
            
            # Xử lý thông thường qua router
            if self.router:
                result = self.router.route(user_input)
                
                # Tự động học từ interaction
                self._auto_learn_from_interaction(user_input, result, session_id)
                
                return result
            else:
                return {
                    "status": "error",
                    "error": "ChatRouter chưa được khởi tạo",
                    "fallback": "Xin lỗi, hệ thống chưa sẵn sàng."
                }
            
        except Exception as e:
            self.logger.error(f"Lỗi xử lý input: {e}")
            return {
                "status": "error",
                "error": str(e),
                "fallback": "Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu."
            }
    
    def _process_learning(self, content: str, content_type: str, session_id: str) -> Dict[str, Any]:
        """Xử lý học tập"""
        if not self.ai_agent:
            return {
                "status": "error",
                "error": "AI Agent chưa được khởi tạo",
                "fallback": "Tính năng học tập chưa sẵn sàng. Vui lòng kiểm tra lại cài đặt."
            }
        
        task = {
            "intent": "learning",
            "user_input": f"Học {content_type}",
            "content": content,
            "content_type": content_type,
            "session_id": session_id
        }
        
        result = self.ai_agent.process(task)
        
        return {
            "status": "success",
            "result": result,
            "type": "ai_agent_learning",
            "timestamp": datetime.now().isoformat()
        }
    
    def _process_planning(self, goal: str, session_id: str) -> Dict[str, Any]:
        """Xử lý tạo kế hoạch"""
        if not self.ai_agent:
            return {
                "status": "error",
                "error": "AI Agent chưa được khởi tạo",
                "fallback": "Tính năng lập kế hoạch chưa sẵn sàng."
            }
        
        task = {
            "intent": "planning",
            "user_input": goal,
            "session_id": session_id
        }
        
        result = self.ai_agent.process(task)
        
        return {
            "status": "success",
            "result": result,
            "type": "ai_agent_planning",
            "timestamp": datetime.now().isoformat()
        }
    
    def _process_research(self, topic: str, session_id: str) -> Dict[str, Any]:
        """Xử lý nghiên cứu"""
        if not self.ai_agent:
            return {
                "status": "error",
                "error": "AI Agent chưa được khởi tạo",
                "fallback": "Tính năng nghiên cứu chưa sẵn sàng."
            }
        
        task = {
            "intent": "research",
            "user_input": topic,
            "session_id": session_id
        }
        
        result = self.ai_agent.process(task)
        
        return {
            "status": "success",
            "result": result,
            "type": "ai_agent_research",
            "timestamp": datetime.now().isoformat()
        }
    
    def _check_memory_stats(self) -> Dict[str, Any]:
        """Kiểm tra thống kê bộ nhớ"""
        if not self.memory:
            return {
                "status": "success",
                "result": {
                    "response": "Hệ thống bộ nhớ chưa được khởi tạo",
                    "stats": {}
                },
                "type": "memory_stats"
            }
        
        try:
            import json
            index_file = self.memory.base_path / "memory_index.json"
            if index_file.exists():
                with open(index_file, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
                
                return {
                    "status": "success",
                    "result": {
                        "response": "Thống kê hệ thống bộ nhớ",
                        "stats": stats,
                        "memory_path": str(self.memory.base_path)
                    },
                    "type": "memory_stats"
                }
            else:
                return {
                    "status": "success",
                    "result": {
                        "response": "Hệ thống bộ nhớ chưa được khởi tạo đầy đủ",
                        "stats": {}
                    },
                    "type": "memory_stats"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "type": "memory_stats"
            }
    
    def _get_learning_history(self) -> Dict[str, Any]:
        """Lấy lịch sử học tập"""
        if not self.ai_agent:
            return {
                "status": "error",
                "error": "AI Agent chưa được khởi tạo",
                "fallback": "Không có dữ liệu học tập."
            }
        
        try:
            summary = self.ai_agent.get_learning_summary()
            
            return {
                "status": "success",
                "result": {
                    "response": "Lịch sử học tập của AI Agent",
                    "summary": summary,
                    "total_sessions": len(self.ai_agent.learning_history) if hasattr(self.ai_agent, 'learning_history') else 0
                },
                "type": "learning_history"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "type": "learning_history"
            }
    
    def _auto_learn_from_interaction(self, user_input: str, result: Dict[str, Any], session_id: str):
        """Tự động học từ tương tác"""
        try:
            # Chỉ học nếu result thành công và có memory system
            if result.get('status') == 'success' and self.memory:
                learning_content = {
                    "user_input": user_input,
                    "result_preview": str(result.get('result', {}))[:200],
                    "session_id": session_id,
                    "learned_at": datetime.now().isoformat()
                }
                
                # Lưu vào memory
                self.memory.save_short_term(session_id, {
                    "interaction": learning_content
                })
                
        except Exception as e:
            self.logger.debug(f"Lỗi auto-learn: {e}")

def main():
    """Hàm chính"""
    logger = setup_logging()
    
    try:
        display_ai_agent_banner()
        
        # Khởi tạo Orchestrator với AI Agent
        logger.info("🚀 Khởi động Orchestrator với AI Agent...")
        orchestrator = OrchestratorWithAIAgent()
        
        print("\n📊 KIỂM TRA HỆ THỐNG AI-AGENT")
        print("="*60)
        
        # Hiển thị trạng thái các module
        modules_status = []
        if orchestrator.router:
            modules_status.append("✅ ChatRouter: Đã sẵn sàng")
        else:
            modules_status.append("❌ ChatRouter: Chưa khởi tạo được")
        
        if orchestrator.ai_agent:
            modules_status.append("✅ AI Agent: Đã sẵn sàng")
        else:
            modules_status.append("⚠️ AI Agent: Chưa có module (có thể bỏ qua)")
        
        if orchestrator.memory:
            modules_status.append("✅ Memory System: Đã sẵn sàng")
        else:
            modules_status.append("⚠️ Memory System: Chưa có module (có thể bỏ qua)")
        
        for status in modules_status:
            print(f"   {status}")
        
        print("\n💡 LƯU Ý:")
        print("   - Nếu thiếu module, hệ thống vẫn chạy với tính năng cơ bản")
        print("   - Để có đầy đủ tính năng, tạo các file module bị thiếu")
        print("="*60)
        
        print("\n💬 BẮT ĐẦU CHAT (gõ 'thoát' để dừng)")
        
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        while True:
            try:
                # Nhập input
                user_input = input("\n👤 Bạn: ").strip()
                
                # Xử lý lệnh đặc biệt
                if not user_input:
                    continue
                    
                if user_input.lower() in ['thoát', 'exit', 'quit']:
                    print("\n👋 Tạm biệt!")
                    break
                
                if user_input.lower() in ['trợ giúp', 'help']:
                    print("\n📖 TRỢ GIÚP ORCHESTRATOR WITH AI-AGENT:")
                    print("Lệnh thông thường:")
                    print("  - Chat: Gõ bình thường (tiếng Việt/Anh)")
                    print("  - Code: 'Viết code Python đọc file'")
                    print("\nLệnh AI-Agent (nếu module có sẵn):")
                    print("  - 'học tài liệu: <nội dung>'")
                    print("  - 'học code: <code mẫu>'")
                    print("  - 'tạo kế hoạch: <mục tiêu>'")
                    print("  - 'nghiên cứu: <chủ đề>'")
                    print("  - 'kiểm tra bộ nhớ'")
                    print("  - 'lịch sử học tập'")
                    continue
                
                if user_input.lower() in ['model', 'models']:
                    print("\n🤖 THÔNG TIN HỆ THỐNG:")
                    if orchestrator.router and hasattr(orchestrator.router.brain, 'llm_dispatcher'):
                        print(f"• Model có sẵn: {len(orchestrator.router.brain.llm_dispatcher.available_models)} model")
                        print(f"• Coding model: {orchestrator.router.brain.llm_dispatcher.model_priority.get('coding', 'N/A')}")
                        print(f"• Chat model: {orchestrator.router.brain.llm_dispatcher.model_priority.get('chat', 'N/A')}")
                    else:
                        print("• Model info: Không có thông tin")
                    
                    print(f"• AI Agent: {'Đã tích hợp' if orchestrator.ai_agent else 'Chưa có'}")
                    print(f"• Memory System: {'Đã tích hợp' if orchestrator.memory else 'Chưa có'}")
                    continue
                
                if user_input.lower() in ['status', 'trạng thái']:
                    print("\n⚙️ TRẠNG THÁI HỆ THỐNG:")
                    print(f"• Session ID: {session_id}")
                    print(f"• ChatRouter: {'✅ Đã sẵn sàng' if orchestrator.router else '❌ Chưa sẵn sàng'}")
                    print(f"• AI Agent: {'✅ Đã sẵn sàng' if orchestrator.ai_agent else '❌ Chưa sẵn sàng'}")
                    print(f"• Memory System: {'✅ Đã sẵn sàng' if orchestrator.memory else '❌ Chưa sẵn sàng'}")
                    continue
                
                # Xử lý
                print("🤖 Đang xử lý...", end="", flush=True)
                
                result = orchestrator.process_user_input(user_input, session_id)
                
                # Xóa dòng "đang xử lý"
                print("\r" + " " * 50 + "\r", end="")
                
                # Hiển thị kết quả
                if result.get('status') == 'success':
                    result_data = result.get('result', {})
                    result_type = result.get('type', 'normal')
                    
                    if result_type == 'ai_agent_learning':
                        ai_result = result_data.get('result', {})
                        response = ai_result.get('response', 'Đã học xong')
                        print(f"🧠 AI-AGENT [Learner]: {response}")
                        
                        # Hiển thị thêm thông tin
                        if 'key_points' in ai_result:
                            print("   📝 Điểm chính đã học:")
                            for point in ai_result['key_points'][:3]:
                                print(f"     • {point}")
                                
                    elif result_type == 'ai_agent_planning':
                        ai_result = result_data.get('result', {})
                        response = ai_result.get('response', 'Kế hoạch đã tạo')
                        print(f"🧠 AI-AGENT [Planner]: {response}")
                        
                        plan = ai_result.get('plan', {})
                        if plan and 'steps' in plan:
                            print("   📋 Các bước thực hiện:")
                            for step in plan['steps'][:4]:
                                print(f"     {step}")
                                
                    elif result_type == 'ai_agent_research':
                        ai_result = result_data.get('result', {})
                        response = ai_result.get('response', 'Nghiên cứu hoàn tất')
                        print(f"🧠 AI-AGENT [Researcher]: {response}")
                        
                        research = ai_result.get('research', {})
                        if research:
                            print(f"   📊 Tài liệu tìm thấy: {research.get('documents_found', 0)}")
                            print(f"   🧠 Ký ức liên quan: {research.get('memories_found', 0)}")
                            
                    elif result_type == 'memory_stats':
                        stats_data = result_data.get('stats', {})
                        print("🧠 AI-AGENT [Memory System]:")
                        if stats_data:
                            print(f"   📈 Tổng mục: {stats_data.get('total_entries', 0)}")
                            categories = stats_data.get('categories', {})
                            for cat, count in categories.items():
                                print(f"   • {cat}: {count}")
                        else:
                            print("   ℹ️ Chưa có dữ liệu thống kê")
                            
                    elif result_type == 'learning_history':
                        summary = result_data.get('summary', {})
                        print("🧠 AI-AGENT [Learning History]:")
                        if summary and summary.get('message') != 'Chưa có lịch sử học tập':
                            print(f"   📚 Tổng phiên học: {summary.get('total_learning_sessions', 0)}")
                            if 'agent_usage' in summary:
                                print("   🤖 Sử dụng agent:")
                                for agent, count in summary['agent_usage'].items():
                                    print(f"     • {agent}: {count}")
                        else:
                            print("   ℹ️ Chưa có lịch sử học tập")
                                
                    else:
                        # Kết quả thông thường từ LLM
                        if isinstance(result_data, dict):
                            response = result_data.get('response', '')
                            model = result_data.get('model', 'unknown')
                            
                            if 'coder' in model.lower():
                                print(f"🤖 [{model} - Coding Assistant]:")
                            else:
                                print(f"🤖 [{model}]:")
                            
                            # Hiển thị response
                            if response:
                                print(f"{response}\n")
                            
                            # Tự động học nếu có code
                            if '```python' in str(response):
                                print("   💡 Hệ thống đã tự động học code pattern này")
                        else:
                            print(f"🤖 ORCHESTRATOR: {result_data}\n")
                    
                else:
                    print(f"❌ Lỗi: {result.get('error', 'Không xác định')}")
                    if result.get('fallback'):
                        print(f"💡 Fallback: {result.get('fallback')}")
                    print()
                
                # Log
                logger.info(f"Input: {user_input[:50]}... | Type: {result.get('type', 'normal')}")
                
            except KeyboardInterrupt:
                print("\n\n🛑 Đã dừng bởi người dùng")
                break
            except Exception as e:
                print(f"\n⚠️ Lỗi: {str(e)[:100]}")
                logger.error(f"Lỗi trong chat: {e}")
    
    except Exception as e:
        logger.critical(f"Lỗi khởi động: {e}")
        print(f"❌ Lỗi nghiêm trọng: {e}")
        return 1
    
    logger.info("Hệ thống đã dừng")
    return 0

if __name__ == "__main__":
    sys.exit(main())