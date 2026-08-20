from media_delivery.models import MediaAsset
from media_delivery.search_workflow import MediaDeliveryWorkflow


class FakeMediaAI:
    def __init__(self) -> None:
        self.brief_requests: list[tuple[str, str]] = []

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = {
            "lighting transcript": [1.0, 0.0],
            "cooking transcript": [0.0, 1.0],
            "find lighting": [0.9, 0.1],
        }
        return [vectors[text] for text in texts]

    def prepare_creator_brief(self, query: str, excerpt: str) -> str:
        self.brief_requests.append((query, excerpt))
        return "Maya explains the finale lighting choice and its effect on the edit."


def test_only_relevant_media_is_handed_to_creator_delivery() -> None:
    ai = FakeMediaAI()
    workflow = MediaDeliveryWorkflow(ai, relevance_threshold=0.8)
    workflow.ingest(
        MediaAsset(
            asset_id="stream-light",
            creator_id="maya",
            title="Finale notes",
            transcript="lighting transcript",
        )
    )
    workflow.ingest(
        MediaAsset(
            asset_id="stream-food",
            creator_id="noah",
            title="Kitchen notes",
            transcript="cooking transcript",
        )
    )

    result = workflow.search("find lighting", limit=2)

    assert [delivery.asset_id for delivery in result.deliveries] == ["stream-light"]
    assert ai.brief_requests == [("find lighting", "lighting transcript")]

