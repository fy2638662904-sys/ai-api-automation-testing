"""API 契约：认证失败、参数异常与输入边界。"""

import pytest

from utils.data import load_cases, pytest_params
from utils.case_runner import run_case

CASES = load_cases("cases_api_errors.json")


@pytest.mark.api
@pytest.mark.parametrize("case", pytest_params(CASES))
def test_api_errors(client, case, request):
    run_case(client, case, request)
