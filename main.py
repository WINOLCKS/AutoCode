import os
import logging
import json  # NEW: 用于账本加载
from core.state_machine import IterationState, State
from core.srs_handler import load_srs, parse_srs, SRSHandler  # NEW: 导入 SRSHandler 用于协商
from core.code_generator import CodeGenerator  # NEW: 导入，但实际在 state_machine 中使用

logger = logging.getLogger(__name__)

def main(project_dir: str):
    """主入口：先需求协商，然后 coding loop。"""
    srs_handler = SRSHandler()  # 初始化 SRSHandler
    user_requirement = input("请输入原始需求（自然语言）：")  # 用户输入需求
    srs_content = srs_handler.generate_initial_srs(user_requirement, project_dir)  # MODIFIED: 传入 project_dir
    print("生成的 SRS：\n" + srs_content)

    while True:
        feedback = input("审阅 SRS，提供反馈（行号或描述），或输入 'ok' 确认：")
        if feedback.lower() == 'ok':
            # 确认后，冻结 SRS（写入文件，只读）
            srs_path = os.path.join(project_dir, 'project.srs.md')
            with open(srs_path, 'w', encoding='utf-8') as f:
                f.write(srs_content)
            break
        else:
            srs_content = srs_handler.modify_srs(feedback, srs_content, project_dir)  # MODIFIED: 传入 project_dir
            print("修改后的 SRS：\n" + srs_content)

    parsed_srs = parse_srs(srs_content)  # 解析以验证

    state = IterationState(project_dir)
    state.transition_to_coding()

    max_iterations = 10  # 防止无限循环
    for i in range(1, max_iterations + 1):
        logger.info(f"Starting code generation for iteration {i}")
        if state.run_iteration():  # MODIFIED: 无需传入代码，现在内部生成
            logger.info("Loop completed: PASS")
            break
    if state.state != State.PASS:
        state.state = State.FAILED
        logger.error("Max iterations reached: FAILED")

if __name__ == "__main__":
    project_dir = os.path.join(os.path.dirname(__file__), 'projects', 'project_template')
    main(project_dir)