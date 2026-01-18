"""
SELF-LEARNING MODULE - Tự học code và tự test nâng cấp
"""
import os
import sys
import ast
import json
import logging
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime

class SelfLearning:
    """Module tự học code và tự test"""
    
    def __init__(self, sandbox_path: str = "sandbox"):
        self.logger = logging.getLogger(__name__)
        self.sandbox_path = Path(sandbox_path)
        self.sandbox_path.mkdir(exist_ok=True)
        
        # Learning database
        self.learning_db = self.sandbox_path / "learning_db.json"
        self._init_learning_db()
    
    def _init_learning_db(self):
        """Khởi tạo database học tập"""
        if not self.learning_db.exists():
            with open(self.learning_db, 'w', encoding='utf-8') as f:
                json.dump({
                    "learned_patterns": [],
                    "test_cases": [],
                    "improvements": [],
                    "stats": {
                        "total_learned": 0,
                        "total_tests": 0,
                        "success_rate": 0.0
                    },
                    "created_at": datetime.now().isoformat()
                }, f, indent=2)
    
    def learn_from_code(self, code: str, source: str = "user_input") -> Dict[str, Any]:
        """Học từ code mẫu"""
        try:
            # Phân tích code
            analysis = self._analyze_code(code)
            
            # Trích xuất patterns
            patterns = self._extract_patterns(code, analysis)
            
            # Lưu vào database
            with open(self.learning_db, 'r', encoding='utf-8') as f:
                db = json.load(f)
            
            pattern_entry = {
                "id": f"pattern_{len(db['learned_patterns']) + 1}",
                "code_preview": code[:500],
                "analysis": analysis,
                "patterns": patterns,
                "source": source,
                "learned_at": datetime.now().isoformat(),
                "usage_count": 0
            }
            
            db['learned_patterns'].append(pattern_entry)
            db['stats']['total_learned'] += 1
            
            with open(self.learning_db, 'w', encoding='utf-8') as f:
                json.dump(db, f, indent=2)
            
            return {
                "status": "success",
                "learned_patterns": len(patterns),
                "analysis_summary": analysis,
                "pattern_id": pattern_entry["id"]
            }
            
        except Exception as e:
            self.logger.error(f"Lỗi học code: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _analyze_code(self, code: str) -> Dict[str, Any]:
        """Phân tích code"""
        try:
            tree = ast.parse(code)
            
            analysis = {
                "functions": [],
                "classes": [],
                "imports": [],
                "loops": 0,
                "conditionals": 0,
                "try_except": 0,
                "has_docstrings": False
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis["functions"].append(node.name)
                    if ast.get_docstring(node):
                        analysis["has_docstrings"] = True
                        
                elif isinstance(node, ast.ClassDef):
                    analysis["classes"].append(node.name)
                    
                elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                    analysis["imports"].append(ast.unparse(node))
                    
                elif isinstance(node, ast.For) or isinstance(node, ast.While):
                    analysis["loops"] += 1
                    
                elif isinstance(node, ast.If):
                    analysis["conditionals"] += 1
                    
                elif isinstance(node, ast.Try):
                    analysis["try_except"] += 1
            
            return analysis
            
        except SyntaxError as e:
            return {
                "error": f"Syntax error: {e}",
                "valid_code": False
            }
        except Exception as e:
            return {
                "error": str(e),
                "valid_code": False
            }
    
    def _extract_patterns(self, code: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Trích xuất patterns từ code"""
        patterns = []
        
        # Pattern 1: Function definition với docstring
        if analysis.get("has_docstrings", False):
            patterns.append({
                "type": "documented_function",
                "description": "Hàm có docstring giải thích",
                "best_practice": True
            })
        
        # Pattern 2: Error handling
        if analysis.get("try_except", 0) > 0:
            patterns.append({
                "type": "error_handling",
                "description": "Xử lý lỗi với try-except",
                "best_practice": True
            })
        
        # Pattern 3: Modular imports
        imports = analysis.get("imports", [])
        if len(imports) > 0:
            patterns.append({
                "type": "module_import",
                "description": f"Sử dụng {len(imports)} modules",
                "modules": imports
            })
        
        # Pattern 4: Clean code (dựa trên độ phức tạp)
        if analysis.get("loops", 0) <= 3 and analysis.get("conditionals", 0) <= 5:
            patterns.append({
                "type": "clean_code",
                "description": "Code đơn giản, dễ đọc",
                "best_practice": True
            })
        
        return patterns
    
    def generate_test_cases(self, code: str) -> List[Dict[str, Any]]:
        """Tạo test cases tự động"""
        test_cases = []
        
        # Phân tích để tạo test
        analysis = self._analyze_code(code)
        
        # Test case 1: Syntax test
        test_cases.append({
            "id": "test_syntax",
            "description": "Kiểm tra cú pháp code",
            "type": "syntax",
            "expected": "No syntax errors",
            "automated": True
        })
        
        # Test case 2: Function test (nếu có hàm)
        functions = analysis.get("functions", [])
        for func in functions[:2]:  # Tối đa 2 hàm
            test_cases.append({
                "id": f"test_func_{func}",
                "description": f"Kiểm tra hàm {func}",
                "type": "function",
                "target": func,
                "expected": "Runs without errors",
                "automated": True
            })
        
        # Test case 3: Import test
        if analysis.get("imports"):
            test_cases.append({
                "id": "test_imports",
                "description": "Kiểm tra imports",
                "type": "import",
                "expected": "All imports available",
                "automated": True
            })
        
        return test_cases
    
    def run_tests_in_sandbox(self, code: str, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Chạy test trong sandbox an toàn"""
        results = []
        passed = 0
        failed = 0
        
        # Tạo file test tạm thời
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', 
                                        dir=self.sandbox_path, delete=False) as f:
            # Viết code + test runner
            test_code = f"""
{code}

# Test runner
if __name__ == "__main__":
    print("=== STARTING TESTS ===")
    
    # Test 1: Syntax (đã pass nếu chạy được đến đây)
    print("✅ Test 1: Syntax - PASSED")
    
    # Test 2: Check functions exist
"""
            
            # Thêm test cho từng hàm
            for test in test_cases:
                if test["type"] == "function":
                    func_name = test["target"]
                    test_code += f"""
    try:
        # Check if {func_name} exists and callable
        if callable({func_name}):
            print("✅ Test {func_name}: Function exists - PASSED")
        else:
            print("❌ Test {func_name}: Not callable - FAILED")
    except NameError:
        print("❌ Test {func_name}: Function not defined - FAILED")
"""
            
            f.write(test_code)
            temp_file = f.name
        
        try:
            # Chạy trong sandbox
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.sandbox_path
            )
            
            # Phân tích kết quả
            output = result.stdout + result.stderr
            
            for line in output.split('\n'):
                if '✅' in line:
                    passed += 1
                    results.append({
                        "status": "passed",
                        "message": line.strip()
                    })
                elif '❌' in line:
                    failed += 1
                    results.append({
                        "status": "failed",
                        "message": line.strip()
                    })
            
            # Cleanup
            os.unlink(temp_file)
            
            return {
                "total_tests": passed + failed,
                "passed": passed,
                "failed": failed,
                "success_rate": passed / (passed + failed) if (passed + failed) > 0 else 0,
                "results": results,
                "output": output[:1000]  # Giới hạn output
            }
            
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "error": "Test timeout",
                "results": []
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "results": []
            }
    
    def suggest_improvements(self, code: str, test_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Đề xuất cải tiến code"""
        improvements = []
        
        # Phân tích code
        analysis = self._analyze_code(code)
        
        # Improvement 1: Thiếu docstring
        if not analysis.get("has_docstrings", False) and analysis.get("functions"):
            improvements.append({
                "type": "add_docstrings",
                "priority": "medium",
                "description": "Thêm docstring cho các hàm",
                "reason": "Docstring giúp code dễ đọc và bảo trì"
            })
        
        # Improvement 2: Thiếu error handling
        if analysis.get("try_except", 0) == 0 and analysis.get("functions"):
            improvements.append({
                "type": "add_error_handling",
                "priority": "high",
                "description": "Thêm xử lý lỗi với try-except",
                "reason": "Code có thể crash với input không hợp lệ"
            })
        
        # Improvement 3: Test coverage
        success_rate = test_results.get("success_rate", 0)
        if success_rate < 0.7:
            improvements.append({
                "type": "improve_test_coverage",
                "priority": "high",
                "description": "Cải thiện test coverage",
                "reason": f"Tỷ lệ test pass chỉ đạt {success_rate:.0%}"
            })
        
        return improvements
    
    def auto_learn_and_improve(self, code: str) -> Dict[str, Any]:
        """Tự động học và đề xuất cải tiến"""
        try:
            # Bước 1: Học từ code
            learn_result = self.learn_from_code(code, "auto_learning")
            
            # Bước 2: Tạo test cases
            test_cases = self.generate_test_cases(code)
            
            # Bước 3: Chạy tests
            test_results = self.run_tests_in_sandbox(code, test_cases)
            
            # Bước 4: Đề xuất cải tiến
            improvements = self.suggest_improvements(code, test_results)
            
            # Bước 5: Tạo báo cáo
            report = {
                "learning": learn_result,
                "testing": test_results,
                "improvements": improvements,
                "summary": {
                    "code_length": len(code),
                    "functions_found": len(learn_result.get("analysis_summary", {}).get("functions", [])),
                    "patterns_learned": learn_result.get("learned_patterns", 0),
                    "tests_passed": test_results.get("passed", 0),
                    "improvements_suggested": len(improvements)
                },
                "timestamp": datetime.now().isoformat()
            }
            
            return {
                "status": "success",
                "report": report,
                "message": f"Đã học {learn_result.get('learned_patterns', 0)} patterns, " \
                          f"chạy {test_results.get('total_tests', 0)} tests, " \
                          f"đề xuất {len(improvements)} cải tiến"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }