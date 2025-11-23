# Mock SRS for Phase 1 Testing
## 验收用例
```python
def test_add():
    from src.main_code import add  # 假设 src/main_code.py 有 add 函数
    assert add(1, 2) == 3

def test_subtract():
    from src.main_code import subtract
    assert subtract(5, 3) == 2