from __future__ import annotations

import math
from hashlib import blake2b


class LocalHashEmbeddingService:
    def __init__(self, dimension: int = 64) -> None:
        self.dimension = dimension

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        tokens = _tokenize(text)
        for token in tokens:
            digest = blake2b(token.encode("utf-8"), digest_size=8).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimension
            vector[index] += 1.0
        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]


def _tokenize(text: str) -> list[str]:
    normalized = text.lower()
    ascii_tokens: list[str] = []
    current = ""
    for char in normalized:
        if char.isascii() and char.isalnum():
            current += char
            continue
        if current:
            ascii_tokens.append(current)
            current = ""
    if current:
        ascii_tokens.append(current)

    cjk_chars = [char for char in normalized if "\u4e00" <= char <= "\u9fff"]
    cjk_tokens = cjk_chars[:]
    cjk_tokens.extend("".join(cjk_chars[index : index + 2]) for index in range(max(len(cjk_chars) - 1, 0)))
    return [*ascii_tokens, *_domain_synonyms(normalized), *cjk_tokens]


def _domain_synonyms(text: str) -> list[str]:
    synonyms: list[str] = []
    mapping = {
        "边界": ["boundary", "boundaries", "respectful"],
        "沟通": ["communication", "discuss", "expectations"],
        "隐私": ["privacy", "private", "digital"],
        "手机": ["phone", "digital", "privacy"],
        "回复": ["reply", "response", "expectations"],
        "空间": ["space", "privacy", "boundaries"],
        "尊重": ["respect", "respectful", "boundaries"],
        "暧昧": ["dating", "invitation", "relationship"],
        "邀约": ["invitation", "dating", "ask"],
    }
    for keyword, values in mapping.items():
        if keyword in text:
            synonyms.extend(values)
    return synonyms
