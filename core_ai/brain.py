"""
BRAIN - Bộ não điều phối trung tâm
Chỉ nhận task đã chuẩn hóa, không biết UI/CLI/Web
"""
import logging
from typing import Dict, Any
# THÊM IMPORT TẠI ĐÂY - TRƯỚC KHI SỬ DỤNG
from .reasoning_engine import ReasoningEngine
from .llm_dispatcher import LLMDispatcher

class Brain:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.reasoning_engine = ReasoningEngine()
        self.llm_dispatcher = LLMDispatcher()
        
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Xử lý task theo luồng: Reason → Plan → Dispatch
        
        Args:
            task: Task đã chuẩn hóa từ chat_module
            
        Returns:
            Kết quả xử lý
        """
        try:
            self.logger.info(f"Brain nhận task: {task.get('intent', 'unknown')}")
            
            # 1. Reasoning - Phân tích và lập kế hoạch
            plan = self.reasoning_engine.analyze(task)
            
            # 2. Dispatch - Phân phối cho LLM phù hợp
            result = self.llm_dispatcher.dispatch(plan)
            
            self.logger.info(f"Brain hoàn thành task")
            return {
                "status": "success",
                "result": result,
                "plan": plan
            }
            
        except Exception as e:
            self.logger.error(f"Lỗi trong Brain.process: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "fallback": "Hệ thống đang gặp sự cố. Vui lòng thử lại."
            }