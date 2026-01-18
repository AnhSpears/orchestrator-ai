"""
Định tuyến chat đến core_ai
"""
import logging
from typing import Dict, Any
from core_ai.brain import Brain

class ChatRouter:
    def __init__(self):
        self.brain = Brain()
        self.logger = logging.getLogger(__name__)
    
    def route(self, user_input: str) -> Dict[str, Any]:
        """
        Định tuyến input người dùng qua toàn bộ pipeline
        
        Args:
            user_input: Input từ người dùng
            
        Returns:
            Kết quả xử lý
        """
        try:
            self.logger.info(f"Routing input: {user_input[:50]}...")
            
            # 1. Chuẩn hóa task
            task = self._normalize_task(user_input)
            
            # 2. Gửi đến Brain xử lý
            result = self.brain.process(task)
            
            # 3. Thêm thông tin routing
            result['routing_info'] = {
                'input_length': len(user_input),
                'task_type': task.get('intent', 'unknown')
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Lỗi routing: {e}")
            return {
                "status": "error",
                "error": f"Lỗi định tuyến: {str(e)}",
                "fallback": "Xin lỗi, tôi không thể xử lý yêu cầu này ngay lúc này."
            }
    
    def _normalize_task(self, user_input: str) -> Dict[str, Any]:
        """
        Chuẩn hóa input thành task cho core_ai
        
        Args:
            user_input: Input thô từ người dùng
            
        Returns:
            Task đã chuẩn hóa
        """
        from .language_detect import detect_language
        from .intent_classifier import classify_intent
        
        # Phát hiện ngôn ngữ
        language = detect_language(user_input)
        
        # Phân loại intent
        intent_info = classify_intent(user_input, language)
        
        # Tạo task chuẩn hóa
        task = {
            "content": user_input,
            "language": language,
            "intent": intent_info["intent"],
            "confidence": intent_info["confidence"],
            "source": "chat_interface",
            "requires_response": True
        }
        
        return task