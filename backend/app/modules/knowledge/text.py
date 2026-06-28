from __future__ import annotations

import re
from dataclasses import dataclass
from hashlib import sha256
from typing import Any


@dataclass(frozen=True)
class ParsedMarkdown:
    metadata: dict[str, Any]
    content: str


@dataclass(frozen=True)
class ChunkDraft:
    title: str
    title_path: str
    content: str
    metadata: dict[str, Any]


def parse_markdown(markdown: str) -> ParsedMarkdown:
    content = markdown.strip()
    if not content.startswith("---"):
        return ParsedMarkdown(metadata={}, content=content)

    lines = content.splitlines()
    end_index = next((index for index, line in enumerate(lines[1:], start=1) if line == "---"), -1)
    if end_index == -1:
        return ParsedMarkdown(metadata={}, content=content)

    metadata = _parse_frontmatter(lines[1:end_index])
    body = "\n".join(lines[end_index + 1 :]).strip()
    return ParsedMarkdown(metadata=metadata, content=body)


def split_markdown(
    markdown: str,
    metadata: dict[str, Any],
    *,
    chunk_size: int = 700,
    chunk_overlap: int = 100,
    min_chunk_chars: int = 260,
) -> list[ChunkDraft]:
    title = str(metadata.get("title") or _first_heading(markdown) or "未命名知识文档")
    sections = _merge_short_sections(
        _split_sections(markdown, title),
        chunk_size=chunk_size,
        min_chunk_chars=min_chunk_chars,
    )
    chunks: list[ChunkDraft] = []
    for title_path, section_content in sections:
        section_content = section_content.strip()
        if not section_content:
            continue
        for part in _split_long_text(section_content, chunk_size, chunk_overlap):
            enriched_content = (
                f"标题：{title}\n"
                f"章节：{title_path}\n"
                f"正文：\n{part.strip()}"
            )
            chunks.append(
                ChunkDraft(
                    title=title,
                    title_path=title_path,
                    content=enriched_content,
                    metadata=dict(metadata),
                )
            )
    return chunks


def _merge_short_sections(
    sections: list[tuple[str, str]],
    *,
    chunk_size: int,
    min_chunk_chars: int,
) -> list[tuple[str, str]]:
    merged: list[tuple[str, str]] = []
    pending: list[tuple[str, str]] = []

    def flush_pending() -> None:
        if not pending:
            return
        merged.append(_merge_section_group(pending))
        pending.clear()

    for title_path, section_content in sections:
        section_content = section_content.strip()
        if not section_content:
            continue
        if len(section_content) >= min_chunk_chars:
            flush_pending()
            merged.append(_merge_section_group([(title_path, section_content)]))
            continue

        candidate = pending + [(title_path, section_content)]
        _, candidate_content = _merge_section_group(candidate)
        if pending and len(candidate_content) > chunk_size:
            flush_pending()
            pending.append((title_path, section_content))
        else:
            pending.append((title_path, section_content))

    flush_pending()
    return merged


def _merge_section_group(sections: list[tuple[str, str]]) -> tuple[str, str]:
    if len(sections) == 1:
        title_path, section_content = sections[0]
        label = _section_label(title_path)
        return title_path, f"【{label}】\n{section_content.strip()}"

    base_title = sections[0][0].split(" / ", 1)[0]
    labels = [_section_label(title_path) for title_path, _ in sections]
    title_path = f"{base_title} / {' + '.join(labels)}"
    content = "\n\n".join(
        f"【{_section_label(section_path)}】\n{section_content.strip()}"
        for section_path, section_content in sections
    )
    return title_path, content


def _section_label(title_path: str) -> str:
    return title_path.rsplit(" / ", 1)[-1]


def stable_hash(content: str) -> str:
    return sha256(content.encode("utf-8")).hexdigest()


def _parse_frontmatter(lines: list[str]) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    current_key: str | None = None
    for raw_line in lines:
        line = raw_line.rstrip()
        if not line:
            continue
        stripped = line.strip()
        if stripped.startswith("- ") and current_key:
            value = stripped[2:].strip()
            metadata.setdefault(current_key, [])
            if isinstance(metadata[current_key], list):
                metadata[current_key].append(value)
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        current_key = key.strip()
        value = value.strip()
        if value:
            metadata[current_key] = _parse_scalar(value)
        else:
            metadata[current_key] = []
    return metadata


def _parse_scalar(value: str) -> Any:
    if value in {"true", "false"}:
        return value == "true"
    if value.startswith("[") and value.endswith("]"):
        return [item.strip().strip('"').strip("'") for item in value[1:-1].split(",") if item.strip()]
    return value.strip('"').strip("'")


def _first_heading(content: str) -> str | None:
    for line in content.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def _split_sections(content: str, fallback_title: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, list[str]]] = []
    current_path = fallback_title
    heading_stack: list[tuple[int, str]] = [(1, fallback_title)]
    buffer: list[str] = []

    for line in content.splitlines():
        heading_match = re.match(r"^(#{1,4})\s+(.+)$", line)
        if heading_match:
            if buffer:
                sections.append((current_path, buffer))
                buffer = []
            level = len(heading_match.group(1))
            heading = heading_match.group(2).strip()
            heading_stack = [(item_level, item) for item_level, item in heading_stack if item_level < level]
            heading_stack.append((level, heading))
            current_path = " / ".join(item for _, item in heading_stack)
            continue
        buffer.append(line)

    if buffer:
        sections.append((current_path, buffer))

    return [(path, "\n".join(lines)) for path, lines in sections]


def _split_long_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    paragraphs = [paragraph.strip() for paragraph in re.split(r"\n\s*\n", text) if paragraph.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= chunk_size:
            current = candidate
            continue
        if current:
            chunks.append(current)
        if len(paragraph) <= chunk_size:
            current = paragraph
            continue
        chunks.extend(_window_text(paragraph, chunk_size, chunk_overlap))
        current = ""
    if current:
        chunks.append(current)
    return chunks


def _window_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = max(end - chunk_overlap, start + 1)
    return chunks
