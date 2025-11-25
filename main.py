import os
import logging
from core.state_machine import IterationState, State
from core.srs_handler import load_srs, parse_srs
import ollama

logger = logging.getLogger(__name__)

def simulate_generate_code(iteration: int) -> str:
    """Mock 云 LLM 生成代码，根据迭代调整。"""
    if iteration == 1:
        return "def add(a, b): return a + b\n def subtract(a, b): return a - b"  # 正确 mock
    elif iteration == 2:
        return "def add(a, b): return a + b\n def subtract(a, b return a - b"  # SyntaxError
    else:
        return "def add(a, b): return a + b\n def subtrct(a, b): return a - b"  # NameError

def main(project_dir: str):
    """模拟 coding loop。"""
    srs_content = load_srs(project_dir)
    parsed_srs = parse_srs(srs_content)  # 解析以验证

    state = IterationState(project_dir)
    state.transition_to_coding()

    max_iterations = 10  # 防止无限循环
    for i in range(1, max_iterations + 1):
        generated_code = simulate_generate_code(i)  # Mock 生成
        logger.info(f"Simulating code generation for iteration {i}")
        if state.run_iteration(generated_code):
            logger.info("Loop completed: PASS")
            break
    if state.state != State.PASS:
        state.state = State.FAILED
        logger.error("Max iterations reached: FAILED")

if __name__ == "__main__":
    project_dir = os.path.join(os.path.dirname(__file__), 'projects', 'project_template')
    main(project_dir)