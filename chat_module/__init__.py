"""
CHAT MODULE - Xử lý ngôn ngữ tự nhiên
"""
from .language_detect import detect_language
from .intent_classifier import classify_intent
from .chat_router import ChatRouter
from .response_formatter import format_response

__all__ = [
    'detect_language',
    'classify_intent', 
    'ChatRouter',
    'format_response'
]