"""
Phát hiện ngôn ngữ từ input người dùng
"""
import re

def detect_language(text: str) -> str:
    """
    Phát hiện ngôn ngữ (ưu tiên tiếng Việt)
    
    Args:
        text: Văn bản đầu vào
        
    Returns:
        Mã ngôn ngữ: 'vi', 'en', hoặc 'other'
    """
    text = text.lower().strip()
    
    if not text:
        return 'vi'  # Mặc định tiếng Việt
    
    # Kiểm tra ký tự tiếng Việt
    vietnamese_pattern = re.compile(r'[àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]')
    
    if vietnamese_pattern.search(text):
        return 'vi'
    
    # Kiểm tra tiếng Anh (đơn giản)
    english_words = ['the', 'and', 'you', 'that', 'have', 'for', 'with', 'this']
    word_count = 0
    english_count = 0
    
    words = text.split()
    for word in words[:10]:  # Chỉ kiểm tra 10 từ đầu
        if len(word) > 2:
            word_count += 1
            if word in english_words:
                english_count += 1
    
    if word_count > 0 and english_count / word_count > 0.3:
        return 'en'
    
    return 'vi'  # Mặc định là tiếng Việt