from typing import Literal

try:
    from pydantic import BaseModel, Field
except ModuleNotFoundError:
    from dataclasses import MISSING, dataclass, field

    class BaseModel:
        def __init_subclass__(cls) -> None:
            dataclass(cls)

    def Field(default=MISSING, **_: object):
        if default is MISSING:
            return field()
        return field(default=default)


class MediaAsset(BaseModel):
    asset_id: str = Field(min_length=1)
    creator_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    transcript: str = Field(min_length=1)


class ProcessingJob(BaseModel):
    job_id: str
    asset_id: str
    status: Literal["completed"]


class MediaSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=3, ge=1, le=10)


class CreatorDelivery(BaseModel):
    asset_id: str
    creator_id: str
    title: str
    excerpt: str
    score: float
    creator_brief: str


class MediaSearchResponse(BaseModel):
    deliveries: list[CreatorDelivery]
