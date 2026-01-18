"""
Phân loại ý định người dùng
"""
import re
from typing import Dict, Any

def classify_intent(text: str, language: str = 'vi') -> Dict[str, Any]:
    """
    Phân loại intent từ văn bản
    
    Args:
        text: Văn bản đầu vào
        language: Ngôn ngữ
        
    Returns:
        Dict chứa intent và thông tin liên quan
    """
    text_lower = text.lower().strip()
    
    
    # KIỂM TRA COMMAND ĐẶC BIỆT TRƯỚC
    commands = {
        'chế độ': 'command_mode',
        'mode': 'command_mode',
        'model': 'command_model',
        'models': 'command_model',
        'mô hình': 'command_model',
        'thoát': 'command_exit',
        'exit': 'command_exit',
        'trợ giúp': 'command_help',
        'help': 'command_help',
        'test': 'command_test',
        'kiểm tra': 'command_test'
    }
    
    for cmd_key, cmd_intent in commands.items():
        if cmd_key in text_lower:
            return {
                "intent": cmd_intent,
                "confidence": 0.9,
                "is_command": True
            }
    # Từ khóa cho từng intent (tiếng Việt)
    keywords = {
        'web_search': ['tìm kiếm', 'google', 'tra cứu', 'search', 'web', 'mạng'],
        'research': ['nghiên cứu', 'thông tin', 'tài liệu', 'bài báo'],
        'coding': ['code', 'lập trình', 'python', 'viết mã', 'debug', 'sửa lỗi'],
        'planning': ['kế hoạch', 'lập kế hoạch', 'sắp xếp', 'tổ chức'],
        'summary': ['tóm tắt', 'tổng hợp', 'trích yếu'],
        'reasoning': ['phân tích', 'suy luận', 'tại sao', 'vì sao', 'nguyên nhân']
    }
    
    # Kiểm tra từng intent
    for intent, word_list in keywords.items():
        for word in word_list:
            if word in text_lower:
                return {
                    "intent": intent,
                    "confidence": 0.8,
                    "matched_keyword": word
                }
    
    # Nếu không tìm thấy, mặc định là chat
    return {
        "intent": "chat",
        "confidence": 0.5,
        "matched_keyword": None
    }