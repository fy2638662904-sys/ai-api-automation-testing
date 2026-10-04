"""DeepSeek Chat Completions 接口封装。

把 base_url、鉴权、超时、默认模型统一收在这里，测试用例只关心业务参数，
避免每个用例重复写 URL 和 headers（V1 的写法就是每个函数里重复一遍）。
"""

import requests


class DeepSeekClient:
    def __init__(self, base_url: str, api_key: str, model: str, timeout: int = 60):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }
        )

    # ---------- 原始请求 ----------

    def chat_raw(self, payload: dict, headers: dict | None = None) -> requests.Response:
        """发送请求并返回原始 Response，供需要断言状态码/错误结构的用例使用。"""
        return self.session.post(
            f"{self.base_url}/chat/completions",
            json=payload,
            headers=headers,
            timeout=self.timeout,
        )

    # ---------- 便捷方法 ----------

    def build_payload(self, messages: list, **overrides) -> dict:
        payload = {"model": self.model, "messages": messages, "stream": False}
        payload.update(overrides)
        return payload

    def chat(self, messages: list, **overrides) -> requests.Response:
        return self.chat_raw(self.build_payload(messages, **overrides))

    def ask(self, prompt: str, **overrides) -> str:
        """单轮提问，直接返回回答文本；断言失败时由用例处理。"""
        response = self.chat([{"role": "user", "content": prompt}], **overrides)
        assert response.status_code == 200, f"HTTP {response.status_code}: {response.text[:200]}"
        return response.json()["choices"][0]["message"]["content"]


def content_of(response: requests.Response) -> str:
    """从成功响应中取出回答文本。"""
    return response.json()["choices"][0]["message"]["content"]
