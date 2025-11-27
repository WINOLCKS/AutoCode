import os
import logging
import subprocess
from enum import Enum
from typing import Optional, List, Dict
import json


from agents.tester import extract_pytest_cases, run_pytest_cases, check_regressions, compute_error_fingerprint
from agents.self_repair import micro_fix
from agents.error_book import append_error, backfill_fixed
from core.srs_handler import load_srs  # 假设 Substep 5 会实现，目前 mock
from core.srs_handler import parse_srs  # NEW: 导入 parse_srs 函数
from core.code_generator import CodeGenerator  # NEW: 导入 CodeGenerator 用于真实代码生成
from core.code_generator import CodeGenerator

logger = logging.getLogger(__name__)

class State(Enum):
    NEGOTIATING = "NEGOTIATING"
    CODING = "CODING"
    PASS = "PASS"
    FAILED = "FAILED"

class IterationState:
    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        self.state = State.NEGOTIATING
        self.iteration = 0
        self.current_code: Optional[str] = None
        srs_path = os.path.join(project_dir, 'project.srs.md')
        self.srs_content = load_srs(project_dir)
        parsed = parse_srs(self.srs_content)  # MODIFIED: 调用 parse_srs 以补全用例
        self.test_cases = parsed['test_cases']
        self.code_generator = CodeGenerator()  # NEW: 初始化 CodeGenerator（默认 config_path）

    def transition_to_coding(self):
        """从 NEGOTIATING 过渡到 CODING。"""
        self.state = State.CODING
        logger.info("Transitioned to CODING state")

    def run_iteration(self) -> bool:
        self.iteration += 1
        logger.info(f"Starting iteration {self.iteration}")

        # MODIFIED: 使用云端 LLM 生成代码，注入 SRS + 账本 + 回归标志 + project_dir
        history_path = os.path.join(self.project_dir, 'error_history.json')
        with open(history_path, 'r', encoding='utf-8') as f:
            error_book = json.load(f)
        is_regression = len(check_regressions([], history_path)) > 0  # 检查是否有历史回归
        self.current_code = self.code_generator.generate_code(self.srs_content, error_book, self.project_dir,is_regression)  # MODIFIED: 传入 project_dir

        # 步骤1: 在 sandbox 中运行测试
        fresh_errors: List[Dict] = run_pytest_cases(self.test_cases, self.current_code, self.project_dir)

        # 步骤2: 检查回归
        history_path = os.path.join(self.project_dir, 'error_history.json')
        regressions = check_regressions(fresh_errors, history_path)
        if regressions:
            logger.warning(f"Detected {len(regressions)} regressions")
            # 可以选择 FAILED 或继续，但根据设计，继续但记录

        if not fresh_errors:  # 无错误，所有测试通过，无回归
            self.state = State.PASS
            self.generate_report()
            logger.info("All tests passed, no regressions")
            return True

        # 步骤3: 处理错误并更新日志
        for err in fresh_errors:
            error_hash = err['hash']  # 已由 tester 计算
            abstract = err['abstract']
            case = err['case']
            append_error(self.project_dir, error_hash, self.iteration, abstract, case)

        # 步骤4: 尝试 minor fix（仅当单一错误且为 Syntax/NameError）
        if len(fresh_errors) == 1:
            err = fresh_errors[0]
            exception_str = err['exception'].lower()  # 转小写，忽略大小写
            if 'syntaxerror' in exception_str or 'indentationerror' in exception_str or 'nameerror' in exception_str:
                logger.info("Detected minor error, attempting LLM fix")
                fixed_code, fixed = micro_fix(self.current_code, err)
                if fixed:
                    self.current_code = fixed_code
                    backfill_fixed(self.project_dir, err['hash'], self.iteration)
                    return self.run_iteration()  # 递归重试（移除参数）

        # 如果未修复或多个错误，继续下一次迭代
        logger.info(f"Iteration {self.iteration} failed, proceeding to next")
        return False

    def generate_report(self):
        """生成 pytest HTML 报告。"""
        report_path = os.path.join(self.project_dir, 'pytest_report.html')
        test_file = os.path.join(self.project_dir, 'temp_tests.py')  # 临时写入测试用例
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.test_cases))

        cmd = ['pytest', test_file, f'--html={report_path}', '--self-contained-html']
        try:
            result = subprocess.run(cmd, check=True, capture_output=True)  # 捕获输出
            logger.info(f"Report generated at {report_path}")
        except subprocess.CalledProcessError as e:
            stderr_output = e.stderr.decode('utf-8') if e.stderr else 'No stderr'
            logger.error(f"Failed to generate report: {e}. Stderr: {stderr_output}")
        finally:
            os.remove(test_file)  # 清理