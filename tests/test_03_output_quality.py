"""AI 输出质量：指令遵循、稳定性、幻觉、边界与准确性。"""

import pytest

from utils.data import load_cases, pytest_params
from utils.case_runner import run_case

CASES = load_cases("cases_quality.json")


@pytest.mark.quality
@pytest.mark.parametrize("case", pytest_params(CASES))
def test_output_quality(client, case, request):
    for _ in range(case.get("repeat", 1)):
        run_case(client, case, request)
