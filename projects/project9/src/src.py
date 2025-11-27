```python
import sys

def add(a: float, b: float) -> float:
    return a + b

def subtract(a: float, b: float) -> float:
    return a - b

def multiply(a: float, b: float) -> float:
    return a * b

def divide(a: float, b: float) -> float:
    if b == 0:
        raise ZeroDivisionError("division by zero")
    return a / b

class Calculator:
    def add(self, a: float, b: float) -> float:
        return add(a, b)
    
    def subtract(self, a: float, b: float) -> float:
        return subtract(a, b)
    
    def multiply(self, a: float, b: float) -> float:
        return multiply(a, b)
    
    def divide(self, a: float, b: float) -> float:
        return divide(a, b)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python src.py <operation> <num1> <num2>")
        sys.exit(1)
    operation = sys.argv[1]
    try:
        num1 = float(sys.argv[2])
        num2 = float(sys.argv[3])
    except ValueError:
        print("num1 and num2 must be valid numbers")
        sys.exit(1)
    try:
        if operation == "add":
            print(add(num1, num2))
        elif operation == "subtract":
            print(subtract(num1, num2))
        elif operation == "multiply":
            print(multiply(num1, num2))
        elif operation == "divide":
            print(divide(num1, num2))
        else:
            print("Invalid operation. Use add, subtract, multiply, divide")
            sys.exit(1)
    except ZeroDivisionError as e:
        print(e)
        sys.exit(1)
```