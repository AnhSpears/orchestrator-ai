# HỆ THỐNG ORCHESTRATOR AI

Hệ thống AI tổng quát, an toàn, mở rộng được với kiến trúc bất biến.

## 🎯 MỤC TIÊU
- Chat ngôn ngữ tự nhiên (ưu tiên tiếng Việt)
- Kiến trúc core bất biến, không sửa đổi
- Multi-agent có kiểm soát
- Chạy local ổn định 100%

## 📁 CẤU TRÚC THƯ MỤC
ORCHESTRATOR/
├── core_ai/ # Core AI bất biến
├── chat_module/ # Xử lý ngôn ngữ tự nhiên
├── memory/ # Hệ thống memory
├── tools/ # Công cụ (web search, code executor)
├── agents/ # Các agent độc lập
├── sandbox/ # Môi trường an toàn
├── config/ # Cấu hình hệ thống
├── logs/ # Log hệ thống
├── main.py # Điểm khởi chạy
└── requirements.txt # Thư viện cần thiết

## 🚀 CÀI ĐẶT & CHẠY

### 1. Cài đặt Python
- Python 3.8 hoặc cao hơn
- Pip (package manager)

### 2. Cài đặt Ollama (cho LLM local)
```bash
# Trên macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Khởi động Ollama
ollama serve

# Tải các model (trong terminal mới)
ollama pull llama3:8b
ollama pull mixtral:latest
ollama pull deepseek-coder:6.7b