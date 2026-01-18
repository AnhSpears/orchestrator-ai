"""
Script kiểm tra hệ thống ORCHESTRATOR
"""
import sys
import os

# Thêm đường dẫn hiện tại
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Kiểm tra import các module"""
    print("🧪 Kiểm tra import các module...")
    
    tests = [
        ("core_ai", "core_ai"),
        ("chat_module", "chat_module"),
        ("core_ai.brain", "Brain"),
        ("core_ai.reasoning_engine", "ReasoningEngine"),
        ("core_ai.llm_dispatcher", "LLMDispatcher"),
        ("chat_module.language_detect", "detect_language"),
        ("chat_module.intent_classifier", "classify_intent"),
    ]
    
    all_passed = True
    
    for module_name, class_name in tests:
        try:
            if module_name == "core_ai":
                module = __import__("core_ai")
                print(f"✅ {module_name}")
            elif "." in module_name:
                # Import từ submodule
                parts = module_name.split(".")
                mod = __import__(parts[0])
                for part in parts[1:]:
                    mod = getattr(mod, part)
                print(f"✅ {module_name}")
            else:
                module = __import__(module_name)
                print(f"✅ {module_name}")
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
            all_passed = False
        except Exception as e:
            print(f"⚠️  {module_name}: {e}")
    
    return all_passed

def test_directories():
    """Kiểm tra cấu trúc thư mục"""
    print("\n📁 Kiểm tra cấu trúc thư mục...")
    
    required_dirs = [
        "core_ai",
        "chat_module", 
        "memory",
        "tools",
        "agents",
        "sandbox",
        "config",
        "logs",
        "reports"
    ]
    
    all_exist = True
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name) and os.path.isdir(dir_name):
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/ (thiếu)")
            all_exist = False
    
    return all_exist

def test_config_files():
    """Kiểm tra file cấu hình"""
    print("\n⚙️ Kiểm tra file cấu hình...")
    
    required_files = [
        "config/permissions.yaml",
        "config/llm_profiles.yaml",
        "config/settings.yaml"
    ]
    
    all_exist = True
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (thiếu)")
            all_exist = False
    
    return all_exist

def test_simple_chat():
    """Kiểm tra chat đơn giản"""
    print("\n💬 Kiểm tra chat đơn giản...")
    
    try:
        from chat_module.language_detect import detect_language
        from chat_module.intent_classifier import classify_intent
        
        test_cases = [
            ("Xin chào", "vi", "chat"),
            ("Hello world", "en", "chat"),
            ("Tìm kiếm thông tin", "vi", "web_search"),
            ("Write Python code", "en", "coding"),
        ]
        
        for text, expected_lang, expected_intent in test_cases:
            lang = detect_language(text)
            intent_result = classify_intent(text, lang)
            intent = intent_result.get("intent", "unknown")
            
            if lang == expected_lang and intent == expected_intent:
                print(f"✅ '{text[:20]}...' -> lang:{lang}, intent:{intent}")
            else:
                print(f"⚠️  '{text[:20]}...' -> lang:{lang}(expected:{expected_lang}), intent:{intent}(expected:{expected_intent})")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi kiểm tra chat: {e}")
        return False

def main():
    """Hàm chính kiểm tra"""
    print("=" * 60)
    print("KIỂM TRA HỆ THỐNG ORCHESTRATOR")
    print("=" * 60)
    
    results = []
    
    results.append(test_directories())
    results.append(test_config_files())
    results.append(test_imports())
    results.append(test_simple_chat())
    
    print("\n" + "=" * 60)
    print("KẾT QUẢ KIỂM TRA")
    print("=" * 60)
    
    if all(results):
        print("🎉 TẤT CẢ KIỂM TRA ĐÃ THÀNH CÔNG!")
        print("\nHệ thống đã sẵn sàng. Chạy: python main.py")
        return 0
    else:
        print("⚠️  MỘT SỐ KIỂM TRA THẤT BẠI!")
        print("\nVui lòng kiểm tra lại cấu trúc thư mục và file.")
        return 1

if __name__ == "__main__":
    sys.exit(main())