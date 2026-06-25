import re

from app.agent_kernel.guardrails.contracts import (
    GuardrailContext,
    GuardrailDecision,
    GuardrailFinding,
    GuardrailResult,
)

PHONE_RE = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
SECRET_VALUE_RE = re.compile(r"(?i)sk-[A-Za-z0-9][A-Za-z0-9_-]{6,}")
LABELED_SECRET_RE = re.compile(
    r"(?i)((?:api[_-]?key|secret[_-]?key|token)\s*(?:是|=|:)\s*)[A-Za-z0-9._:/+=-]+"
)


class PiiAndSecretRedactionInterceptor:
    def inspect(self, content: str, context: GuardrailContext) -> GuardrailResult:
        sanitized = content
        findings: list[GuardrailFinding] = []

        sanitized, phone_count = PHONE_RE.subn("[已脱敏手机号]", sanitized)
        if phone_count:
            findings.append(
                GuardrailFinding(
                    category="pii",
                    severity="medium",
                    message="内容包含手机号，已脱敏。",
                )
            )

        sanitized, email_count = EMAIL_RE.subn("[已脱敏邮箱]", sanitized)
        if email_count:
            findings.append(
                GuardrailFinding(
                    category="pii",
                    severity="medium",
                    message="内容包含邮箱，已脱敏。",
                )
            )

        sanitized, labeled_secret_count = LABELED_SECRET_RE.subn(r"\1[已脱敏密钥]", sanitized)
        sanitized, secret_value_count = SECRET_VALUE_RE.subn("[已脱敏密钥]", sanitized)
        secret_count = labeled_secret_count + secret_value_count
        if secret_count:
            findings.append(
                GuardrailFinding(
                    category="secret",
                    severity="high",
                    message="内容包含疑似密钥或 token，已脱敏。",
                )
            )

        if not findings:
            return GuardrailResult(decision=GuardrailDecision.ALLOW)

        return GuardrailResult(
            decision=GuardrailDecision.REDACT,
            sanitized_content=sanitized,
            findings=findings,
        )
