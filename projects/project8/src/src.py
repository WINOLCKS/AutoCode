```python
import sys

class Calculator:
    def add(self, a: float, b: float) -> float:
        return a + b
    
    def subtract(self, a: float, b: float) -> float:
        return a - b
    
    def multiply(self, a: float, b: float) -> float:
        return a * b
    
    def divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ZeroDivisionError
        return a / b

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python src.py <operation> <num1> <num2>")
        sys.exit(1)
    op = sys.argv[1]
    try:
        num1 = float(sys.argv[2])
        num2 = float(sys.argv[3])
    except ValueError:
        print("Invalid number")
        sys.exit(1)
    calc = Calculator()
    try:
        if op == 'add':
            res = calc.add(num1, num2)
        elif op == 'subtract':
            res = calc.subtract(num1, num2)
        elif op == 'multiply':
            res = calc.multiply(num1, num2)
        elif op == 'divide':
            res = calc.divide(num1, num2)
        else:
            print(f"Invalid operation: {op}")
            sys.exit(1)
        print(int(res) if res.is_integer() else res)
    except ZeroDivisionError:
        print("Error: Division by zero")
        sys.exit(1)
```