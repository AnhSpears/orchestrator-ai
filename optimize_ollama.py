"""
Script tối ưu hóa Ollama cho hệ thống ORCHESTRATOR
"""
import subprocess
import sys
import os

def check_ollama():
    """Kiểm tra Ollama đã cài đặt chưa"""
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama đã cài đặt")
            return True
        else:
            print("❌ Ollama không khả dụng")
            return False
    except FileNotFoundError:
        print("❌ Ollama chưa cài đặt")
        return False

def check_models():
    """Kiểm tra model đã có"""
    try:
        result = subprocess.run(['ollama', 'list'], 
                              capture_output=True, text=True)
        print("📋 Model hiện có:")
        print(result.stdout)
        return True
    except:
        print("⚠️ Không thể kiểm tra model")
        return False

def recommend_models():
    """Đề xuất model tối ưu"""
    print("\n🎯 ĐỀ XUẤT MODEL TỐI ƯU:")
    print("="*50)
    print("1. qwen2.5:14b - Tốt nhất cho tiếng Việt")
    print("   - Hỗ trợ tiếng Việt xuất sắc")
    print("   - Context 32K tokens")
    print("   - Dung lượng: ~8GB")
    print("")
    print("2. llama3:8b - Nhanh, ổn định")
    print("   - Tốc độ nhanh")
    print("   - Tiếng Anh tốt, tiếng Việt khá")
    print("   - Dung lượng: ~4.7GB")
    print("")
    print("3. deepseek-coder:6.7b - Chuyên code")
    print("   - Code xuất sắc")
    print("   - Hỗ trợ nhiều ngôn ngữ lập trình")
    print("   - Dung lượng: ~4GB")
    print("")
    print("📥 Lệnh tải model:")
    print("  ollama pull qwen2.5:14b")
    print("  ollama pull llama3:8b")
    print("  ollama pull deepseek-coder:6.7b")

def optimize_settings():
    """Tối ưu cài đặt Ollama"""
    print("\n⚙️ CÀI ĐẶT TỐI ƯU:")
    print("="*50)
    
    settings = """
# Thêm vào biến môi trường hoặc chạy trước khi start ollama

# Windows (PowerShell):
$env:OLLAMA_NUM_GPU = 1
$env:OLLAMA_MAX_VRAM = "6144"  # 6GB VRAM

# Linux/Mac:
export OLLAMA_NUM_GPU=1
export OLLAMA_MAX_VRAM="6144"

# Khởi động Ollama với nhiều resource:
ollama serve --num-gpu 1
"""
    print(settings)
    
    # Tạo file batch cho Windows
    if sys.platform == "win32":
        with open("start_ollama_optimized.bat", "w") as f:
            f.write("""@echo off
set OLLAMA_NUM_GPU=1
set OLLAMA_MAX_VRAM=6144
echo Starting Ollama with optimized settings...
ollama serve
pause""")
        print("✅ Đã tạo file start_ollama_optimized.bat")

def create_model_profiles():
    """Tạo profile model tối ưu"""
    profiles = {
        "chat": {
            "primary": "qwen2.5:14b",
            "fallback": "llama3:8b",
            "timeout": 45,
            "max_tokens": 4096
        },
        "coding": {
            "primary": "deepseek-coder:6.7b", 
            "fallback": "llama3:8b",
            "timeout": 60,
            "max_tokens": 8192
        },
        "research": {
            "primary": "qwen2.5:14b",
            "fallback": "llama3:8b",
            "timeout": 60,
            "max_tokens": 8192
        }
    }
    
    with open("optimal_model_profiles.yaml", "w") as f:
        import yaml
        yaml.dump(profiles, f, default_flow_style=False, allow_unicode=True)
    
    print("✅ Đã tạo file optimal_model_profiles.yaml")

def main():
    """Hàm chính"""
    print("="*60)
    print("TỐI ƯU HÓA OLLAMA CHO ORCHESTRATOR")
    print("="*60)
    
    if not check_ollama():
        print("\n⚠️ Vui lòng cài đặt Ollama trước:")
        print("  https://ollama.com/download")
        return
    
    check_models()
    recommend_models()
    optimize_settings()
    create_model_profiles()
    
    print("\n" + "="*60)
    print("✅ HOÀN TẤT TỐI ƯU HÓA")
    print("="*60)
    print("\n📋 HÀNH ĐỘNG TIẾP THEO:")
    print("1. Tải model đề xuất: ollama pull qwen2.5:14b")
    print("2. Khởi động Ollama: start_ollama_optimized.bat")
    print("3. Chạy ORCHESTRATOR: python main.py")
    print("4. Kiểm tra: python test_model_capabilities.py")

if __name__ == "__main__":
    main()