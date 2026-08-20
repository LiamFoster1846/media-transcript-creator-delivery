from fastapi import FastAPI

from media_delivery.infrai_ai import InfraiMediaAI
from media_delivery.models import (
    MediaAsset,
    MediaSearchRequest,
    MediaSearchResponse,
    ProcessingJob,
)
from media_delivery.search_workflow import MediaDeliveryWorkflow

app = FastAPI(title="Media brief search")
workflow = MediaDeliveryWorkflow(InfraiMediaAI())


@app.post("/assets", response_model=ProcessingJob)
def ingest_asset(asset: MediaAsset) -> ProcessingJob:
    return workflow.ingest(asset)


@app.post("/search", response_model=MediaSearchResponse)
def search_media(request: MediaSearchRequest) -> MediaSearchResponse:
    return workflow.search(request.query, request.limit)

