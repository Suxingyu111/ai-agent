from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Protocol
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class UrlFetchResult:
    url: str
    html: str


class UrlFetcher(Protocol):
    def fetch(self, url: str) -> UrlFetchResult: ...


class StandardLibraryUrlFetcher:
    def __init__(self, timeout_seconds: int = 15) -> None:
        self._timeout_seconds = timeout_seconds

    def fetch(self, url: str) -> UrlFetchResult:
        request = Request(
            url,
            headers={
                "User-Agent": "ai-agent-knowledge-collector/0.1",
                "Accept": "text/html,application/xhtml+xml",
            },
        )
        with urlopen(request, timeout=self._timeout_seconds) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            content = response.read().decode(charset, errors="replace")
        return UrlFetchResult(url=url, html=content)


@dataclass(frozen=True)
class KnowledgeCardOptions:
    title: str | None = None
    relationship_stage: str | None = None
    primary_category: str | None = None
    topic_tags: list[str] = field(default_factory=list)
    intent_tags: list[str] = field(default_factory=list)
    safety_level: str = "normal"
    max_chars: int = 6000


class HtmlKnowledgeCardBuilder:
    def build_markdown(
        self,
        *,
        source_url: str,
        html_content: str,
        options: KnowledgeCardOptions,
    ) -> str:
        parsed = _ReadableHtmlParser()
        parsed.feed(html_content)
        extracted = parsed.result()
        title = options.title or extracted.title or "未命名网页资料"
        body_text = _truncate_text("\n\n".join(extracted.blocks), options.max_chars)
        metadata = {
            "title": title,
            "relationship_stage": options.relationship_stage or _infer_relationship_stage(body_text),
            "primary_category": options.primary_category or _infer_primary_category(body_text),
            "topic_tags": options.topic_tags or _infer_topic_tags(body_text),
            "intent_tags": options.intent_tags or ["explain"],
            "safety_level": options.safety_level,
            "source_urls": [source_url],
        }
        return (
            f"{_frontmatter(metadata)}\n\n"
            f"# {title}\n\n"
            "## 资料摘要\n\n"
            f"{extracted.description or _first_sentence(body_text) or '原始网页未提供摘要。'}\n\n"
            "## 关键内容\n\n"
            f"{body_text}\n\n"
            "## 来源\n\n"
            f"- {source_url}\n"
        )


@dataclass(frozen=True)
class ExtractedHtml:
    title: str
    description: str
    blocks: list[str]


class _ReadableHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skip_depth = 0
        self._active_block: str | None = None
        self._buffer: list[str] = []
        self._blocks: list[str] = []
        self._title_buffer: list[str] = []
        self._in_title = False
        self._description = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "nav", "header", "footer", "aside", "form"}:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if tag == "title":
            self._in_title = True
            return
        if tag == "meta":
            attributes = {key.lower(): value or "" for key, value in attrs}
            if attributes.get("name", "").lower() == "description":
                self._description = _normalize_text(attributes.get("content", ""))
            return
        if tag in {"h1", "h2", "h3", "p", "li"}:
            self._flush_block()
            self._active_block = tag

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "nav", "header", "footer", "aside", "form"}:
            self._skip_depth = max(self._skip_depth - 1, 0)
            return
        if self._skip_depth:
            return
        if tag == "title":
            self._in_title = False
            return
        if tag == self._active_block:
            self._flush_block()

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        if self._in_title:
            self._title_buffer.append(data)
            return
        if self._active_block:
            self._buffer.append(data)

    def result(self) -> ExtractedHtml:
        self._flush_block()
        title = _normalize_text(" ".join(self._title_buffer))
        blocks = _dedupe_blocks(self._blocks)
        return ExtractedHtml(title=title, description=self._description, blocks=blocks)

    def _flush_block(self) -> None:
        if not self._active_block:
            return
        text = _normalize_text(" ".join(self._buffer))
        self._buffer = []
        prefix = ""
        if self._active_block == "h1":
            prefix = "### "
        elif self._active_block in {"h2", "h3"}:
            prefix = "#### "
        elif self._active_block == "li":
            prefix = "- "
        if len(text) >= 12:
            self._blocks.append(f"{prefix}{text}")
        self._active_block = None


def _frontmatter(metadata: dict[str, object]) -> str:
    lines = ["---"]
    for key, value in metadata.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines)


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def _dedupe_blocks(blocks: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for block in blocks:
        normalized = block.lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        result.append(block)
    return result


def _truncate_text(value: str, max_chars: int) -> str:
    if len(value) <= max_chars:
        return value
    return value[:max_chars].rsplit("\n\n", 1)[0].strip() or value[:max_chars].strip()


def _first_sentence(value: str) -> str:
    match = re.search(r"[^。.!?！？]+[。.!?！？]", value)
    return match.group(0).strip() if match else value[:120].strip()


def _infer_relationship_stage(value: str) -> str:
    if "暧昧" in value:
        return "ambiguous"
    if "marriage" in value.lower() or "婚姻" in value:
        return "marriage"
    if "breakup" in value.lower() or "分手" in value:
        return "breakup"
    return "general"


def _infer_primary_category(value: str) -> str:
    lowered = value.lower()
    if "boundary" in lowered or "边界" in value or "privacy" in lowered:
        return "safety_boundaries"
    if "conflict" in lowered or "冲突" in value:
        return "conflict_repair"
    if "breakup" in lowered or "分手" in value:
        return "breakup_recovery"
    return "relationship"


def _infer_topic_tags(value: str) -> list[str]:
    lowered = value.lower()
    tags: list[str] = []
    if "boundary" in lowered or "边界" in value:
        tags.append("boundaries")
    if "communication" in lowered or "沟通" in value:
        tags.append("communication")
    if "privacy" in lowered or "隐私" in value:
        tags.append("digital_boundaries")
    return tags or ["relationship"]
