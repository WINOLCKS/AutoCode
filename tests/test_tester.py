import pytest
from agents.tester import extract_pytest_cases, compute_error_fingerprint, run_pytest_cases, check_regressions
import os
import json

def test_extract_cases(tmp_path):
    srs_file = tmp_path / 'mock.srs.md'
    srs_file.write_text('# Test\n```python\ndef test_ok():\n    assert True\n```\n```python\ndef not_test():\n    pass\n```')
    cases = extract_pytest_cases(str(srs_file))
    assert len(cases) == 1
    assert 'def test_ok' in cases[0]

def test_compute_fingerprint():
    fp = compute_error_fingerprint('SyntaxError', 'line 1', 'print("hi")')  # 故意缺少闭括号以测试 fallback
    assert len(fp) == 64  # SHA256 长度

def test_run_pytest_cases(tmp_path):
    cases = ['def test_add():\n    assert add(1,2) == 3']
    code = 'def add(a,b): return a + b'
    src_dir = str(tmp_path)
    errors = run_pytest_cases(cases, code, src_dir)
    assert len(errors) == 0  # 通过

    bad_code = 'def add(a, b: return a + b'  # 故意语法错误（缺少闭括号）
    errors = run_pytest_cases(cases, bad_code, src_dir)
    assert len(errors) == 1
    assert 'SyntaxError' in errors[0]['exception']

def test_check_regressions(tmp_path):
    history_file = tmp_path / 'mock.json'
    history = [{'hash': 'abc', 'fixed_iter': 1}, {'hash': 'def', 'fixed_iter': None}]
    with open(history_file, 'w') as f:
        json.dump(history, f)
    fresh = [{'hash': 'abc'}, {'hash': 'ghi'}]
    regs = check_regressions(fresh, str(history_file))
    assert len(regs) == 1
    assert regs[0]['hash'] == 'abc'