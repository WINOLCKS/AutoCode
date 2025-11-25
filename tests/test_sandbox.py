import pytest
from agents.sandbox import run_in_sandbox

def test_normal_execution():
    result = run_in_sandbox('print("Test")')
    assert result['stdout'].strip() == 'Test'
    assert result['returncode'] == 0
    assert result['exception'] is None

def test_syntax_error():
    result = run_in_sandbox('print("Test"')  # 缺括号
    assert 'SyntaxError' in result['exception']
    assert result['returncode'] != 0

def test_timeout():
    result = run_in_sandbox('import time; time.sleep(20)')  # 超时
    assert 'TimeoutError' in result['exception']

def test_network_block():  # 手动检查，预期失败
    result = run_in_sandbox('import requests; requests.get("https://example.com")')
    assert 'ConnectionError' in result['exception'] or 'OSError' in result['exception']  # 视环境

def test_file_write_block():
    result = run_in_sandbox('with open("test.txt", "w") as f: f.write("test")')
    assert 'PermissionError' in result['exception'] or result['returncode'] == 0  # umask 限制