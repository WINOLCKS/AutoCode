import os
import re
import logging
import yaml
from .utils import LLMClient
from agents.local_llm_agent import LocalLLMAgent

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

class SRSHandler:
    def __init__(self, config_path='config/config.yaml'):
        self.config = yaml.safe_load(open(config_path))
        self.llm = LLMClient(self.config['cloud_llm'])
        self.local_agent = LocalLLMAgent()  # 初始化本地 Ollama Agent

    def generate_initial_srs(self, user_requirement: str, project_dir: str) -> str:
        """生成初版 SRS，使用云端 LLM。"""
        prompt = f"基于用户自然语言需求：{user_requirement}\n编写完整的 SRS Markdown 文档，包括：\n- 原始需求摘录\n- 功能点清单（可勾选）\n- 接口签名（函数/类/CLI）\n- 验收用例：必须包含至少3个 pytest 格式的测试函数，覆盖正常、边界和异常场景。每个用例放在单独的 ```python 代码块中，例如：\n```python\ndef test_add():\n    assert add(1, 2) == 3\n```\n确保输出为纯 Markdown 格式，无额外解释。"
        temperature = self.config['cloud_llm'].get('temperature_srs', 0.3)
        srs_content = self.llm.generate(prompt, temperature)
        srs_path = os.path.join(project_dir, 'project.srs.md')
        os.makedirs(os.path.dirname(srs_path), exist_ok=True)
        with open(srs_path, 'w', encoding='utf-8') as f:
            f.write(srs_content)
        return srs_content

    def modify_srs(self, feedback: str, current_srs: str, project_dir: str) -> str:
        """根据反馈修改 SRS，使用云端 LLM。"""
        prompt = f"当前 SRS：{current_srs}\n用户反馈：{feedback}\n修改 SRS 文档，确保一致性，并更新验收用例。验收用例必须包含至少3个 pytest 格式的测试函数，覆盖正常、边界和异常场景，每个用例放在单独的 ```python 代码块中。"
        temperature = self.config['cloud_llm'].get('temperature_srs', 0.3)
        new_srs = self.llm.generate(prompt, temperature)
        srs_path = os.path.join(project_dir, 'project.srs.md')
        os.makedirs(os.path.dirname(srs_path), exist_ok=True)
        with open(srs_path, 'w', encoding='utf-8') as f:
            f.write(new_srs)
        return new_srs

    def parse_srs_with_supplement(self, srs_content: str, project_dir: str) -> dict:
        """解析 SRS，提取测试用例，并补全如果不足（类方法版本）。"""
        # 使用全局 parse_srs 作为基础解析
        parsed = parse_srs(srs_content)

        # 如果用例 <3，使用本地 Ollama 补全
        test_cases = parsed['test_cases']
        if len(test_cases) < 3:
            logger.warning(f"SRS 中测试用例不足 ({len(test_cases)})，使用本地 LLM 补全")
            supplement_prompt = f"基于 SRS 内容：{srs_content[:2000]}\n生成至少 {3 - len(test_cases)} 个 pytest 测试函数，覆盖正常、边界和异常场景。每个函数格式为：def test_xxx():\n    assert ...\n只输出代码，无解释。"
            supplement_cases = self.local_agent.generate(supplement_prompt)
            if supplement_cases:
                # 拆分并追加
                new_cases = re.findall(r'def test_.*?:.*?assert.*?(?=\n\n|def|$)', supplement_cases, re.DOTALL)
                parsed['test_cases'].extend(new_cases)
                # 更新 SRS 文件：追加新用例到末尾
                srs_path = os.path.join(project_dir, 'project.srs.md')
                with open(srs_path, 'a', encoding='utf-8') as f:
                    f.write("\n\n## 补充验收用例\n")
                    for case in new_cases:
                        f.write(f"```python\n{case}\n```\n")
                logger.info(f"补全了 {len(new_cases)} 个测试用例")

        return parsed