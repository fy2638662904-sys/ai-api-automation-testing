"""测试数据加载（数据与代码分离的唯一入口）。"""

import json
import pathlib

DATA_DIR = pathlib.Path(__file__).resolve().parent.parent / "data"


def load_cases(filename: str) -> list:
    with open(DATA_DIR / filename, encoding="utf-8") as fh:
        return json.load(fh)


def case_ids(cases: list) -> list:
    return [f"{c['id']} {c['title']}" for c in cases]


def pytest_params(cases: list) -> list:
    """把用例数据转成 parametrize 参数；带 xfail 的用例标记为已知问题。"""
    import pytest  # 延迟导入：导出文档等场景不需要 pytest

    params = []
    for case in cases:
        marks = []
        if case.get("xfail"):
            marks.append(pytest.mark.xfail(reason=case["xfail"], strict=True))
        params.append(pytest.param(case, id=f"{case['id']} {case['title']}", marks=marks))
    return params
