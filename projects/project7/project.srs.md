# 计算器程序 SRS文档


## 1. 原始需求摘录  
用户需求：请写一个计算器程序  


## 2. 功能点清单  
- [√] 加法运算：计算两个数的和  
- [√] 减法运算：计算两个数的差  
- [√] 乘法运算：计算两个数的积  
- [√] 除法运算：计算两个数的商（处理除以零异常）  
- [√] 输入验证：拒绝非数字类型输入并抛出异常  


## 3. 接口签名  
### 函数接口  
```python
def add(a: float, b: float) -> float:
    """计算两个数的加法结果"""
    pass

def subtract(a: float, b: float) -> float:
    """计算两个数的减法结果"""
    pass

def multiply(a: float, b: float) -> float:
    """计算两个数的乘法结果"""
    pass

def divide(a: float, b: float) -> float:
    """计算两个数的除法结果，除数为0时抛出ZeroDivisionError"""
    pass
```


## 4. 验收用例  

### 正常场景：基础加法运算  
```python
def test_add_normal():
    assert add(1.5, 2.5) == 4.0
    assert add(-3, 5) == 2
```

### 边界场景：大数减法运算  
```python
def test_subtract_boundary():
    assert subtract(10**18, 10**18 -1) == 1
    assert subtract(0, 999999) == -999999
```

### 异常场景：除以零错误  
```python
import pytest

def test_divide_by_zero_exception():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)
```

### 异常场景：非数字输入错误  
```python
import pytest

def test_invalid_input_exception():
    with pytest.raises(TypeError):
        multiply("abc", 123)
```