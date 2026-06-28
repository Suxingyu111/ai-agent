from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class VectorPoint:
    point_id: str
    vector: list[float]
    payload: dict[str, Any]


@dataclass(frozen=True)
class VectorSearchHit:
    point_id: str
    score: float
    payload: dict[str, Any]


class KnowledgeVectorStore(Protocol):
    def upsert(self, collection_name: str, points: list[VectorPoint]) -> None: ...

    def delete(self, collection_name: str, *, filters: dict[str, object]) -> None: ...

    def search(
        self,
        collection_name: str,
        query_vector: list[float],
        *,
        limit: int,
        filters: dict[str, object],
    ) -> list[VectorSearchHit]: ...


class InMemoryKnowledgeVectorStore:
    def __init__(self) -> None:
        self._collections: dict[str, dict[str, VectorPoint]] = {}

    def upsert(self, collection_name: str, points: list[VectorPoint]) -> None:
        collection = self._collections.setdefault(collection_name, {})
        for point in points:
            collection[point.point_id] = point

    def delete(self, collection_name: str, *, filters: dict[str, object]) -> None:
        collection = self._collections.get(collection_name)
        if collection is None:
            return
        self._collections[collection_name] = {
            point_id: point
            for point_id, point in collection.items()
            if not _matches_filters(point.payload, filters)
        }

    def search(
        self,
        collection_name: str,
        query_vector: list[float],
        *,
        limit: int,
        filters: dict[str, object],
    ) -> list[VectorSearchHit]:
        hits: list[VectorSearchHit] = []
        for point in self._collections.get(collection_name, {}).values():
            if not _matches_filters(point.payload, filters):
                continue
            hits.append(
                VectorSearchHit(
                    point_id=point.point_id,
                    score=_cosine_similarity(query_vector, point.vector),
                    payload=point.payload,
                )
            )
        return sorted(hits, key=lambda hit: hit.score, reverse=True)[:limit]


class QdrantKnowledgeVectorStore:
    def __init__(self, *, url: str, api_key: str, vector_size: int) -> None:
        from qdrant_client import QdrantClient

        self._client = QdrantClient(url=url, api_key=api_key or None)
        self._vector_size = vector_size

    def upsert(self, collection_name: str, points: list[VectorPoint]) -> None:
        from qdrant_client import models

        self._ensure_collection(collection_name)
        self._ensure_indexes(collection_name)
        self._client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=point.point_id,
                    vector=point.vector,
                    payload=point.payload,
                )
                for point in points
            ],
            wait=True,
        )

    def delete(self, collection_name: str, *, filters: dict[str, object]) -> None:
        from qdrant_client import models

        if not self._client.collection_exists(collection_name):
            return
        query_filter = models.Filter(
            must=[
                models.FieldCondition(key=key, match=models.MatchValue(value=value))
                for key, value in filters.items()
            ]
        )
        self._client.delete(
            collection_name=collection_name,
            points_selector=models.FilterSelector(filter=query_filter),
            wait=True,
        )

    def search(
        self,
        collection_name: str,
        query_vector: list[float],
        *,
        limit: int,
        filters: dict[str, object],
    ) -> list[VectorSearchHit]:
        from qdrant_client import models

        query_filter = models.Filter(
            must=[
                models.FieldCondition(key=key, match=models.MatchValue(value=value))
                for key, value in filters.items()
            ]
        )
        result = self._client.query_points(
            collection_name=collection_name,
            query=query_vector,
            query_filter=query_filter,
            with_payload=True,
            limit=limit,
        )
        return [
            VectorSearchHit(
                point_id=str(point.id),
                score=float(point.score),
                payload=dict(point.payload or {}),
            )
            for point in result.points
        ]

    def _ensure_collection(self, collection_name: str) -> None:
        from qdrant_client import models

        if self._client.collection_exists(collection_name):
            return
        self._client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=self._vector_size,
                distance=models.Distance.COSINE,
            ),
        )

    def _ensure_indexes(self, collection_name: str) -> None:
        from qdrant_client import models

        for field_name in (
            "tenant_id",
            "project_id",
            "agent_key",
            "knowledge_base_id",
            "relationship_stage",
            "primary_category",
            "safety_level",
            "active",
        ):
            schema = (
                models.PayloadSchemaType.BOOL
                if field_name == "active"
                else models.PayloadSchemaType.KEYWORD
            )
            try:
                self._client.create_payload_index(
                    collection_name=collection_name,
                    field_name=field_name,
                    field_schema=schema,
                )
            except Exception:
                continue


class ResilientKnowledgeVectorStore:
    def __init__(self, primary: KnowledgeVectorStore | None = None) -> None:
        self._primary = primary
        self._fallback = InMemoryKnowledgeVectorStore()
        self._primary_available = primary is not None

    def upsert(self, collection_name: str, points: list[VectorPoint]) -> None:
        self._fallback.upsert(collection_name, points)
        if not self._primary_available or self._primary is None:
            return
        try:
            self._primary.upsert(collection_name, points)
        except Exception:
            self._primary_available = False

    def delete(self, collection_name: str, *, filters: dict[str, object]) -> None:
        self._fallback.delete(collection_name, filters=filters)
        if not self._primary_available or self._primary is None:
            return
        try:
            self._primary.delete(collection_name, filters=filters)
        except Exception:
            self._primary_available = False

    def search(
        self,
        collection_name: str,
        query_vector: list[float],
        *,
        limit: int,
        filters: dict[str, object],
    ) -> list[VectorSearchHit]:
        if self._primary_available and self._primary is not None:
            try:
                hits = self._primary.search(
                    collection_name,
                    query_vector,
                    limit=limit,
                    filters=filters,
                )
                if hits:
                    return hits
            except Exception:
                self._primary_available = False
        return self._fallback.search(collection_name, query_vector, limit=limit, filters=filters)


def _matches_filters(payload: dict[str, Any], filters: dict[str, object]) -> bool:
    return all(payload.get(key) == value for key, value in filters.items())


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    dot = sum(a * b for a, b in zip(left, right, strict=False))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)
