"""人工复核辅助：把指定用例的真实回答完整打印出来。

AI 输出类用例的规则断言只能覆盖客观条件（长度、关键词、是否泄露密钥），
像"提示词注入有没有被绕过"必须看原文判断，所以单独留一个复核入口。

用法：
    python tools/review_outputs.py cases_safety.json
    python tools/review_outputs.py cases_safety.json SAFE-002 SAFE-003
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.api_client import DeepSeekClient  # noqa: E402
from utils.data import load_cases  # noqa: E402


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    filename = sys.argv[1]
    only = set(sys.argv[2:])

    key = os.getenv("DEEPSEEK_API_KEY")
    if not key:
        print("请先设置环境变量 DEEPSEEK_API_KEY")
        return 1

    client = DeepSeekClient(
        os.getenv("AI_API_BASE_URL", "https://api.deepseek.com"),
        key,
        os.getenv("AI_API_MODEL", "deepseek-flash"),
    )

    for case in load_cases(filename):
        if only and case["id"] not in only:
            continue
        messages = case.get("messages") or [{"role": "user", "content": case["prompt"]}]
        print("=" * 78)
        print(f"{case['id']} {case['title']}")
        if case.get("human_review"):
            print(f"复核点：{case['human_review']}")
        print("-" * 78)
        response = client.chat_raw(client.build_payload(messages))
        if response.status_code != 200:
            print(f"HTTP {response.status_code}: {response.text[:300]}")
            continue
        print(response.json()["choices"][0]["message"]["content"])
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
