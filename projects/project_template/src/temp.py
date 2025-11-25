
import sys
sys.path.insert(0, r'projects\project_template\src')  # 插入到路径开头，优先搜索src/
def add(a, b): return a + b
def subtract(a, b): return a - b

def test_add():
    from main_code import add  # 假设 src/main_code.py 有 add 函数
    assert add(1, 2) == 3

def test_subtract():
    from main_code import subtract
    assert subtract(5, 3) == 2

# 调用测试函数（假设test_xxx无参）
test_func_name = 'test_add'
globals()[test_func_name]()
