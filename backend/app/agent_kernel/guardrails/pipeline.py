from app.agent_kernel.guardrails.contracts import (
    GuardrailContext,
    GuardrailDecision,
    GuardrailFinding,
    GuardrailInterceptor,
    GuardrailResult,
)
from app.agent_kernel.guardrails.pii import PiiAndSecretRedactionInterceptor
from app.agent_kernel.guardrails.prompt_injection import (
    PromptInjectionInterceptor,
    SecretRequestInterceptor,
)
from app.agent_kernel.guardrails.safety import (
    SystemPromptLeakageInterceptor,
    UnsafeControlOrHarassmentInterceptor,
)

DEFAULT_BLOCK_MESSAGE = "这个请求可能涉及安全或隐私风险，我不能按这个方向继续。"


class GuardrailPipeline:
    def __init__(self, interceptors: list[GuardrailInterceptor]) -> None:
        self._interceptors = interceptors

    def inspect(self, content: str, context: GuardrailContext) -> GuardrailResult:
        current_content = content
        all_findings: list[GuardrailFinding] = []
        final_decision = GuardrailDecision.ALLOW
        block_message: str | None = None

        for interceptor in self._interceptors:
            result = interceptor.inspect(current_content, context)
            if result.findings:
                all_findings.extend(result.findings)
            if result.decision == GuardrailDecision.BLOCK:
                final_decision = GuardrailDecision.BLOCK
                block_message = block_message or result.user_message
                continue
            if result.decision in {GuardrailDecision.REDACT, GuardrailDecision.REWRITE}:
                if final_decision != GuardrailDecision.BLOCK:
                    final_decision = result.decision
                if result.sanitized_content is not None:
                    current_content = result.sanitized_content

        if final_decision == GuardrailDecision.BLOCK:
            return GuardrailResult(
                decision=GuardrailDecision.BLOCK,
                sanitized_content=current_content if current_content != content else None,
                user_message=block_message or DEFAULT_BLOCK_MESSAGE,
                findings=all_findings,
            )

        if final_decision == GuardrailDecision.ALLOW:
            return GuardrailResult(decision=GuardrailDecision.ALLOW, sanitized_content=content)

        return GuardrailResult(
            decision=final_decision,
            sanitized_content=current_content,
            findings=all_findings,
        )


def build_default_guardrail_pipeline() -> GuardrailPipeline:
    return GuardrailPipeline(
        interceptors=[
            PromptInjectionInterceptor(),
            SecretRequestInterceptor(),
            SystemPromptLeakageInterceptor(),
            UnsafeControlOrHarassmentInterceptor(),
            PiiAndSecretRedactionInterceptor(),
        ]
    )
