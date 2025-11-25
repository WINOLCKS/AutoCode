import re
import ast
import hashlib
import json
import os
import logging
import yaml
import ollama  # 新增导入，用于 LLM 增强

from .sandbox import run_in_sandbox  # 同包导入沙箱

# 加载配置（相对路径，从agents/到根config/）
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.yaml')
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 配置日志（使用logging.conf）
logging_conf_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'logging.conf')
logging.config.fileConfig(logging_conf_path)

# LLM 配置（从 config.yaml 读取，或 hardcode）
LLM_MODEL = 'qwen3:8b'  # 你的模型
LLM_TEMPERATURE = 0.2  # 低温度，确保精确


def extract_pytest_cases(srs_path: str) -> list[str]:
    """
    从SRS Markdown提取pytest用例代码块。
    - srs_path: SRS文件路径。
    返回: pytest函数字符串列表。
    示例: 提取def test_xxx()块。
    """
    logging.info(f"Extracting pytest cases from {srs_path}")
    try:
        with open(srs_path, 'r', encoding='utf-8') as f:
            content = f.read()
        cases = re.findall(r'```python\n(.*?)\n```', content, re.DOTALL)
        filtered_cases = [case.strip() for case in cases if case.strip().startswith('def test_')]
        logging.info(f"Extracted {len(filtered_cases)} test cases")
        return filtered_cases
    except FileNotFoundError:
        logging.error(f"SRS file not found: {srs_path}")
        return []
    except Exception as e:
        logging.error(f"Extraction error: {e}")
        return []


def compute_error_fingerprint(error_type: str, stack_trace: str, related_code: str) -> str:
    """
    计算错误指纹：异常类型 + 栈迹 + AST子树哈希。
    - error_type: 异常类型（如'SyntaxError'）。
    - stack_trace: 异常栈字符串。
    - related_code: 相关代码片段（用例或源码）。
    返回: SHA256哈希字符串。

    增强: 用 LLM 生成智能摘要（abstract）。
    """
    logging.debug("Computing error fingerprint")
    try:
        tree = ast.parse(related_code)
        ast_str = ast.dump(tree, indent=None)
    except SyntaxError as e:
        ast_str = related_code  # 回退到原始代码
        logging.warning(f"AST parse failed: {e}")
    data = f"{error_type}:{stack_trace}:{ast_str}".encode('utf-8')
    hash_value = hashlib.sha256(data).hexdigest()
    logging.debug(f"Fingerprint computed: {hash_value[:10]}...")  # 只记录前10位

    # LLM 增强: 生成摘要（可选，回退到原逻辑）
    try:
        prompt = f"""Analyze this Python error:
Error type: {error_type}
Stack trace: {stack_trace}
Related code: {related_code}

Provide a brief summary (under 100 chars) including possible cause. Output ONLY the summary text."""
        response = ollama.generate(model=LLM_MODEL, prompt=prompt, options={'temperature': LLM_TEMPERATURE})
        enhanced_abstract = response['response'].strip()[:100]
        logging.info(f"LLM enhanced abstract: {enhanced_abstract}")
        # 这里返回 hash，但你可以修改 err['abstract'] 在调用处使用此摘要
    except Exception as e:
        logging.error(f"LLM analysis failed: {e}")
        enhanced_abstract = f"{error_type} in test case"  # 回退

    return hash_value  # 原返回不变，摘要可在调用处使用


