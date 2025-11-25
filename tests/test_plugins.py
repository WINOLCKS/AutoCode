import pytest
from unittest.mock import patch
from plugins.file_reader.reader import FileReader  # 假设 FileReader 类在 reader.py 中定义
from plugins.web_search.searcher import Searcher  # 假设 Searcher 类在 searcher.py 中定义


@pytest.fixture
def mock_file_content():
    return "Mock file content\nLine 2"


def test_file_reader_success(tmp_path, mock_file_content):
    # 创建 mock 文件
    file_path = tmp_path / 'test.txt'
    file_path.write_text(mock_file_content, encoding='utf-8')

    reader = FileReader()
    content = reader.read(str(file_path))  # 假设 read 方法返回文件内容
    assert content == mock_file_content
    assert "Line 2" in content


def test_file_reader_not_found():
    reader = FileReader()
    with pytest.raises(FileNotFoundError):
        reader.read('nonexistent_file.txt')  # 测试文件不存在异常


def test_web_searcher_success():
    searcher = Searcher()
    with patch('requests.get') as mock_get:  # 假设 searcher 使用 requests.get 进行搜索
        mock_get.return_value.status_code = 200  # 添加这一行，设置状态码为 200
        mock_get.return_value.json.return_value = {'RelatedTopics': [{'Text': 'Mock Result Title', 'FirstURL': 'https://mock.url'}]}  # 调整为 DuckDuckGo API 格式，以匹配 searcher.py 的解析逻辑
        results = searcher.search('test query')  # 假设 search 方法返回结果列表
        assert len(results) > 0
        assert 'Mock Result Title' in results[0]['title']


def test_web_searcher_empty_query():
    searcher = Searcher()
    with pytest.raises(ValueError):  # 假设空查询抛出 ValueError
        searcher.search('')  # 测试空查询处理