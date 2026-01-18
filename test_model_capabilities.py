"""
Kiểm tra khả năng của từng model
"""
import requests
import time
import json

def test_model_response(model_name, prompt, max_tokens=4096):
    """Test model với prompt cụ thể"""
    print(f"\n{'='*60}")
    print(f"TESTING MODEL: {model_name}")
    print(f"{'='*60}")
    
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": max_tokens,
            "top_p": 0.9
        }
    }
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=120)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', '')
            
            print(f"⏱️  Thời gian: {elapsed:.2f}s")
            print(f"📝 Độ dài: {len(response_text)} ký tự")
            print(f"📊 Số từ: {len(response_text.split())}")
            
            # Phân tích chất lượng
            lines = response_text.count('\n') + 1
            sentences = response_text.count('.') + response_text.count('!') + response_text.count('?')
            
            print(f"📈 Số dòng: {lines}")
            print(f"📈 Số câu: {sentences}")
            
            # Kiểm tra ngôn ngữ
            vi_chars = ['à', 'á', 'ả', 'ã', 'ạ', 'ă', 'ắ', 'ằ', 'ẳ', 'ẵ', 'ặ']
            has_vi = any(char in response_text.lower() for char in vi_chars)
            print(f"🇻🇳 Có tiếng Việt: {'✅' if has_vi else '❌'}")
            
            # Preview
            print(f"\n📄 PREVIEW (200 ký tự đầu):")
            print(response_text[:200] + "...")
            
            # Kiểm tra nếu bị cắt
            last_char = response_text.strip()[-1] if response_text.strip() else ''
            if last_char not in ['.', '!', '?', '"', "'"]:
                print("⚠️  CẢNH BÁO: Response có thể bị cắt!")
            
            return {
                "success": True,
                "length": len(response_text),
                "time": elapsed,
                "text": response_text
            }
        else:
            print(f"❌ Lỗi HTTP: {response.status_code}")
            return {"success": False, "error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return {"success": False, "error": str(e)}

def main():
    """Test các model khác nhau"""
    print("KIỂM TRA KHẢ NĂNG CỦA CÁC MODEL LLAMA")
    print("="*60)
    
    # Test prompt tiếng Việt
    test_prompt = """
=== YÊU CẦU BẮT BUỘC ===
1. TRẢ LỜI 100% BẰNG TIẾNG VIỆT
2. ĐỘ DÀI TỐI THIỂU 500 TỪ
3. KHÔNG ĐƯỢC CẮT NGANG
4. TỔ CHỨC THÔNG TIN CÓ CẤU TRÚC

=== CÂU HỎI ===
Giải thích chi tiết về Trí Tuệ Nhân Tạo (Artificial Intelligence), bao gồm:
- Khái niệm và định nghĩa
- Lịch sử phát triển
- Các loại AI khác nhau
- Ứng dụng thực tế
- Xu hướng hiện tại
- Thách thức và tương lai

=== BẮT ĐẦU TRẢ LỜI (BẰNG TIẾNG VIỆT) ===
"""
    
    models_to_test = [
        "llama3:8b",
        "mixtral:latest", 
        "qwen2.5:14b",
        "deepseek-coder:6.7b"
    ]
    
    results = {}
    
    for model in models_to_test:
        results[model] = test_model_response(model, test_prompt, max_tokens=8192)
        time.sleep(2)  # Chờ giữa các request
    
    # Tổng kết
    print(f"\n{'='*60}")
    print("TỔNG KẾT KẾT QUẢ")
    print(f"{'='*60}")
    
    best_model = None
    best_length = 0
    
    for model, result in results.items():
        if result.get("success"):
            length = result.get("length", 0)
            print(f"{model}: {length} ký tự")
            
            if length > best_length:
                best_length = length
                best_model = model
        else:
            print(f"{model}: ❌ FAILED - {result.get('error')}")
    
    if best_model:
        print(f"\n🏆 MODEL TỐT NHẤT: {best_model} ({best_length} ký tự)")
        
        # Lưu kết quả
        with open("model_test_results.txt", "w", encoding="utf-8") as f:
            f.write(f"BEST MODEL: {best_model}\n\n")
            for model, result in results.items():
                f.write(f"{'='*60}\n")
                f.write(f"MODEL: {model}\n")
                if result.get("success"):
                    f.write(f"Length: {result.get('length')}\n")
                    f.write(f"Time: {result.get('time'):.2f}s\n")
                    f.write(f"\n--- RESPONSE ---\n")
                    f.write(result.get("text", "")[:1000])
                    f.write("\n...\n")
                else:
                    f.write(f"ERROR: {result.get('error')}\n")
    
    print("\n✅ Đã lưu kết quả vào model_test_results.txt")

if __name__ == "__main__":
    main()