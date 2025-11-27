import os
import logging
import json  # NEW: 用于账本加载
from core.state_machine import IterationState, State
from core.srs_handler import load_srs, parse_srs, SRSHandler  # NEW: 导入 SRSHandler 用于协商
from core.code_generator import CodeGenerator  # NEW: 导入，但实际在 state_machine 中使用

logger = logging.getLogger(__name__)


def create_new_project(base_dir: str, template_dir: str) -> str:
    """创建新项目目录，复制模板并初始化。"""
    # 找到现有项目最大编号（如 project1 -> 1）
    existing_projects = [d for d in os.listdir(base_dir) if d.startswith('project') and d[7:].isdigit()]
    max_num = max([int(d[7:]) for d in existing_projects] or [0])
    new_project_name = f'project{max_num + 1}'
    new_project_dir = os.path.join(base_dir, new_project_name)

    os.makedirs(new_project_dir, exist_ok=True)
    os.makedirs(os.path.join(new_project_dir, 'src'), exist_ok=True)
    os.makedirs(os.path.join(new_project_dir, 'reports'), exist_ok=True)

    # 复制模板文件
    for file in os.listdir(template_dir):
        src = os.path.join(template_dir, file)
        dst = os.path.join(new_project_dir, file)
        if os.path.isfile(src):
            with open(src, 'rb') as f_src, open(dst, 'wb') as f_dst:
                f_dst.write(f_src.read())

    # 初始化账本为空数组（覆盖旧内容）
    history_path = os.path.join(new_project_dir, 'error_history.json')
    with open(history_path, 'w', encoding='utf-8') as f:
        json.dump([], f)

    # 清空旧 SRS 和 src（如果存在）
    srs_path = os.path.join(new_project_dir, 'project.srs.md')
    open(srs_path, 'w').close()
    src_path = os.path.join(new_project_dir, 'src', 'src.py')
    open(src_path, 'w').close()

    logger.info(f"创建新项目: {new_project_dir}")
    return new_project_dir


def main():
    base_dir = os.path.join(os.path.dirname(__file__), 'projects')
    template_dir = os.path.join(base_dir, 'project_template')

    # 创建新项目
    project_dir = create_new_project(base_dir, template_dir)

    # 需求协商阶段
    srs_handler = SRSHandler()
    user_requirement = input("请输入原始需求（自然语言）：")
    srs_content = srs_handler.generate_initial_srs(user_requirement, project_dir)
    print("生成的 SRS：\n" + srs_content)

    while True:
        feedback = input("审阅 SRS，提供反馈（行号或描述），或输入 'ok' 确认：")
        if feedback.lower() == 'ok':
            srs_path = os.path.join(project_dir, 'project.srs.md')
            with open(srs_path, 'w', encoding='utf-8') as f:
                f.write(srs_content)
            break
        else:
            srs_content = srs_handler.modify_srs(feedback, srs_content, project_dir)
            print("修改后的 SRS：\n" + srs_content)

    parsed_srs = parse_srs(srs_content)

    state = IterationState(project_dir)
    state.transition_to_coding()

    max_iterations = 10
    for i in range(1, max_iterations + 1):
        logger.info(f"Starting code generation for iteration {i}")
        if state.run_iteration():
            logger.info("Loop completed: PASS")
            break
    if state.state != State.PASS:
        state.state = State.FAILED
        logger.error("Max iterations reached: FAILED")

if __name__ == "__main__":
    main()