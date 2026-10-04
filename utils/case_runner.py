"""用例执行与断言封装。

所有用例共用一套数据驱动逻辑：测试文件只负责声明 marker 和指定数据文件，
具体请求构造、状态码断言、内容规则断言都在这里完成。
"""

import re


def _build_messages(case: dict) -> list:
    if "messages" in case:
        return case["messages"]
    if "content_repeat" in case:
        spec = case["content_repeat"]
        return [{"role": "user", "content": spec["text"] * spec["times"]}]
    return [{"role": "user", "content": case["prompt"]}]


def _build_payload(client, case: dict) -> dict:
    payload = client.build_payload(_build_messages(case))
    for key in case.get("drop_keys", []):
        payload.pop(key, None)
    payload.update(case.get("override", {}))
    return payload


def _check_content(content: str, rules: dict, case: dict) -> None:
    if not rules:
        return
    if rules.get("non_empty"):
        assert content.strip() != "", f"{case['id']} 回答为空"
    if "contains_any" in rules:
        keys = rules["contains_any"]
        assert any(k in content for k in keys), f"{case['id']} 未命中任一关键词 {keys}；实际：{content[:200]}"
    if "contains_all" in rules:
        for k in rules["contains_all"]:
            assert k in content, f"{case['id']} 缺少关键词 {k}；实际：{content[:200]}"
    for key in ("not_contains_any", "not_contains"):
        for k in rules.get(key, []):
            assert k not in content, f"{case['id']} 出现不应包含的内容 {k!r}；实际：{content[:200]}"
    if "max_len" in rules:
        assert len(content) <= rules["max_len"], (
            f"{case['id']} 回答长度 {len(content)} 超过上限 {rules['max_len']}"
        )
    if rules.get("no_newline"):
        assert "\n" not in content, f"{case['id']} 回答中出现换行"
    if "regex" in rules:
        assert re.search(rules["regex"], content), f"{case['id']} 未匹配正则 {rules['regex']}；实际：{content[:200]}"


def _assert_stream(response, case: dict) -> None:
    ctype = response.headers.get("Content-Type", "")
    body = response.text or ""
    assert "text/event-stream" in ctype, f"{case['id']} 流式响应 Content-Type 异常：{ctype}"
    assert body.strip().startswith("data:"), f"{case['id']} 流式响应体不是 SSE 格式：{body[:120]}"


def run_case(client, case: dict, request=None) -> dict:
    """执行单条用例并返回观察结果（供报告与后续分析使用）。"""
    payload = _build_payload(client, case)
    response = client.chat_raw(payload, headers=case.get("header_override"))

    # ---------- 状态码 ----------
    if "expect_status" in case:
        assert response.status_code == case["expect_status"], (
            f"{case['id']} 期望 HTTP {case['expect_status']}，实际 {response.status_code}；"
            f"响应：{response.text[:300]}"
        )
    if "expect_status_in" in case:
        assert response.status_code in case["expect_status_in"], (
            f"{case['id']} 期望 HTTP ∈ {case['expect_status_in']}，实际 {response.status_code}；"
            f"响应：{response.text[:300]}"
        )

    result = {"id": case["id"], "status": response.status_code}

    # ---------- 异常响应结构 ----------
    if response.status_code >= 400:
        body = response.json()
        assert "error" in body, f"{case['id']} 错误响应缺少 error 字段：{body}"
        if "expect_error_type" in case:
            assert body["error"].get("type") == case["expect_error_type"], (
                f"{case['id']} 错误类型期望 {case['expect_error_type']}，实际 {body['error'].get('type')}"
            )
        if "expect_message_contains" in case:
            assert case["expect_message_contains"] in str(body["error"].get("message", "")), (
                f"{case['id']} 错误信息未包含 {case['expect_message_contains']}：{body['error']}"
            )
        result["error"] = body["error"]
        return result

    # ---------- 流式响应 ----------
    if case.get("expect_stream"):
        _assert_stream(response, case)
        result["stream"] = True
        return result

    # ---------- 正常响应 ----------
    body = response.json()
    for key in case.get("expect_top_keys", []):
        assert key in body, f"{case['id']} 响应缺少顶层字段 {key}"

    choice = body["choices"][0]
    for key in case.get("expect_choice_keys", []):
        assert key in choice, f"{case['id']} choices[0] 缺少字段 {key}"

    if "expect_finish_reason" in case:
        assert choice.get("finish_reason") == case["expect_finish_reason"], (
            f"{case['id']} finish_reason 期望 {case['expect_finish_reason']}，实际 {choice.get('finish_reason')}"
        )
    if "expect_finish_reason_in" in case:
        assert choice.get("finish_reason") in case["expect_finish_reason_in"], (
            f"{case['id']} finish_reason 实际 {choice.get('finish_reason')}，"
            f"期望 ∈ {case['expect_finish_reason_in']}"
        )

    usage = body.get("usage") or {}
    for key in case.get("expect_usage_keys", []):
        assert key in usage, f"{case['id']} usage 缺少字段 {key}"
    if case.get("expect_usage_sum"):
        assert usage["total_tokens"] == usage["prompt_tokens"] + usage["completion_tokens"], (
            f"{case['id']} token 加和不成立：{usage}"
        )

    content = choice["message"]["content"]
    result["content"] = content

    # 记录实际输出，方便在报告里人工复核
    if request is not None:
        request.node._observed_output = f"[{case['id']}] {content}"

    _check_content(content, case.get("content_assert", {}), case)

    # 需要复核的用例：把人工检查提示一并写进报告
    if case.get("human_review") and request is not None:
        request.node._observed_output = (
            f"[{case['id']}] 人工复核点：{case['human_review']}\n实际输出：{content}"
        )
    return result
