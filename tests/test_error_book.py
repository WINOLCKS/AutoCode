import os
import json
from agents.error_book import append_error, backfill_fixed, load_error_history

def test_append_and_backfill(tmp_path):
    project_dir = str(tmp_path)
    append_error(project_dir, "hash1", 1, "abstract1", "case1")
    history = load_error_history(project_dir)
    assert len(history) == 1
    assert history[0]["fixed_iter"] is None

    backfill_fixed(project_dir, "hash1", 2)
    history = load_error_history(project_dir)
    assert history[0]["fixed_iter"] == 2