"""
LLM DISPATCHER - Điều phối LLM
Quyết định gọi LLM nào, với prompt nào
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
        self.load_llm_profiles()
        self.ollama_base = "http://localhost:11434"
        self.use_mock = False
        self._check_ollama_connection()
        
    def _check_ollama_connection(self):
        """Kiểm tra kết nối Ollama khi khởi động"""
        try:
            response = requests.get(f"{self.ollama_base}/api/tags", timeout=5)
            if response.status_code == 200:
                self.logger.info("✅ Kết nối đến Ollama thành công!")
                self.use_mock = False
            else:
                self.logger.warning("⚠️ Ollama trả về lỗi, dùng mock mode")
                self.use_mock = True
        except Exception as e:
            self.logger.warning(f"⚠️ Không thể kết nối đến Ollama: {e}")
            self.logger.warning("🔧 Chuyển sang chế độ mock (không cần Ollama)")
            self.use_mock = True
    
    def load_llm_profiles(self):
        """Tải cấu hình LLM"""
        try:
            with open('config/llm_profiles.yaml', 'r') as f:
                self.llm_profiles = yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Không thể tải llm_profiles: {e}")
            self.llm_profiles = {}
    
    def dispatch(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatch task đến LLM phù hợp
        
        Args:
            plan: Kế hoạch từ ReasoningEngine
            
        Returns:
            Phản hồi từ LLM
        """
        llm_type = plan.get('llm_type', 'chat')
        model = self._select_model(llm_type)
        
        # Tạo prompt phù hợp
        prompt = self._create_detailed_prompt(plan)
        
        # Gọi LLM hoặc dùng mock
        if self.use_mock:
            self.logger.info("📝 Đang dùng mock LLM (không cần kết nối mạng)")
            response = self._mock_llm_call(plan)
        else:
            try:
                response = self._call_llm_with_retry(model, prompt, llm_type)
            except Exception as e:
                self.logger.error(f"Lỗi khi gọi LLM: {e}")
                response = self._mock_llm_call(plan)
        
        return {
            "model": model,
            "response": response,
            "prompt_length": len(prompt),
            "mode": "mock" if self.use_mock else "real"
        }
    
    def _select_model(self, llm_type: str) -> str:
        """Chọn model dựa trên loại task"""
        profiles = self.llm_profiles.get('profiles', {})
        if llm_type in profiles:
            models = profiles[llm_type].get('models', [])
            if models:
                return models[0]  # Lấy model đầu tiên
        
        # Fallback models
        fallbacks = {
            'chat': 'llama3:8b',
            'reasoning': 'mixtral:latest',
            'coding': 'deepseek-coder:6.7b'
        }
        return fallbacks.get(llm_type, 'llama3:8b')
    
    def _create_detailed_prompt(self, plan: Dict[str, Any]) -> str:
        """Tạo prompt chi tiết và cấu trúc cho task"""
        intent = plan.get('intent', 'chat')
        user_input = plan.get('user_input', '')
        language = plan.get('language', 'vi')
        
        # System prompts chi tiết cho từng loại task
        system_prompts = {
            'chat': {
                'vi': """Bạn là ORCHESTRATOR AI - trợ lý thông minh, chuyên nghiệp. 
Hãy trả lời đầy đủ, chi tiết và hữu ích. 
Ưu tiên cung cấp thông tin có giá trị, không chỉ trả lời ngắn gọn.
Luôn giữ thái độ thân thiện, nhiệt tình.""",
                'en': """You are ORCHESTRATOR AI - an intelligent, professional assistant.
Provide complete, detailed, and helpful responses.
Prioritize giving valuable information, not just brief answers.
Always maintain a friendly and enthusiastic attitude."""
            },
            'web_search': {
                'vi': """Bạn là công cụ tìm kiếm thông minh. Hãy cung cấp thông tin chi tiết, có cấu trúc:
1. Tổng quan về chủ đề
2. Các điểm chính quan trọng
3. Ứng dụng thực tế
4. Xu hướng hiện tại
5. Tài liệu tham khảo (nếu có)

Thông tin phải chính xác, có tổ chức và dễ hiểu.""",
                'en': """You are an intelligent search tool. Provide detailed, structured information:
1. Topic overview
2. Key important points
3. Practical applications
4. Current trends
5. References (if available)

Information must be accurate, organized, and easy to understand."""
            },
            'coding': {
                'vi': """Bạn là lập trình viên chuyên nghiệp. Hãy viết code đầy đủ với:
1. Code hoàn chỉnh, có thể chạy được
2. Comment giải thích rõ ràng
3. Ví dụ sử dụng cụ thể
4. Giải thích logic và thuật toán
5. Xử lý các trường hợp đặc biệt

Luôn ưu tiên code rõ ràng, hiệu quả và dễ bảo trì.""",
                'en': """You are a professional programmer. Write complete code with:
1. Complete, runnable code
2. Clear explanatory comments
3. Specific usage examples
4. Explanation of logic and algorithms
5. Handling of special cases

Always prioritize clear, efficient, and maintainable code."""
            },
            'research': {
                'vi': """Bạn là nhà nghiên cứu chuyên nghiệp. Cung cấp nghiên cứu chi tiết:
1. Giới thiệu và bối cảnh
2. Phương pháp nghiên cứu
3. Phân tích chi tiết
4. Kết quả và phát hiện
5. Kết luận và đề xuất
6. Hướng nghiên cứu tương lai

Thông tin phải sâu sắc, có căn cứ và hữu ích.""",
                'en': """You are a professional researcher. Provide detailed research:
1. Introduction and context
2. Research methodology
3. Detailed analysis
4. Results and findings
5. Conclusions and recommendations
6. Future research directions

Information must be insightful, evidence-based, and useful."""
            }
        }
        
        # Lấy prompt phù hợp với ngôn ngữ
        prompt_template = system_prompts.get(intent, system_prompts['chat'])
        system = prompt_template.get(language, prompt_template['vi'])
        def _create_forceful_prompt(self, plan: Dict[str, Any]) -> str:
            """Tạo prompt với yêu cầu cực mạnh để kiểm soát response"""
            intent = plan.get('intent', 'chat')
            user_input = plan.get('user_input', '')
            language = plan.get('language', 'vi')
            
            # YÊU CẦU CỰC MẠNH VỀ NGÔN NGỮ
            if language == 'vi':
                lang_force = """
    === QUY ĐỊNH NGÔN NGỮ BẮT BUỘC ===
    1. PHẢI trả lời 100% bằng TIẾNG VIỆT
    2. KHÔNG ĐƯỢC chuyển sang tiếng Anh bất kỳ lúc nào
    3. KHÔNG ĐƯỢC pha trộn ngôn ngữ
    4. Nếu từ chuyên ngành không có tiếng Việt, giải thích bằng tiếng Việt
    """
            else:
                lang_force = """
    === MANDATORY LANGUAGE RULES ===
    1. MUST answer 100% in ENGLISH
    2. DO NOT switch to any other language
    3. DO NOT mix languages
    4. If technical terms don't exist in English, explain in English
    """
            
            # YÊU CẦU VỀ ĐỘ DÀI
            length_requirements = """
    === YÊU CẦU ĐỘ DÀI BẮT BUỘC ===
    1. Câu trả lời PHẢI có ít nhất 500 từ
    2. PHẢI triển khai đầy đủ các ý
    3. KHÔNG ĐƯỢC cắt ngắn, bỏ dở
    4. Nếu chưa xong, tiếp tục viết cho đến khi hoàn chỉnh
    """
            
            # Prompt template cho từng intent
            templates = {
                'chat': f"""
    ### VAI TRÒ:
    Bạn là ORCHESTRATOR AI - trợ lý thông minh, chuyên nghiệp người Việt.

    ### QUY TẮC BẮT BUỘC:
    {lang_force}
    {length_requirements}

    ### YÊU CẦU CỤ THỂ:
    1. Trả lời CHI TIẾT, ĐẦY ĐỦ
    2. Tổ chức thông tin có cấu trúc rõ ràng
    3. Đưa ví dụ cụ thể khi có thể
    4. Kết thúc với phần tóm tắt

    ### CÂU HỎI: {user_input}

    ### TRẢ LỜI (BẮT BUỘC DÀI, CHI TIẾT, BẰNG TIẾNG VIỆT):
    """,
                'coding': f"""
    ### VAI TRÒ:
    Bạn là lập trình viên chuyên nghiệp.

    ### QUY TẮC BẮT BUỘC:
    {lang_force}
    {length_requirements}

    ### YÊU CẦU CODE:
    1. Code PHẢI đầy đủ, có thể chạy được
    2. Có comment giải thích từng phần
    3. Có ví dụ sử dụng cụ thể
    4. Có xử lý lỗi đầy đủ
    5. Có test cases

    ### YÊU CẦU: {user_input}

    ### CODE HOÀN CHỈNH (BẮT BUỘC ĐẦY ĐỦ):
    """,
                'web_search': f"""
    ### VAI TRÒ:
    Bạn là công cụ tìm kiếm thông tin chuyên sâu.

    ### QUY TẮC BẮT BUỘC:
    {lang_force}
    {length_requirements}

    ### CẤU TRÚC THÔNG TIN BẮT BUỘC:
    1. GIỚI THIỆU: Khái niệm cơ bản
    2. LỊCH SỬ: Quá trình phát triển
    3. ỨNG DỤNG: Các ứng dụng thực tế
    4. XU HƯỚNG: Phát triển hiện tại
    5. THÁCH THỨC: Vấn đề cần giải quyết
    6. TÀI NGUYÊN: Nguồn tham khảo
    7. KẾT LUẬN: Tóm tắt và đánh giá

    ### CHỦ ĐỀ: {user_input}

    ### THÔNG TIN CHI TIẾT (BẮT BUỘC ĐẦY ĐỦ):
    """
            }
            
            return templates.get(intent, templates['chat'])
        # Tạo prompt chi tiết dựa trên intent
        if intent == 'coding':
            return f"""### System Prompt (Hệ thống lập trình)
{system}

### Yêu cầu từ người dùng:
{user_input}

### Yêu cầu chi tiết:
1. **Phân tích yêu cầu**: Hiểu rõ vấn đề cần giải quyết
2. **Thiết kế giải pháp**: Mô tả cách tiếp cận
3. **Triển khai code**: Viết code đầy đủ
4. **Giải thích code**: Comment và giải thích logic
5. **Ví dụ sử dụng**: Show how to use the code
6. **Kiểm thử**: Các test case quan trọng

### Code và giải thích:"""
        
        elif intent == 'web_search':
            return f"""### System Prompt (Công cụ tìm kiếm)
{system}

### Chủ đề tìm kiếm:
{user_input}

### Yêu cầu tìm kiếm chi tiết:
Hãy cung cấp thông tin toàn diện về chủ đề này. Bao gồm:

1. **Tổng quan**: Khái niệm cơ bản, định nghĩa
2. **Lịch sử phát triển**: Quá trình hình thành và phát triển
3. **Ứng dụng thực tế**: Các ứng dụng trong đời sống, công nghiệp
4. **Xu hướng hiện tại**: Các phát triển mới nhất
5. **Thách thức và cơ hội**: Những vấn đề và triển vọng
6. **Tài nguyên học tập**: Các nguồn tham khảo uy tín

### Thông tin chi tiết:"""
        
        elif intent == 'research':
            return f"""### System Prompt (Nhà nghiên cứu)
{system}

### Đề tài nghiên cứu:
{user_input}

### Phương pháp nghiên cứu:
1. **Xác định vấn đề**: Làm rõ phạm vi và mục tiêu nghiên cứu
2. **Thu thập dữ liệu**: Các nguồn thông tin và phương pháp thu thập
3. **Phân tích dữ liệu**: Cách thức xử lý và phân tích thông tin
4. **Tổng hợp kết quả**: Các phát hiện và kết luận
5. **Đề xuất ứng dụng**: Ứng dụng thực tế của nghiên cứu

### Báo cáo nghiên cứu chi tiết:"""
        
        else:  # chat
            return f"""### System Prompt (Trợ lý AI)
{system}

### Tin nhắn từ người dùng:
{user_input}

### Yêu cầu trả lời:
Hãy trả lời đầy đủ, chi tiết và hữu ích. Cấu trúc phản hồi nên bao gồm:

1. **Lời chào thân thiện**: Mở đầu tích cực
2. **Nội dung chính**: Thông tin chi tiết, được tổ chức rõ ràng
3. **Ví dụ minh họa**: Các ví dụ cụ thể nếu có
4. **Lời khuyên hữu ích**: Các gợi ý thực tế
5. **Kết luận**: Tóm tắt và đề xuất tiếp theo

### Phản hồi của bạn:"""
    
    def _call_llm_with_retry(self, model: str, prompt: str, llm_type: str) -> str:
        """Gọi LLM với retry và timeout linh hoạt"""
        max_retries = 3
        timeout = 120 if llm_type == 'research' else 60
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Gọi LLM lần {attempt + 1}: {model}")
                
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 4096  # Tăng độ dài response
                    }
                }
                
                response = requests.post(
                    f"{self.ollama_base}/api/generate",
                    json=payload,
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    result = response.json().get('response', '')
                    if len(result) < 100:  # Nếu response quá ngắn
                        self.logger.warning(f"Response quá ngắn ({len(result)} ký tự)")
                        if attempt < max_retries - 1:
                            time.sleep(2)
                            continue
                    return result
                else:
                    self.logger.warning(f"Lỗi API (lần {attempt+1}): {response.status_code}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        
            except requests.exceptions.Timeout:
                self.logger.warning(f"Timeout (lần {attempt+1})")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    raise Exception(f"Timeout sau {max_retries} lần thử")
            except Exception as e:
                self.logger.warning(f"Lỗi (lần {attempt+1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    raise
        
        raise Exception(f"Không thể lấy response sau {max_retries} lần thử")
    def _call_llm_continued(self, model: str, prompt: str, max_tokens: int = 8192) -> str:
        """Gọi LLM với khả năng tiếp tục nếu response bị cắt"""
        full_response = ""
        max_continuations = 3  # Tối đa 3 lần tiếp tục
        
        for continuation in range(max_continuations):
            try:
                self.logger.info(f"Gọi LLM (tiếp tục {continuation + 1}): {model}")
                
                current_prompt = prompt if continuation == 0 else f"{full_response}\n\n[TIẾP TỤC: Hãy viết thêm, chưa được cắt ngang]"
                
                payload = {
                    "model": model,
                    "prompt": current_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": max_tokens,
                        "top_p": 0.9,
                        "repeat_penalty": 1.1,
                        "stop": ["###", "```end", "[END]"]  # Stop tokens
                    }
                }
                
                response = requests.post(
                    f"{self.ollama_base}/api/generate",
                    json=payload,
                    timeout=180  # 3 phút timeout
                )
                
                if response.status_code == 200:
                    result = response.json().get('response', '')
                    full_response += result
                    
                    # Kiểm tra nếu response đã hoàn chỉnh
                    if self._is_complete_response(result):
                        self.logger.info(f"Response hoàn chỉnh sau {continuation + 1} lần")
                        break
                    else:
                        self.logger.warning(f"Response có thể bị cắt, tiếp tục...")
                        time.sleep(1)
                else:
                    self.logger.error(f"Lỗi API: {response.status_code}")
                    break
                    
            except Exception as e:
                self.logger.error(f"Lỗi khi tiếp tục: {e}")
                break
        
        return full_response
    
    def _is_complete_response(self, response: str) -> bool:
        """Kiểm tra xem response đã hoàn chỉnh chưa"""
        # Nếu response quá ngắn
        if len(response.strip()) < 100:
            return False
        
        # Nếu kết thúc bằng dấu câu hoàn chỉnh
        endings = ['.', '!', '?', '```', '###']
        last_char = response.strip()[-1] if response.strip() else ''
        
        # Nếu có từ chỉ sự hoàn thành
        completion_indicators = [
            'kết thúc', 'tạm kết', 'trên đây', 'tóm lại',
            'end', 'conclusion', 'summary', 'in conclusion'
        ]
        
        last_50_chars = response.strip()[-50:].lower()
        has_completion_indicator = any(indicator in last_50_chars for indicator in completion_indicators)
        
        return last_char in endings or has_completion_indicator
    def _select_best_model(self, llm_type: str) -> str:
        """Chọn model tốt nhất cho task"""
        # Ưu tiên các model mạnh, nhiều token
        model_priority = {
            'chat': ['mixtral:latest', 'qwen2.5:14b', 'llama3:8b'],
            'coding': ['deepseek-coder:6.7b', 'codellama:7b', 'llama3:8b'],
            'web_search': ['mixtral:latest', 'qwen2.5:14b', 'llama3.1:latest'],
            'research': ['qwen2.5:14b', 'mixtral:latest', 'llama3.1:latest']
        }
        
        available_models = self._get_available_models()
        priority_list = model_priority.get(llm_type, ['mixtral:latest', 'llama3:8b'])
        
        # Chọn model có sẵn đầu tiên trong danh sách ưu tiên
        for model in priority_list:
            if model in available_models:
                return model
        
        # Fallback
        return 'llama3:8b'
    
    def _get_available_models(self):
        """Lấy danh sách model có sẵn từ Ollama"""
        try:
            response = requests.get(f"{self.ollama_base}/api/tags", timeout=5)
            if response.status_code == 200:
                models = [model['name'] for model in response.json().get('models', [])]
                return models
        except:
            pass
        return ['llama3:8b']  # Fallback
    def _mock_llm_call(self, plan: Dict[str, Any]) -> str:
        """Mock LLM call chi tiết hơn"""
        intent = plan.get('intent', 'chat')
        user_input = plan.get('user_input', '')
        language = plan.get('language', 'vi')
        
        # Mock responses chi tiết hơn
        mock_responses = {
            'coding': {
                'vi': f"""**PHÂN TÍCH YÊU CẦU**: {user_input}

**GIẢI PHÁP**:
1. **Phân tích vấn đề**: Hiểu rõ yêu cầu và xác định các trường hợp cần xử lý
2. **Thiết kế thuật toán**: Lựa chọn thuật toán phù hợp, tối ưu hiệu suất
3. **Triển khai code**: Viết code rõ ràng, có cấu trúc tốt
4. **Xử lý lỗi**: Dự đoán và xử lý các lỗi có thể xảy ra

**CODE MẪU**:
"""},}


def main():
    print("Chức năng đang được phát triển")
    print("Kết nối đến LLM để nhận code đầy đủ")
    
if __name__ == "__main__":
    main()