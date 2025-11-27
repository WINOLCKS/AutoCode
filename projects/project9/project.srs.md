# 计算器程序 SRS 文档

## 原始需求摘录  
请编写一个计算器程序

## 功能点清单  
- [ ] 加法运算：支持两个数字的加法计算  
- [ ] 减法运算：支持两个数字的减法计算  
- [ ] 乘法运算：支持两个数字的乘法计算  
- [ ] 除法运算：支持两个数字的除法计算（处理除以零异常）  

## 接口签名  

### 函数接口  
```python
def add(a: float, b: float) -> float:
    """返回a与b的和"""
    pass

def subtract(a: float, b: float) -> float:
    """返回a与b的差"""
    pass

def multiply(a: float, b: float) -> float:
    """返回a与b的积"""
    pass

def divide(a: float, b: float) -> float:
    """返回a与b的商，当b为0时抛出ZeroDivisionError"""
    pass
```

### 类接口  
```python
class Calculator:
    def add(self, a: float, b: float) -> float:
        """返回a与b的和"""
        pass
    
    def subtract(self, a: float, b: float) -> float:
        """返回a与b的差"""
        pass
    
    def multiply(self, a: float, b: float) -> float:
        """返回a与b的积"""
        pass
    
    def divide(self, a: float, b: float) -> float:
        """返回a与b的商，当b为0时抛出ZeroDivisionError"""
        pass
```

### CLI 接口  
命令行调用格式：  
`python calculator.py <operation> <num1> <num2>`  
示例：  
```bash
python calculator.py add 1 2  
python calculator.py divide 10 2  
```

## 验收用例  

### 正常场景：加法运算  
```python
def test_add_normal():
    assert add(1, 2) == 3
```

### 边界场景：乘法零值处理  
```python
def test_multiply_boundary():
    assert multiply(0, 999999999) == 0
```

### 异常场景：除法除以零  
```python
import pytest

def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(5, 0)
```