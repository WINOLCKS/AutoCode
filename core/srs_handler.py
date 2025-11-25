import os
import re
import logging

logger = logging.getLogger(__name__)

def load_srs(project_dir: str) -> str:
    """加载 SRS 文件内容。"""
    srs_path = os.path.join(project_dir, 'project.srs.md')
    if not os.path.exists(srs_path):
        logger.error(f"SRS file not found: {srs_path}")
        raise FileNotFoundError(f"SRS file not found: {srs_path}")
    try:
        with open(srs_path, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.info(f"Loaded SRS from {srs_path}")
        return content
    except Exception as e:
        logger.error(f"Failed to load SRS: {e}")
        raise

def parse_srs(content: str) -> dict:
    """解析 SRS 内容：提取要求、函数、测试用例。"""
    requirements = re.findall(r'## Requirements\n(.*?)(?=##|$)', content, re.DOTALL)
    functions = re.findall(r'## Functions\n(.*?)(?=##|$)', content, re.DOTALL)
    test_cases = re.findall(r'```python\n(.*?)\n```', content, re.DOTALL)
    parsed = {
        'requirements': requirements[0].strip() if requirements else '',
        'functions': functions[0].strip() if functions else '',
        'test_cases': [case.strip() for case in test_cases if case.strip().startswith('def test_')]
    }
    if not parsed['test_cases']:
        logger.warning("No test cases found in SRS")
    logger.info(f"Parsed SRS: {len(parsed['test_cases'])} test cases")
    return parsed