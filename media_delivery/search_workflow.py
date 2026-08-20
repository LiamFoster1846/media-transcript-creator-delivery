import math
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from media_delivery.models import (
    CreatorDelivery,
    MediaAsset,
    MediaSearchResponse,
    ProcessingJob,
)


@dataclass(frozen=True)
class IndexedAsset:
    asset: MediaAsset
    embedding: list[float]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("Embedding dimensions must match")
    magnitude = math.sqrt(sum(value * value for value in left)) * math.sqrt(
        sum(value * value for value in right)
    )
    return sum(a * b for a, b in zip(left, right, strict=True)) / magnitude if magnitude else 0.0


class MediaDeliveryWorkflow:
    def __init__(self, ai: Any, relevance_threshold: float = 0.72) -> None:
        self.ai = ai
        self.relevance_threshold = relevance_threshold
        self._assets: dict[str, IndexedAsset] = {}

    def ingest(self, asset: MediaAsset) -> ProcessingJob:
        embedding = self.ai.embed([asset.transcript])[0]
        self._assets[asset.asset_id] = IndexedAsset(asset=asset, embedding=embedding)
        return ProcessingJob(job_id=str(uuid4()), asset_id=asset.asset_id, status="completed")

    def search(self, query: str, limit: int = 3) -> MediaSearchResponse:
        if not self._assets:
            return MediaSearchResponse(deliveries=[])

        query_embedding = self.ai.embed([query])[0]
        ranked = sorted(
            (
                (cosine_similarity(query_embedding, indexed.embedding), indexed.asset)
                for indexed in self._assets.values()
            ),
            key=lambda match: match[0],
            reverse=True,
        )

        deliveries = []
        for score, asset in ranked[:limit]:
            if score < self.relevance_threshold:
                continue
            excerpt = asset.transcript[:600]
            deliveries.append(
                CreatorDelivery(
                    asset_id=asset.asset_id,
                    creator_id=asset.creator_id,
                    title=asset.title,
                    excerpt=excerpt,
                    score=round(score, 4),
                    creator_brief=self.ai.prepare_creator_brief(query, excerpt),
                )
            )
        return MediaSearchResponse(deliveries=deliveries)
