import os
from core.srs_handler import load_srs, parse_srs

def test_load_and_parse(tmp_path):
    srs_path = tmp_path / 'project.srs.md'
    mock_content = """## Requirements
Req1
## Functions
Func1
```python
def test_add():
    assert True
```"""
    srs_path.write_text(mock_content, encoding='utf-8')
    content = load_srs(str(tmp_path))
    assert "Req1" in content
    parsed = parse_srs(content)
    assert len(parsed['test_cases']) == 1