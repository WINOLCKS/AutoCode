from core.state_machine import IterationState
from unittest.mock import patch

def test_run_iteration_pass(tmp_path):
    project_dir = str(tmp_path)
    with patch('core.state_machine.load_srs', return_value="Mock SRS"):
        with patch('core.state_machine.extract_pytest_cases', return_value=['def test_add(): assert add(1, 2) == 3']):
            state = IterationState(project_dir)
            state.transition_to_coding()

            with patch('core.state_machine.run_pytest_cases', return_value=[]):  # Mock 无错误
                with patch('core.state_machine.check_regressions', return_value=[]):
                    with patch('core.state_machine.subprocess.run') as mock_run:  # Mock subprocess 以避免 report 错误
                        mock_run.return_value = None
                        assert state.run_iteration("mock_code") is True
                    assert state.state.name == "PASS"

def test_run_iteration_fail(tmp_path):
    project_dir = str(tmp_path)
    with patch('core.state_machine.load_srs', return_value="Mock SRS"):
        with patch('core.state_machine.extract_pytest_cases', return_value=['def test_add(): assert add(1, 2) == 3']):
            state = IterationState(project_dir)
            state.transition_to_coding()

            mock_errors = [{'hash': 'test_hash', 'abstract': 'test_abstract', 'case': 'test_case', 'exception': 'NameError: test'}]
            with patch('core.state_machine.run_pytest_cases', return_value=mock_errors):  # Mock 有单一错误
                with patch('core.state_machine.check_regressions', return_value=[]):
                    with patch('core.state_machine.micro_fix', return_value=("mock_fixed_code", False)):  # Mock 无修复
                        assert state.run_iteration("mock_code") is False