def run_pytest_cases(cases: list[str], code: str, src_dir: str) -> list[dict]:
    """
    执行提取的pytest用例（在沙箱中）。
    - cases: 用例列表。
    - code: 要测试的源码字符串（假设包含被测函数）。
    - src_dir: 源码目录（用于sys.path）。
    返回: fresh_errors列表[{'hash': str, 'abstract': str, 'case': str, 'exception': str, 'llm_diagnosis': str}]

    增强: 用 LLM 分析每个异常，提供诊断信息。
    """
    logging.info(f"Running {len(cases)} pytest cases")
    fresh_errors = []
    for case in cases:
        # 移除任何导入语句，因为 code 是内联字符串，直接使用函数
        adjusted_case = re.sub(r'from\s+.*\s+import\s+.*', '', case).strip()  # 用 regex 移除导入行

        # 组合完整代码：直接内联 code + adjusted_case + 调用测试，无需 sys.path 或模块导入
        full_code = f"""
{code}  # 内联源码函数定义

{adjusted_case}  # 测试用例

# 调用测试函数（假设test_xxx无参）
test_func_name = '{adjusted_case.split('(')[0].split()[-1]}'
globals()[test_func_name]()
"""
        logging.debug(f"Executing test case: {adjusted_case[:50]}...")
        result = run_in_sandbox(full_code, src_dir)

        if result['exception']:
            error_type = result['exception'].split(':')[0].strip() if ':' in result['exception'] else 'Unknown'
            stack_trace = result['exception']
            hash_value = compute_error_fingerprint(error_type, stack_trace, adjusted_case)

            # LLM 增强: 分析异常，提供诊断
            try:
                prompt = f"""Diagnose this Python test failure:
Error: {result['exception']}
Code snippet: {adjusted_case}

Output JSON: {{"abstract": "brief summary <100 chars", "diagnosis": "possible cause and fix suggestion"}}"""
                response = ollama.generate(model=LLM_MODEL, prompt=prompt, options={'temperature': LLM_TEMPERATURE})
                llm_output = json.loads(response['response'].strip())  # 假设输出 JSON
                abstract = llm_output.get('abstract', f"{error_type} in test case")
                diagnosis = llm_output.get('diagnosis', '')
                logging.info(f"LLM diagnosis: {diagnosis}")
            except Exception as e:
                logging.error(f"LLM diagnosis failed: {e}")
                abstract = f"{error_type} in test case"
                diagnosis = ''

            err = {
                'hash': hash_value,
                'abstract': abstract,  # 使用 LLM 增强摘要
                'case': adjusted_case,
                'exception': result['exception'],
                'llm_diagnosis': diagnosis  # 新增字段，供上游使用
            }
            fresh_errors.append(err)
            logging.warning(f"Test failed: {err['abstract']}")

    logging.info(f"Found {len(fresh_errors)} fresh errors")
    return fresh_errors


def check_regressions(fresh_errors: list[dict], history_path: str) -> list[dict]:
    """
    检查fresh_errors是否为回归（fixed_iter != None）。
    - fresh_errors: 新错误列表。
    - history_path: 账本路径。
    返回: 回归错误列表。

    增强: 如果有回归，用 LLM 生成总结报告。
    """
    logging.info(f"Checking regressions in {history_path}")
    try:
        with open(history_path, 'r', encoding='utf-8') as f:
            history = json.load(f)
    except FileNotFoundError:
        logging.warning("History file not found, no regressions")
        history = []
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e}")
        history = []

    regressions = [err for err in fresh_errors if
                   any(h['hash'] == err['hash'] and h.get('fixed_iter') is not None for h in history)]

    # LLM 增强: 如果有回归，生成总结
    if regressions:
        logging.error(f"Detected {len(regressions)} regressions")
        try:
            regression_summary = [f"Hash: {err['hash']}, Abstract: {err['abstract']}" for err in regressions]
            joined_summary = '\n'.join(regression_summary)  # 预计算 join，避免 f-string 内部反斜杠
            prompt = f"""Summarize these regressions:
{joined_summary}

Output a brief report (<200 chars) on why they might have regressed."""
            response = ollama.generate(model=LLM_MODEL, prompt=prompt, options={'temperature': LLM_TEMPERATURE})
            summary = response['response'].strip()
            logging.info(f"LLM regression summary: {summary}")
            # 可以将 summary 添加到 regressions 或日志
        except Exception as e:
            logging.error(f"LLM summary failed: {e}")
    else:
        logging.info("No regressions found")

    return regressions