from .utils import LLMClient
import yaml
import json
import os

class CodeGenerator:
    def __init__(self, config_path='config/config.yaml'):
        self.config = yaml.safe_load(open(config_path))
        self.llm = LLMClient(self.config['cloud_llm'])

    def generate_code(self, srs_content: str, error_book: dict, project_dir: str, is_regression=False) -> str:  # MODIFIED: 添加 project_dir 参数
        prompt = f"读取 SRS 全文：{srs_content}\n错误账本：{json.dumps(error_book, ensure_ascii=False)}\n生成完整、可运行的 Python 源码文件（单一文件，如 src.py），严格遵守 SRS 中的接口和功能。不含任何解释或注释。"
        if is_regression:
            prompt += "\n强调：不得再次引入已修复的错误。"
            temperature = self.config['cloud_llm']['temperature_regression']
        else:
            temperature = self.config['cloud_llm']['temperature_code']
        code = self.llm.generate(prompt, temperature)
        src_path = os.path.join(project_dir, 'src', 'src.py')  # MODIFIED: 使用动态路径
        os.makedirs(os.path.dirname(src_path), exist_ok=True)  # NEW: 自动创建 src/ 目录
        with open(src_path, 'w', encoding='utf-8') as f:
            f.write(code)
        return code