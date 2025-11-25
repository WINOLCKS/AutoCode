import json
import os
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

def load_error_history(project_dir: str) -> List[Dict]:
    """加载 error_history.json 文件。"""
    history_path = os.path.join(project_dir, 'error_history.json')
    if not os.path.exists(history_path):
        logger.warning(f"Error history file not found: {history_path}. Creating empty list.")
        return []
    try:
        with open(history_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in {history_path}: {e}")
        return []

def save_error_history(project_dir: str, history: List[Dict]):
    """保存 error_history.json 文件。"""
    history_path = os.path.join(project_dir, 'error_history.json')
    with open(history_path, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=4)
    logger.info(f"Error history saved to {history_path}")

def append_error(project_dir: str, error_hash: str, iteration: int, abstract: str, case: str):
    """追加新错误到历史。"""
    history = load_error_history(project_dir)
    new_entry = {
        "hash": error_hash,
        "first_iter": iteration,
        "fixed_iter": None,  # 初始为 None，待回填
        "abstract": abstract,
        "case": case
    }
    history.append(new_entry)
    save_error_history(project_dir, history)
    logger.info(f"Appended error with hash {error_hash} at iteration {iteration}")

def backfill_fixed(project_dir: str, error_hash: str, fixed_iteration: int):
    """回填 fixed_iter 到匹配的 hash 条目。"""
    history = load_error_history(project_dir)
    for entry in history:
        if entry["hash"] == error_hash and entry["fixed_iter"] is None:
            entry["fixed_iter"] = fixed_iteration
            save_error_history(project_dir, history)
            logger.info(f"Backfilled fixed_iter {fixed_iteration} for hash {error_hash}")
            return
    logger.warning(f"No unfixed entry found for hash {error_hash}")