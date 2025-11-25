from main import main
from unittest.mock import patch

def test_main_simulation(tmp_path):
    # Mock 项目目录，创建 mock SRS
    srs_path = tmp_path / 'project.srs.md'
    srs_path.write_text("Mock SRS\n```python\ndef test_add(): assert add(1,2)==3\n```", encoding='utf-8')
    (tmp_path / 'error_history.json').write_text("[]", encoding='utf-8')

    with patch('core.state_machine.IterationState.run_iteration', return_value=True):
        main(str(tmp_path))