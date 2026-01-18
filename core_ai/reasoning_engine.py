"""
REASONING ENGINE - Máy suy luận
Phân tích task và tạo kế hoạch xử lý
"""
import yaml
import logging
from typing import Dict, Any

class ReasoningEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.load_permissions()
        
    def load_permissions(self):
        """Tải file permissions.yaml"""
        try:
            with open('config/permissions.yaml', 'r') as f:
                self.permissions = yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Không thể tải permissions: {e}")
            self.permissions = {}
    
    def analyze(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phân tích task và tạo kế hoạch
        
        Args:
            task: Task từ user
            
        Returns:
            Kế hoạch xử lý chi tiết
        """
        intent = task.get('intent', 'chat')
        language = task.get('language', 'vi')
        
        # Xác định loại LLM cần dùng dựa trên intent
        llm_type = self._determine_llm_type(intent)
        
        # Xác định tools cần dùng
        tools = self._determine_tools(intent)
        
        # Xác định agent cần gọi (nếu có)
        agent = self._determine_agent(intent)
        
        plan = {
            "intent": intent,
            "language": language,
            "llm_type": llm_type,
            "tools": tools,
            "agent": agent,
            "user_input": task.get('content', ''),
            "requires_web_search": intent in ['research', 'web_search'],
            "requires_code": intent in ['coding', 'code_review']
        }
        
        self.logger.debug(f"Kế hoạch tạo: {plan}")
        return plan
    
    def _determine_llm_type(self, intent: str) -> str:
        """Xác định loại LLM dựa trên intent"""
        mapping = {
            'chat': 'chat',
            'reasoning': 'reasoning',
            'coding': 'coding',
            'research': 'reasoning',
            'summary': 'lightweight'
        }
        return mapping.get(intent, 'chat')
    
    def _determine_tools(self, intent: str) -> list:
        """Xác định tools cần dùng"""
        mapping = {
            'web_search': ['web_search'],
            'research': ['web_search', 'memory_read'],
            'coding': ['code_executor'],
            'file_read': ['file_reader']
        }
        return mapping.get(intent, [])
    
    def _determine_agent(self, intent: str) -> str:
        """Xác định agent cần gọi"""
        mapping = {
            'planning': 'planner',
            'research': 'research',
            'coding': 'coding',
            'review': 'reviewer',
            'security': 'security'
        }
        return mapping.get(intent, None)