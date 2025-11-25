import pytest
from agents.self_repair import micro_fix

def test_syntax_fix_paren():
    code = 'print("Hello"'
    error = {'exception': 'SyntaxError: unexpected EOF while parsing (line 1)'}
    fixed, is_fixed = micro_fix(code, error)
    assert is_fixed
    assert fixed == 'print("Hello")'  # 补引号

def test_syntax_fix_colon():
    code = 'def func()\n    pass'
    error = {'exception': 'SyntaxError: expected \':\' (line 1)'}
    fixed, is_fixed = micro_fix(code, error)
    assert is_fixed
    assert fixed == 'def func():\n    pass'  # 补冒号

def test_name_fix():
    code = 'def add(a, b):\n    return a + bb'  # 添加4空格缩进，确保AST解析成功
    error = {'exception': "NameError: name 'bb' is not defined"}
    fixed, is_fixed = micro_fix(code, error)
    assert is_fixed
    assert 'return a + b' in fixed  # 替换bb为b

def test_no_fix_multi_errors():
    code = 'invalid code'
    error = {}  # 无效error
    fixed, is_fixed = micro_fix(code, error)
    assert not is_fixed
    assert fixed == code

def test_no_match_name():
    code = 'print(unknown_var)'
    error = {'exception': "NameError: name 'unknown_var' is not defined"}
    fixed, is_fixed = micro_fix(code, error)
    assert not is_fixed