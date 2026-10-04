"""AI 安全：提示词注入、系统指令绕过、敏感信息泄露、越权与拒答。"""

import pytest

from utils.data import load_cases, pytest_params
from utils.case_runner import run_case

CASES = load_cases("cases_safety.json")


@pytest.mark.safety
@pytest.mark.parametrize("case", pytest_params(CASES))
def test_safety(client, case, request):
    run_case(client, case, request)
