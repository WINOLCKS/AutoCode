import os
import re
import logging
from .utils import LLMClient
import yaml

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

import yaml
from .utils import LLMClient  # 假设已存在
import os  # NEW: 添加 os 导入，如果未有

class SRSHandler:
    def __init__(self, config_path='config/config.yaml'):
        self.config = yaml.safe_load(open(config_path))
        self.llm = LLMClient(self.config['cloud_llm'])

    def generate_initial_srs(self, user_requirement: str, project_dir: str) -> str:  # MODIFIED: 添加 project_dir 参数
        prompt = f"基于用户自然语言需求：{user_requirement}\n编写完整的 SRS Markdown 文档，包括原始需求摘录、功能点清单、接口签名和 pytest 格式的验收用例。确保输出格式为 Markdown，且用例在代码块中。"
        temperature = self.config['cloud_llm']['temperature_srs']
        srs_content = self.llm.generate(prompt, temperature)
        srs_path = os.path.join(project_dir, 'project.srs.md')  # MODIFIED: 使用动态路径
        os.makedirs(os.path.dirname(srs_path), exist_ok=True)  # NEW: 自动创建目录如果不存在
        with open(srs_path, 'w', encoding='utf-8') as f:
            f.write(srs_content)
        return srs_content

    def modify_srs(self, feedback: str, current_srs: str, project_dir: str) -> str:  # MODIFIED: 添加 project_dir 参数
        prompt = f"当前 SRS：{current_srs}\n用户反馈：{feedback}\n修改 SRS 文档，确保一致性，并更新验收用例。输出完整 Markdown。"
        temperature = self.config['cloud_llm']['temperature_srs']
        new_srs = self.llm.generate(prompt, temperature)
        srs_path = os.path.join(project_dir, 'project.srs.md')  # MODIFIED: 使用动态路径
        os.makedirs(os.path.dirname(srs_path), exist_ok=True)  # NEW: 自动创建目录如果不存在
        with open(srs_path, 'w', encoding='utf-8') as f:
            f.write(new_srs)
        return new_srs