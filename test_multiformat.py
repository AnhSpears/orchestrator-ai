"""
TEST MULTIFORMAT - Kiểm tra xử lý đa định dạng
"""
import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_all_formats():
    """Test tất cả định dạng"""
    from tools.multiformat_processor import MultiFormatProcessor
    
    processor = MultiFormatProcessor()
    
    # Tạo thư mục test
    test_dir = Path("test_documents")
    test_dir.mkdir(exist_ok=True)
    
    print("🧪 KIỂM TRA XỬ LÝ ĐA ĐỊNH DẠNG")
    print("="*60)
    
    # Test files mẫu
    test_files = {
        "text.txt": "Đây là file text thuần túy.\nCó nhiều dòng.\nVà tiếng Việt có dấu.",
        "markdown.md": "# Tiêu đề\n\n- Mục 1\n- Mục 2\n\n```python\nprint('Hello')\n```",
        "data.json": '{"name": "Test", "value": 123, "list": [1, 2, 3]}',
        "config.yaml": "system:\n  name: Test\n  version: 1.0",
        "code.py": "def hello():\n    print('Hello World')\n\nclass Test:\n    pass"
    }
    
    # Tạo test files
    for filename, content in test_files.items():
        filepath = test_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # Test từng file
    supported_count = 0
    total_count = 0
    
    print("\n📋 ĐỊNH DẠNG ĐƯỢC HỖ TRỢ:")
    for ext, processor_func in processor.supported_formats.items():
        total_count += 1
        print(f"  ✅ {ext:10s} - {processor_func.__name__}")
        supported_count += 1
    
    print(f"\n📊 Tổng cộng: {supported_count}/{total_count} định dạng")
    
    # Test processing
    print("\n🧪 TEST XỬ LÝ FILE:")
    for test_file in test_dir.glob("*"):
        if test_file.is_file():
            print(f"\n📄 {test_file.name}:")
            result = processor.process_file(str(test_file))
            
            if "error" in result:
                print(f"  ❌ {result['error']}")
            else:
                print(f"  ✅ Type: {result.get('type', 'unknown')}")
                print(f"  📝 Preview: {str(result.get('content', ''))[:80]}...")
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir)
    
    print(f"\n{'='*60}")
    print("✅ TEST HOÀN TẤT!")
    
    # Hiển thị yêu cầu cài đặt
    print("\n📦 CẦN CÀI ĐẶT CHO ĐẦY ĐỦ TÍNH NĂNG:")
    print("""
# Office formats
pip install pandas openpyxl xlrd
pip install python-pptx
pip install python-docx

# PDF
pip install PyPDF2 pdfminer.six

# Images + OCR
pip install Pillow pytesseract

# Tesseract OCR engine (system install)
# Windows: https://github.com/UB-Mannheim/tesseract/wiki
# macOS: brew install tesseract
# Linux: sudo apt-get install tesseract-ocr
""")

if __name__ == "__main__":
    test_all_formats()