"""公共 fixture 与测试数据加载。"""

import os

import pytest

from utils.api_client import DeepSeekClient


@pytest.fixture(scope="session")
def api_key() -> str:
    key = os.getenv("DEEPSEEK_API_KEY")
    if not key:
        pytest.skip("未设置环境变量 DEEPSEEK_API_KEY，跳过需要真实调用的用例")
    return key


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("AI_API_BASE_URL", "https://api.deepseek.com")


@pytest.fixture(scope="session")
def model_name() -> str:
    return os.getenv("AI_API_MODEL", "deepseek-flash")


@pytest.fixture(scope="session")
def client(api_key, base_url, model_name) -> DeepSeekClient:
    return DeepSeekClient(base_url, api_key, model_name)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """把 AI 实际回答附加到测试报告，方便后续人工复核。"""
    outcome = yield
    report = outcome.get_result()
    observed = getattr(item, "_observed_output", None)
    if observed and report.when == "call":
        report.sections.append(("AI 实际输出", observed[:1200]))
