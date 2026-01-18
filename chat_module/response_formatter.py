"""
Định dạng response thành ngôn ngữ tự nhiên
"""
import logging
from typing import Dict, Any

def format_response(result: Dict[str, Any]) -> str:
    """
    Định dạng kết quả từ Brain thành phản hồi tự nhiên
    
    Args:
        result: Kết quả từ Brain
        
    Returns:
        Phản hồi đã định dạng
    """
    logger = logging.getLogger(__name__)
    
    try:
        if result.get('status') == 'error':
            return result.get('fallback', 'Xin lỗi, có lỗi xảy ra.')
        
        # Lấy response từ LLM
        llm_response = result.get('result', {})
        if isinstance(llm_response, dict):
            response_text = llm_response.get('response', '')
        else:
            response_text = str(llm_response)
        
        # Làm sạch response
        response_text = response_text.strip()
        
        # Đảm bảo response không rỗng
        if not response_text:
            response_text = "Tôi không có thông tin để trả lời câu hỏi này."
        
        # Định dạng cơ bản
        if len(response_text) < 100:
            # Response ngắn
            formatted = response_text
        else:
            # Response dài - thêm định dạng
            sentences = response_text.split('. ')
            if len(sentences) > 1:
                formatted = '.\n\n'.join(sentences[:3]) + '.'
                if len(sentences) > 3:
                    formatted += '...'
            else:
                formatted = response_text
        
        return formatted
        
    except Exception as e:
        logger.error(f"Lỗi định dạng response: {e}")
        return "Xin lỗi, tôi gặp vấn đề khi tạo phản hồi."