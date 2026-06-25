from app.agent_kernel.guardrails.contracts import (
    GuardrailContext,
    GuardrailDecision,
    GuardrailFinding,
    GuardrailResult,
)


class PromptInjectionInterceptor:
    _phrases = (
        "忽略之前",
        "忽略以上",
        "忽略所有规则",
        "ignore previous",
        "ignore all previous",
        "disregard previous",
        "越狱",
        "jailbreak",
        "developer message",
        "system message",
    )

    def inspect(self, content: str, context: GuardrailContext) -> GuardrailResult:
        normalized = content.lower()
        if not any(phrase in normalized for phrase in self._phrases):
            return GuardrailResult(decision=GuardrailDecision.ALLOW)

        return GuardrailResult(
            decision=GuardrailDecision.BLOCK,
            user_message="这个请求可能试图改变系统安全规则，我不能按这个方向继续。",
            findings=[
                GuardrailFinding(
                    category="prompt_injection",
                    severity="high",
                    message="检测到疑似 prompt injection 或 jailbreak 请求。",
                )
            ],
        )


class SecretRequestInterceptor:
    _phrases = (
        "系统提示词",
        "system prompt",
        "api key",
        "apikey",
        "密钥",
        "secret",
        "token",
        "内部规则",
        "规则原文",
    )
    _request_verbs = (
        "给我",
        "输出",
        "显示",
        "告诉",
        "泄露",
        "打印",
        "reveal",
        "show",
        "print",
        "display",
    )

    def inspect(self, content: str, context: GuardrailContext) -> GuardrailResult:
        if context.direction not in {"input", "tool_input"}:
            return GuardrailResult(decision=GuardrailDecision.ALLOW)
        normalized = content.lower()
        has_secret_term = any(phrase in normalized for phrase in self._phrases)
        has_request_verb = any(verb in normalized for verb in self._request_verbs)
        if not (has_secret_term and has_request_verb):
            return GuardrailResult(decision=GuardrailDecision.ALLOW)

        return GuardrailResult(
            decision=GuardrailDecision.BLOCK,
            user_message="这个请求涉及系统规则或敏感信息，我不能按这个方向继续。",
            findings=[
                GuardrailFinding(
                    category="secret_request",
                    severity="high",
                    message="检测到请求泄露系统提示词、内部规则或密钥。",
                )
            ],
        )
