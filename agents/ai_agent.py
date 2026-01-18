"""
AI AGENT - Agent thông minh tổng hợp với khả năng học tập
"""
import os
import sys
import json
import yaml
import logging
import tempfile
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

# Thêm đường dẫn
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.memory_system import MemorySystem

class AIAgent:
    """AI Agent với khả năng học tập và tự cải thiện"""
    
    def __init__(self, config_path: str = "config/permissions.yaml"):
        self.logger = logging.getLogger(__name__)
        self.memory = MemorySystem()
        self.config = self._load_config(config_path)
        self.learning_history = []
        
        # Khởi tạo các module con
        self._init_sub_agents()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Tải cấu hình agent"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.warning(f"Không thể tải config: {e}")
            return {
                "ai_agent": {
                    "enabled": True,
                    "learning_enabled": True,
                    "max_learning_items": 100
                }
            }
    
    def _init_sub_agents(self):
        """Khởi tạo các sub-agent (virtual)"""
        self.sub_agents = {
            "planner": self._planning_agent,
            "researcher": self._research_agent,
            "coder": self._coding_agent,
            "reviewer": self._review_agent,
            "security": self._security_agent,
            "learner": self._learning_agent
        }
        
        self.logger.info("AI Agent đã khởi tạo với 6 sub-agent")
    
    def process(self, task: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Xử lý task với AI Agent
        
        Args:
            task: Task từ orchestrator
            context: Ngữ cảnh bổ sung
            
        Returns:
            Kết quả xử lý
        """
        try:
            self.logger.info(f"AI Agent nhận task: {task.get('intent', 'unknown')}")
            
            # Lưu vào short-term memory
            if context:
                session_id = context.get('session_id', 'default')
                self.memory.save_short_term(session_id, {
                    "task": task,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Xác định loại xử lý
            intent = task.get('intent', 'general')
            handler = self._get_handler(intent)
            
            # Xử lý
            result = handler(task, context)
            
            # Lưu vào learning history
            self._add_to_learning_history(task, result)
            
            return {
                "status": "success",
                "result": result,
                "agent": "ai_agent",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Lỗi trong AI Agent: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agent": "ai_agent"
            }
    
    def _get_handler(self, intent: str):
        """Lấy handler cho từng intent"""
        handlers = {
            'planning': self._planning_agent,
            'research': self._research_agent,
            'coding': self._coding_agent,
            'review': self._review_agent,
            'security': self._security_agent,
            'learning': self._learning_agent,
            'memory': self._memory_agent,
            'document': self._document_agent
        }
        return handlers.get(intent, self._general_agent)
    
    def _general_agent(self, task: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Agent tổng quát"""
        user_input = task.get('user_input', '')
        
        # Kiểm tra nếu cần phân phối đến sub-agent
        if 'kế hoạch' in user_input or 'plan' in user_input:
            return self._planning_agent(task, context)
        elif 'nghiên cứu' in user_input or 'research' in user_input:
            return self._research_agent(task, context)
        elif 'code' in user_input or 'mã' in user_input or 'lập trình' in user_input:
            return self._coding_agent(task, context)
        elif 'học' in user_input or 'learn' in user_input:
            return self._learning_agent(task, context)
        else:
            # Xử lý chung
            return {
                "response": f"AI Agent đã xử lý: {user_input}",
                "action": "processed",
                "recommendation": "Sử dụng sub-agent chuyên biệt cho kết quả tốt hơn"
            }
    
    def _planning_agent(self, task: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Agent lập kế hoạch"""
        user_input = task.get('user_input', '')
        
        # Truy xuất memory liên quan
        related_memories = self.memory.retrieve_long_term(keyword=user_input[:20])
        
        plan = {
            "goal": user_input,
            "steps": [
                "1. Phân tích yêu cầu và xác định mục tiêu",
                "2. Thu thập thông tin và tài nguyên cần thiết",
                "3. Thiết kế giải pháp và lập kế hoạch chi tiết",
                "4. Triển khai và thực hiện",
                "5. Kiểm tra và đánh giá kết quả",
                "6. Điều chỉnh và cải tiến"
            ],
            "estimated_time": "Tùy thuộc vào độ phức tạp",
            "resources_needed": ["Thông tin đầu vào", "Công cụ hỗ trợ", "Nhân lực (nếu cần)"],
            "related_memories": len(related_memories)
        }
        
        # Lưu vào long-term memory
        self.memory.save_long_term(
            key=f"plan_{hash(user_input)}",
            data=plan,
            category="planning"
        )
        
        return {
            "response": f"Đã tạo kế hoạch cho: {user_input}",
            "plan": plan,
            "agent": "planner"
        }
    
    def _research_agent(self, task: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Agent nghiên cứu"""
        user_input = task.get('user_input', '')
        
        # Tìm trong documents
        documents = self.memory.search_documents(user_input, max_results=3)
        
        # Tìm trong memory
        memories = self.memory.retrieve_long_term(keyword=user_input)
        
        research_result = {
            "topic": user_input,
            "documents_found": len(documents),
            "memories_found": len(memories),
            "sources": [doc.get('metadata', {}).get('source', 'unknown') for doc in documents],
            "key_points": [
                "Thông tin từ bộ nhớ hệ thống",
                "Tài liệu đã học",
                "Kiến thức tổng hợp"
            ],
            "recommendations": [
                "Thu thập thêm tài liệu liên quan",
                "Phân tích sâu hơn với chuyên gia domain",
                "Thử nghiệm thực tế nếu có thể"
            ]
        }
        
        return {
            "response": f"Kết quả nghiên cứu về: {user_input}",
            "research": research_result,
            "documents_preview": [{"id": d["id"][:8], "source": d.get("metadata", {}).get("source", "unknown")} 
                                for d in documents[:2]],
            "agent": "researcher"
        }
    
    def _coding_agent(self, task: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Agent lập trình với học tập"""
        user_input = task.get('user_input', '')
        language = task.get('language', 'vi')
        
        # Tìm code patterns trong memory
        code_patterns = self.memory.retrieve_long_term(category="coding")
        
        # Tạo code với learning
        code_result = self._generate_code_with_learning(user_input, language, code_patterns)
        
        return {
            "response": f"Đã tạo code cho: {user_input}",
            "code": code_result.get("code"),
            "explanation": code_result.get("explanation"),
            "learned_patterns": code_result.get("learned_patterns", 0),
            "agent": "coder"
        }
    
    def _generate_code_with_learning(self, requirement: str, language: str, 
                                    existing_patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Tạo code với khả năng học từ patterns"""
        
        # Đơn giản hóa: Tạo code mẫu cơ bản
        if "đọc file" in requirement.lower() or "read file" in requirement.lower():
            code = '''import os

def read_file(file_path):
    """Đọc nội dung file"""
    try:
        if not os.path.exists(file_path):
            return {"error": "File không tồn tại"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "success": True,
            "content": content,
            "file_size": len(content)
        }
    except Exception as e:
        return {"error": str(e)}

# Sử dụng
result = read_file("example.txt")
if result.get("success"):
    print(f"Nội dung file: {result['content'][:100]}...")
else:
    print(f"Lỗi: {result['error']}")'''
            
            explanation = "Code đọc file với xử lý lỗi và kiểm tra tồn tại"
            
        elif "csv" in requirement.lower():
            code = '''import csv
import statistics

def read_csv_and_calculate(csv_file, column_index=0):
    """Đọc file CSV và tính toán"""
    data = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)  # Đọc header
            
            for row in reader:
                if row:  # Bỏ qua dòng trống
                    try:
                        value = float(row[column_index])
                        data.append(value)
                    except ValueError:
                        continue
        
        if data:
            return {
                "average": statistics.mean(data),
                "min": min(data),
                "max": max(data),
                "count": len(data)
            }
        else:
            return {"error": "Không có dữ liệu hợp lệ"}
            
    except Exception as e:
        return {"error": str(e)}

# Ví dụ sử dụng
result = read_csv_and_calculate("data.csv")
print(f"Kết quả: {result}")'''
            
            explanation = "Code đọc CSV và tính toán thống kê cơ bản"
            
        else:
            code = '''def process_data(data):
    """Hàm xử lý dữ liệu tổng quát"""
    # TODO: Triển khai logic xử lý cụ thể
    if isinstance(data, list):
        return {
            "type": "list",
            "length": len(data),
            "processed": [str(item) for item in data[:5]]
        }
    elif isinstance(data, dict):
        return {
            "type": "dict",
            "keys": list(data.keys()),
            "values": list(data.values())[:5]
        }
    else:
        return {"type": "other", "value": str(data)[:100]}

# Ví dụ
print(process_data([1, 2, 3, 4, 5]))'''
            
            explanation = "Code template xử lý dữ liệu tổng quát"
        
        # Lưu pattern vào memory
        pattern_key = f"code_pattern_{hash(requirement)}"
        self.memory.save_long_term(
            key=pattern_key,
            data={
                "requirement": requirement,
                "code": code,
                "language": "python",
                "category": "coding"
            },
            category="coding"
        )
        
        return {
            "code": code,
            "explanation": explanation,
            "learned_patterns": len(existing_patterns) + 1
        }
    
    def _review_agent(self, task: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Agent đánh giá chất lượng"""
        content = task.get('content', '')
        
        review_criteria = {
            "completeness": 0.8,
            "accuracy": 0.7,
            "clarity": 0.9,
            "usefulness": 0.8,
            "innovation": 0.6
        }
        
        suggestions = [
            "Có thể thêm ví dụ cụ thể hơn",
            "Kiểm tra lại tính chính xác của thông tin",
            "Cấu trúc lại cho logic hơn"
        ]
        
        return {
            "response": f"Đã đánh giá nội dung ({len(content)} ký tự)",
            "review": review_criteria,
            "score": sum(review_criteria.values()) / len(review_criteria),
            "suggestions": suggestions,
            "agent": "reviewer"
        }
    
    def _security_agent(self, task: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Agent bảo mật"""
        content = task.get('content', '')
        
        # Kiểm tra bảo mật cơ bản
        security_checks = {
            "has_sensitive_info": False,
            "has_code_injection": False,
            "has_external_calls": False,
            "has_file_operations": "read" in content.lower()
        }
        
        warnings = []
        if "password" in content.lower() or "secret" in content.lower():
            security_checks["has_sensitive_info"] = True
            warnings.append("Phát hiện thông tin nhạy cảm")
        
        if "eval(" in content or "exec(" in content:
            security_checks["has_code_injection"] = True
            warnings.append("Phát hiện code injection risk")
        
        recommendations = [
            "Xóa thông tin nhạy cảm trước khi lưu trữ",
            "Sử dụng parameterized queries cho database",
            "Validate input kỹ lưỡng"
        ]
        
        return {
            "response": "Kiểm tra bảo mật hoàn tất",
            "security_check": security_checks,
            "warnings": warnings,
            "recommendations": recommendations,
            "agent": "security"
        }
    
    def _learning_agent(self, task: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Agent học tập từ tài liệu và code"""
        user_input = task.get('user_input', '')
        content = task.get('content', '')
        
        # Phân tích loại học tập
        if 'tài liệu' in user_input or 'document' in user_input:
            return self._learn_from_document(content)
        elif 'code' in user_input or 'mã' in user_input:
            return self._learn_from_code(content)
        else:
            return self._learn_general(content)
    
    def _learn_from_document(self, content: str) -> Dict[str, Any]:
        """Học từ tài liệu"""
        # Lưu tài liệu
        save_result = self.memory.save_document(
            content=content,
            metadata={
                "type": "learning_material",
                "source": "user_input",
                "learned_at": datetime.now().isoformat()
            }
        )
        
        # Trích xuất key points
        lines = content.split('\n')
        key_points = []
        for line in lines[:10]:  # Lấy 10 dòng đầu
            line_stripped = line.strip()
            if len(line_stripped) > 20 and len(line_stripped) < 200:
                key_points.append(line_stripped)
        
        return {
            "response": f"Đã học từ tài liệu: {save_result}",
            "key_points": key_points[:5],  # Giới hạn 5 điểm
            "document_size": len(content),
            "learned_items": len(key_points),
            "agent": "learner"
        }
    
    def _learn_from_code(self, code: str) -> Dict[str, Any]:
        """Học từ code"""
        # Phân tích code cơ bản
        lines = code.split('\n')
        functions = [line for line in lines if 'def ' in line]
        imports = [line for line in lines if 'import ' in line or 'from ' in line]
        
        # Lưu pattern
        pattern_key = f"learned_code_{hash(code)}"
        self.memory.save_long_term(
            key=pattern_key,
            data={
                "code": code,
                "functions": functions,
                "imports": imports,
                "line_count": len(lines),
                "learned_at": datetime.now().isoformat()
            },
            category="coding"
        )
        
        # Tạo summary
        patterns_identified = []
        if 'def ' in code:
            patterns_identified.append("function_definition")
        if 'class ' in code:
            patterns_identified.append("class_definition")
        if 'try:' in code:
            patterns_identified.append("error_handling")
        if 'import ' in code:
            patterns_identified.append("module_import")
        
        return {
            "response": f"Đã học từ code ({len(lines)} dòng, {len(functions)} hàm)",
            "patterns_identified": patterns_identified,
            "functions_learned": [f.split('def ')[1].split('(')[0] for f in functions[:3]],
            "agent": "learner"
        }
    
    def _learn_general(self, content: str) -> Dict[str, Any]:
        """Học tổng quát"""
        # Lưu vào knowledge base
        knowledge_key = f"knowledge_{hash(content)}"
        self.memory.save_long_term(
            key=knowledge_key,
            data={
                "content": content,
                "type": "general_knowledge",
                "learned_at": datetime.now().isoformat()
            },
            category="knowledge"
        )
        
        return {
            "response": f"Đã lưu kiến thức vào bộ nhớ (ID: {knowledge_key[:8]})",
            "content_preview": content[:100] + "..." if len(content) > 100 else content,
            "agent": "learner"
        }
    
    def _memory_agent(self, task: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Agent quản lý bộ nhớ"""
        action = task.get('action', 'query')
        query = task.get('query', '')
        
        if action == 'query':
            results = self.memory.search_documents(query, max_results=5)
            memories = self.memory.retrieve_long_term(keyword=query)
            
            return {
                "response": f"Tìm thấy {len(results)} tài liệu và {len(memories)} ký ức",
                "documents": [{"id": r["id"][:8], "preview": r["content"][:50]} for r in results[:3]],
                "memories": [{"key": m["key"][:20], "category": m.get("category", "unknown")} 
                           for m in memories[:3]],
                "agent": "memory"
            }
        
        elif action == 'stats':
            # Lấy thống kê
            try:
                index_file = self.memory.base_path / "memory_index.json"
                if index_file.exists():
                    with open(index_file, 'r', encoding='utf-8') as f:
                        stats = json.load(f)
                else:
                    stats = {"error": "Không tìm thấy index"}
                
                return {
                    "response": "Thống kê bộ nhớ hệ thống",
                    "stats": stats,
                    "agent": "memory"
                }
            except Exception as e:
                return {
                    "response": f"Lỗi lấy thống kê: {e}",
                    "agent": "memory"
                }
        
        else:
            return {
                "response": f"Hành động '{action}' không được hỗ trợ",
                "supported_actions": ["query", "stats"],
                "agent": "memory"
            }
    
    def _document_agent(self, task: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Agent xử lý tài liệu"""
        action = task.get('action', 'ingest')
        content = task.get('content', '')
        
        if action == 'ingest':
            if not content:
                return {
                    "response": "Không có nội dung để học",
                    "agent": "document"
                }
            
            # Lưu tài liệu
            result = self.memory.save_document(
                content=content,
                metadata={
                    "source": "document_agent",
                    "ingested_at": datetime.now().isoformat(),
                    "agent": "ai_agent"
                }
            )
            
            # Phân tích tài liệu
            word_count = len(content.split())
            line_count = len(content.split('\n'))
            
            return {
                "response": f"Đã học tài liệu: {result}",
                "analysis": {
                    "word_count": word_count,
                    "line_count": line_count,
                    "estimated_reading_time": f"{word_count/200:.1f} phút"
                },
                "agent": "document"
            }
        
        else:
            return {
                "response": f"Hành động '{action}' không được hỗ trợ",
                "agent": "document"
            }
    
    def _add_to_learning_history(self, task: Dict[str, Any], result: Dict[str, Any]):
        """Thêm vào lịch sử học tập"""
        history_entry = {
            "task": task.get('intent', 'unknown'),
            "timestamp": datetime.now().isoformat(),
            "result_status": result.get("status", "unknown"),
            "agent_used": result.get("agent", "unknown")
        }
        
        self.learning_history.append(history_entry)
        
        # Giới hạn lịch sử
        if len(self.learning_history) > 100:
            self.learning_history = self.learning_history[-100:]
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Lấy summary học tập"""
        if not self.learning_history:
            return {"message": "Chưa có lịch sử học tập"}
        
        # Thống kê
        intents = [h["task"] for h in self.learning_history]
        agents = [h["agent_used"] for h in self.learning_history]
        
        from collections import Counter
        intent_counts = Counter(intents)
        agent_counts = Counter(agents)
        
        return {
            "total_learning_sessions": len(self.learning_history),
            "most_common_intent": intent_counts.most_common(1)[0] if intent_counts else None,
            "agent_usage": dict(agent_counts),
            "first_learning": self.learning_history[0]["timestamp"] if self.learning_history else None,
            "last_learning": self.learning_history[-1]["timestamp"] if self.learning_history else None
        }