# 计算器程序 SRS 文档

## 原始需求摘录
> 请编写一个计算器程序

## 功能点清单
- [ ] 加法运算：支持两个数字相加
- [ ] 减法运算：支持两个数字相减  
- [ ] 乘法运算：支持两个数字相乘  
- [ ] 除法运算：支持两个数字相除（除数不为零）  

## 接口签名

### 类接口
```python
class Calculator:
    def add(self, a: float, b: float) -> float:
        """加法运算：返回a + b的结果"""
        pass
    
    def subtract(self, a: float, b: float) -> float:
        """减法运算：返回a - b的结果"""
        pass
    
    def multiply(self, a: float, b: float) -> float:
        """乘法运算：返回a * b的结果"""
        pass
    
    def divide(self, a: float, b: float) -> float:
        """除法运算：返回a / b的结果，除数为零时抛出ZeroDivisionError"""
        pass
```

### CLI 接口
通过命令行调用格式：  
`python calculator.py <operation> <num1> <num2>`  

参数说明：  
- operation：运算类型（add/subtract/multiply/divide）  
- num1/num2：参与运算的数字  

示例：  
```bash
python calculator.py add 2 3   # 输出5  
python calculator.py divide 10 2 # 输出5  
```

## 验收用例

### 正常场景：加法运算
```python
def test_add_normal():
    calc = Calculator()
    assert calc.add(2, 3) == 5
    assert calc.add(-1, 1) == 0
    assert calc.add(0.5, 0.3) == 0.8
```

### 边界场景：大数乘法
```python
def test_multiply_boundary():
    calc = Calculator()
    assert calc.multiply(10**6, 10**6) == 10**12
    assert calc.multiply(0, 999999) == 0
    assert calc.multiply(-1000, 500) == -500000
```

### 异常场景：除法除以零
```python
import pytest

def test_divide_by_zero():
    calc = Calculator()
    with pytest.raises(ZeroDivisionError):
        calc.divide(5, 0)
    with pytest.raises(ZeroDivisionError):
        calc.divide(-3.14, 0)
```