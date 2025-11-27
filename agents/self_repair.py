import re
import difflib
import ast
import os
import logging
import logging.config
import yaml
import ollama  # 新增导入

# 加载配置（保持原样）
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.yaml')
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

logging_conf_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'logging.conf')
logging.config.fileConfig(logging_conf_path)


def micro_fix(code: str, error: dict) -> tuple[str, bool]:

    if not error or 'exception' not in error:
        logging.warning("Invalid error dict, no fix attempted")
        return code, False

    exc = error['exception']
    logging.info(f"Attempting LLM micro fix for error: {exc[:100]}...")

    # LLM Prompt：设计为结构化，限制输出为代码或 NO_FIX
    prompt = f"""You are a code fixer. Given this Python code:
{code}

It has this error: {exc}

If it's a minor SyntaxError or NameError, fix it and return ONLY the full fixed code.
If you can't fix or it's not minor, return 'NO_FIX'."""

    try:
        response = ollama.generate(model='qwen3:4b', prompt=prompt, options={'temperature': 0.2, 'num_ctx': 16384})
        fixed_code = response['response'].strip()
        if fixed_code == 'NO_FIX':
            logging.info("LLM: No fix applied")
            return code, False
        logging.info("LLM: Fix applied")
        return fixed_code, True
    except Exception as e:
        logging.error(f"LLM call failed: {e}")
        return code, False