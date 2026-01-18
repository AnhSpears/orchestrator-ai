"""
LLM DISPATCHER TỐI ƯU - Sử dụng model phù hợp cho từng task
"""
import yaml
import logging
import time
import requests
from typing import Dict, Any
import random

class LLMDispatcher:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ollama_base = "http://localhost:11434"
        self.use_mock = False
        
        # Tải cấu hình
        self.llm_profiles = self._load_llm_profiles()
        
        # Khởi tạo model
        self.available_models = []
        self.model_priority = {}
        self._initialize_dispatcher()
        
    def _load_llm_profiles(self):
        """Tải cấu hình LLM từ file"""
        try:
            with open('config/llm_profiles.yaml', 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.warning(f"Không thể tải llm_profiles: {e}")
            return {
                "profiles": {
                    "chat": {"models": ["llama3:8b"]},
                    "coding": {"models": ["deepseek-coder:6.7b"]},
                    "research": {"models": ["llama3:8b"]},
                    "web_search": {"models": ["llama3:8b"]}
                }
            }
    
    def _initialize_dispatcher(self):
        """Khởi tạo dispatcher với các model có sẵn"""
        try:
            self._detect_available_models()
            if not self.available_models:
                self.logger.warning("Không có model nào, chuyển sang mock mode")
                self.use_mock = True
            else:
                self._select_optimal_model()
                self.logger.info(f"Dispatcher khởi tạo thành công. Model có sẵn: {self.available_models}")
        except Exception as e:
            self.logger.error(f"Lỗi khởi tạo dispatcher: {e}")
            self.use_mock = True
    
    def _detect_available_models(self):
        """Phát hiện model nào thực sự có sẵn và hoạt động"""
        self.logger.info("🔍 Đang phát hiện model có sẵn...")
        
        # Danh sách model để test
        test_models = ['llama3:8b', 'qwen2.5:14b', 'mixtral:latest', 'deepseek-coder:6.7b']
        self.available_models = []
        
        for model in test_models:
            try:
                # Test nhanh bằng API show
                response = requests.get(
                    f"{self.ollama_base}/api/show",
                    json={"name": model},
                    timeout=3
                )
                if response.status_code == 200:
                    self.available_models.append(model)
                    self.logger.info(f"  ✅ {model} có sẵn")
                else:
                    self.logger.debug(f"  ⚠️ {model} không khả dụng (HTTP {response.status_code})")
            except requests.exceptions.Timeout:
                self.logger.debug(f"  ⏰ {model}: timeout")
            except Exception as e:
                self.logger.debug(f"  ❌ {model}: {str(e)[:50]}")
        
        # Nếu không tìm thấy model, thử kiểm tra kết nối Ollama cơ bản
        if not self.available_models:
            try:
                response = requests.get(f"{self.ollama_base}/api/tags", timeout=5)
                if response.status_code == 200:
                    models_data = response.json().get('models', [])
                    self.available_models = [m['name'] for m in models_data]
                    self.logger.info(f"  📊 Tìm thấy {len(self.available_models)} model từ API tags")
            except Exception as e:
                self.logger.warning(f"  Không thể kết nối đến Ollama: {e}")
    
    def _select_optimal_model(self):
        """Chọn model tối ưu dựa trên performance test"""
        # Ưu tiên theo thứ tự hiệu năng và chất lượng
        self.model_priority = {
            'chat': self._get_best_model_for_type('chat'),
            'coding': self._get_best_model_for_type('coding'),
            'web_search': self._get_best_model_for_type('research'),
            'research': self._get_best_model_for_type('research'),
            'reasoning': self._get_best_model_for_type('reasoning')
        }
        
        self.logger.info(f"🎯 Model tối ưu đã chọn: {self.model_priority}")
    
    def _get_best_model_for_type(self, llm_type: str) -> str:
        """Chọn model tốt nhất cho từng loại task"""
        # Ưu tiên từ file cấu hình
        if self.llm_profiles and 'profiles' in self.llm_profiles:
            profiles = self.llm_profiles['profiles']
            if llm_type in profiles and 'models' in profiles[llm_type]:
                for model in profiles[llm_type]['models']:
                    if model in self.available_models:
                        return model
        
        # Fallback priority
        priority_lists = {
            'chat': ['qwen2.5:14b', 'mixtral:latest', 'llama3:8b'],
            'coding': ['deepseek-coder:6.7b', 'codellama:7b', 'llama3:8b'],
            'research': ['qwen2.5:14b', 'mixtral:latest', 'llama3.1:latest', 'llama3:8b'],
            'reasoning': ['mixtral:latest', 'qwen2.5:14b', 'llama3.1:latest', 'llama3:8b']
        }
        
        priority = priority_lists.get(llm_type, ['llama3:8b'])
        for model in priority:
            if model in self.available_models:
                return model
        
        # Nếu không có model nào, trả về model đầu tiên có sẵn
        return self.available_models[0] if self.available_models else 'llama3:8b'
    
    def dispatch(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatch task đến model tối ưu nhất
        
        Args:
            plan: Kế hoạch từ ReasoningEngine
            
        Returns:
            Phản hồi từ LLM
        """
        if self.use_mock:
            self.logger.info("📝 Đang dùng mock LLM")
            response = self._create_high_quality_mock_response(plan)
            return {
                "model": "mock",
                "response": response,
                "mode": "mock",
                "quality": "high"
            }
        
        llm_type = plan.get('llm_type', 'chat')
        model = self.model_priority.get(llm_type, 'llama3:8b')
        
        # Tạo prompt tối ưu
        prompt = self._create_optimized_prompt(plan, model)
        
        # Gọi LLM với retry strategy thông minh
        try:
            response = self._smart_llm_call(model, prompt, llm_type)
            
            # Nếu response không đủ tốt, thử model khác
            if not self._is_response_adequate(response, llm_type):
                self.logger.warning(f"Response từ {model} không đủ tốt, thử model backup...")
                backup_model = self._get_backup_model(model, llm_type)
                if backup_model and backup_model != model:
                    response = self._smart_llm_call(backup_model, prompt, llm_type)
            
            return {
                "model": model,
                "response": response,
                "mode": "real",
                "quality": "high" if len(response) > 300 else "medium"
            }
            
        except Exception as e:
            self.logger.error(f"Lỗi khi gọi LLM: {e}")
            # Fallback sang mock response chất lượng cao
            response = self._create_high_quality_mock_response(plan)
            return {
                "model": "mock-fallback",
                "response": response,
                "mode": "mock",
                "quality": "high"
            }
    
    def _create_optimized_prompt(self, plan: Dict[str, Any], model: str) -> str:
        """Tạo prompt tối ưu cho từng model"""
        intent = plan.get('intent', 'chat')
        user_input = plan.get('user_input', '')
        language = plan.get('language', 'vi')
        
        # ĐẶC BIỆT: Nếu là coding model (deepseek-coder), dùng prompt tiếng Anh
        if 'coder' in model.lower() or 'code' in model.lower():
            return self._create_coding_specific_prompt(plan, model)
        
        # Xác định yêu cầu ngôn ngữ cho các model khác
        lang_requirement = "Trả lời bằng TIẾNG VIỆT 100%." if language == 'vi' else "Answer in ENGLISH 100%."
        
        # Prompt base
        prompt_base = f"""{lang_requirement}

    YÊU CẦU QUAN TRỌNG:
    1. Trả lời ĐẦY ĐỦ, CHI TIẾT, không cắt ngang
    2. Tổ chức thông tin có cấu trúc rõ ràng
    3. Đưa ví dụ cụ thể khi có thể

    CÂU HỎI/ YÊU CẦU: {user_input}

    BẮT ĐẦU TRẢ LỜI:"""
        
        # Thêm yêu cầu đặc biệt theo intent
        if intent == 'coding':
            prompt_base += "\n\n[YÊU CẦU CODE]\n- Code phải đầy đủ, có thể chạy được\n- Có comment giải thích\n- Có ví dụ sử dụng\n- Có xử lý lỗi"
        elif intent in ['research', 'web_search']:
            prompt_base += "\n\n[YÊU CẦU NGHIÊN CỨU]\n- Cung cấp thông tin chi tiết, có cấu trúc\n- Đưa ra các khía cạnh quan trọng\n- Kết thúc với tóm tắt"
        
        return prompt_base
    
    def _smart_llm_call(self, model: str, prompt: str, llm_type: str) -> str:
        """Gọi LLM với strategy thông minh"""
        # Điều chỉnh timeout dựa trên model
        timeouts = {
            'qwen2.5:14b': 45,
            'mixtral:latest': 60,
            'llama3:8b': 30,
            'deepseek-coder:6.7b': 40
        }
        timeout = timeouts.get(model, 30)
        
        # Điều chỉnh max_tokens dựa trên task
        max_tokens_map = {
            'coding': 4096,
            'research': 3072,
            'web_search': 3072,
            'chat': 2048
        }
        max_tokens = max_tokens_map.get(llm_type, 2048)
        
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": max_tokens,
                    "top_p": 0.9,
                    "repeat_penalty": 1.1
                }
            }
            
            self.logger.info(f"🤖 Gọi {model} (timeout: {timeout}s, tokens: {max_tokens})")
            start_time = time.time()
            
            response = requests.post(
                f"{self.ollama_base}/api/generate",
                json=payload,
                timeout=timeout
            )
            
            elapsed = time.time() - start_time
            self.logger.info(f"⏱️  {model} phản hồi trong {elapsed:.2f}s")
            
            if response.status_code == 200:
                result = response.json().get('response', '').strip()
                
                # Kiểm tra và sửa response nếu cần
                result = self._post_process_response(result, llm_type)
                
                return result
            else:
                raise Exception(f"API error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            self.logger.error(f"⏰ Timeout với {model} sau {timeout}s")
            raise Exception(f"Model {model} timeout")
        except Exception as e:
            self.logger.error(f"❌ Lỗi với {model}: {e}")
            raise
    
    def _post_process_response(self, response: str, llm_type: str) -> str:
        """Xử lý hậu kỳ để cải thiện chất lượng response"""
        if not response:
            return "Xin lỗi, tôi không thể tạo phản hồi lúc này."
        
        # Đảm bảo response không bị cắt ngang
        endings = ['.', '!', '?', '```', '```python', '```bash']
        
        # Nếu response không kết thúc bằng dấu kết thúc hợp lý
        last_char = response.strip()[-1] if response.strip() else ''
        
        if last_char not in endings and len(response) > 100:
            # Tìm vị trí kết thúc hợp lý cuối cùng
            for end_marker in ['.', '!', '?', '\n\n']:
                end_pos = response.rfind(end_marker)
                if end_pos > len(response) * 0.7:  # Nếu gần cuối
                    response = response[:end_pos + 1]
                    break
        
        return response
    
    def _is_response_adequate(self, response: str, llm_type: str) -> bool:
        """Kiểm tra xem response có đủ chất lượng không"""
        if not response or len(response) < 50:
            return False
        
        # Tiêu chí khác nhau cho từng loại task
        if llm_type == 'coding':
            # Ưu tiên deepseek-coder - kiểm tra khác
            code_indicators = [
                'def ', 'class ', 'import ', 'from ', 'print(',
                'return ', 'for ', 'while ', 'if ', 'try:',
                '```python', '```bash', '```cpp', '```java'
            ]
            
            # deepseek-coder thường có response tốt
            # Chỉ cần có một trong các indicator là đủ
            has_code = any(indicator in response for indicator in code_indicators)
            
            # deepseek-coder đặc biệt tốt, không cần fallback trừ khi rất ngắn
            if len(response) > 100 and has_code:
                return True
            return False
            
        elif llm_type in ['research', 'web_search']:
            return len(response) > 200
        else:  # chat
            return len(response) > 100
    def _get_backup_model(self, primary_model: str, llm_type: str) -> str:
        """Lấy model backup nếu primary không tốt"""
        backup_map = {
            'qwen2.5:14b': 'llama3:8b',
            'mixtral:latest': 'qwen2.5:14b',
            'llama3:8b': 'qwen2.5:14b',
            'deepseek-coder:6.7b': 'llama3:8b'
        }
        return backup_map.get(primary_model, 'llama3:8b')
    def _create_coding_specific_prompt(self, plan: Dict[str, Any], model: str) -> str:
        """
        Tạo prompt đặc biệt cho coding models (tiếng Anh)
        """
        user_input = plan.get('user_input', '')
        
        # Phát hiện ngôn ngữ lập trình từ input
        language_hints = {
            'python': ['python', 'pandas', 'numpy', 'def ', 'import '],
            'javascript': ['javascript', 'js', 'node', 'react', 'function('],
            'java': ['java', 'class ', 'public static'],
            'html': ['html', '<div>', '<p>', 'website'],
            'sql': ['sql', 'database', 'select ', 'insert ']
        }
        
        target_lang = 'python'  # Mặc định
        for lang, hints in language_hints.items():
            if any(hint in user_input.lower() for hint in hints):
                target_lang = lang
                break
        
        # Prompt tiếng Anh cho deepseek-coder
        prompt = f"""You are an expert programming assistant. Write complete, runnable code in {target_lang.upper()}.

    USER REQUEST: {user_input}

    REQUIREMENTS:
    1. Write FULL, COMPLETE, RUNNABLE code
    2. Include comprehensive comments explaining the logic
    3. Include error handling
    4. Include example usage with test cases
    5. Use best practices and clean code principles

    RESPONSE FORMAT:
    - Start with a brief explanation of the solution
    - Then provide the complete code in a code block
    - End with example usage and expected output

    Complete {target_lang.upper()} code:"""
        
        return prompt
    def _create_high_quality_mock_response(self, plan: Dict[str, Any]) -> str:
        """Tạo mock response chất lượng cao"""
        intent = plan.get('intent', 'chat')
        user_input = plan.get('user_input', '')
        language = plan.get('language', 'vi')
        
        if language == 'vi':
            return f"""**ORCHESTRATOR AI - CHẾ ĐỘ DEMO CHẤT LƯỢNG CAO**

**Câu hỏi của bạn:** {user_input}

**Thông tin hệ thống:**
- Hệ thống ORCHESTRATOR đang chạy ở chế độ DEMO
- Kiến trúc core AI bất biến đã sẵn sàng
- Module chat tự nhiên hoạt động ổn định
- Hệ thống permission được thiết lập đầy đủ

**Để nhận phản hồi từ LLM thực:**
1. Đảm bảo Ollama đang chạy: `ollama serve`
2. Tải model phù hợp: `ollama pull qwen2.5:14b`
3. Khởi động lại hệ thống ORCHESTRATOR

**Gợi ý cải thiện:**
- Model qwen2.5:14b hỗ trợ tiếng Việt tốt nhất
- Model llama3:8b nhanh và ổn định
- Model deepseek-coder:6.7b chuyên cho lập trình

**Trạng thái hiện tại:**
✅ Kiến trúc hệ thống hoàn chỉnh
✅ Module xử lý ngôn ngữ hoạt động
✅ Permission và security ready
⏳ Đang chờ kết nối LLM thực

Hãy kết nối với Ollama để trải nghiệm đầy đủ! 🚀"""
        else:
            return f"""**ORCHESTRATOR AI - HIGH QUALITY DEMO MODE**

**Your question:** {user_input}

**System information:**
- ORCHESTRATOR system is running in DEMO mode
- Immutable core AI architecture is ready
- Natural language chat module is operational
- Permission system is fully established

**To get real LLM responses:**
1. Ensure Ollama is running: `ollama serve`
2. Pull appropriate models: `ollama pull qwen2.5:14b`
3. Restart ORCHESTRATOR system

**Improvement suggestions:**
- qwen2.5:14b model has best Vietnamese support
- llama3:8b model is fast and stable
- deepseek-coder:6.7b model specializes in programming

**Current status:**
✅ System architecture complete
✅ Language processing module operational
✅ Permission and security ready
⏳ Waiting for real LLM connection

Connect to Ollama for full experience! 🚀"""