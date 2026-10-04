"""API 契约：正常请求与响应结构。"""

import pytest

from utils.data import load_cases, pytest_params
from utils.case_runner import run_case

CASES = load_cases("cases_api_basic.json")


@pytest.mark.api
@pytest.mark.parametrize("case", pytest_params(CASES))
def test_api_basic(client, case, request):
    run_case(client, case, request)
