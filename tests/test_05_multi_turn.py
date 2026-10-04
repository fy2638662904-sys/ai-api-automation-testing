"""多轮对话：上下文记忆、指代切换、指令冲突与长上下文。"""

import pytest

from utils.data import load_cases, pytest_params
from utils.case_runner import run_case

CASES = load_cases("cases_multi_turn.json")


@pytest.mark.multi_turn
@pytest.mark.parametrize("case", pytest_params(CASES))
def test_multi_turn(client, case, request):
    run_case(client, case, request)
