from app.agent_kernel.guardrails.contracts import (
    GuardrailContext,
    GuardrailDecision,
    GuardrailFinding,
    GuardrailResult,
)


class UnsafeControlOrHarassmentInterceptor:
    _keywords = ("跟踪", "监视", "偷拍", "骚扰", "报复", "威胁", "PUA", "操控", "骗她", "骗他")
    _unsafe_guidance_markers = (
        "你可以",
        "建议你",
        "应该",
        "教你",
        "最有效",
        "办法",
        "方法",
        "偷偷",
    )
    _safe_boundary_markers = (
        "不能帮助",
        "不能帮",
        "不会帮助",
        "不能按这个方向",
        "不建议",
        "不要",
        "请不要",
        "尊重",
    )

    def inspect(self, content: str, context: GuardrailContext) -> GuardrailResult:
        if not any(keyword in content for keyword in self._keywords):
            return GuardrailResult(decision=GuardrailDecision.ALLOW)
        if context.direction in {"output", "tool_output"} and self._is_safe_boundary_statement(
            content
        ):
            return GuardrailResult(decision=GuardrailDecision.ALLOW)

        return GuardrailResult(
            decision=GuardrailDecision.BLOCK,
            user_message=(
                "我不能帮助你跟踪、监视、骚扰或操控对方。"
                "这个请求可能侵犯他人边界或带来安全风险，我不能按这个方向继续。"
                "你可以换成尊重对方意愿的沟通目标，我会帮你组织表达。"
            ),
            findings=[
                GuardrailFinding(
                    category="unsafe_control_or_harassment",
                    severity="high",
                    message="检测到跟踪、监视、骚扰、操控或报复相关内容。",
                )
            ],
        )

    def _is_safe_boundary_statement(self, content: str) -> bool:
        has_safe_boundary = any(marker in content for marker in self._safe_boundary_markers)
        has_unsafe_guidance = any(marker in content for marker in self._unsafe_guidance_markers)
        return has_safe_boundary and not has_unsafe_guidance


class SystemPromptLeakageInterceptor:
    _phrases = (
        "系统提示词如下",
        "# ai 恋爱大师智能体",
        "# AI 恋爱大师智能体",
        "developer message",
        "system prompt:",
        "SECRET_KEY",
    )

    def inspect(self, content: str, context: GuardrailContext) -> GuardrailResult:
        if context.direction not in {"output", "tool_output"}:
            return GuardrailResult(decision=GuardrailDecision.ALLOW)
        normalized = content.lower()
        if not any(phrase.lower() in normalized for phrase in self._phrases):
            return GuardrailResult(decision=GuardrailDecision.ALLOW)

        return GuardrailResult(
            decision=GuardrailDecision.BLOCK,
            user_message="模型输出包含系统规则或敏感信息风险，我不能按这个方向继续。",
            findings=[
                GuardrailFinding(
                    category="system_prompt_leakage",
                    severity="critical",
                    message="检测到疑似系统提示词、内部规则或配置泄露。",
                )
            ],
        )
