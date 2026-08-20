from media_delivery.infrai_ai import InfraiMediaAI
from media_delivery.models import MediaAsset
from media_delivery.search_workflow import MediaDeliveryWorkflow


def main() -> None:
    workflow = MediaDeliveryWorkflow(InfraiMediaAI())
    job = workflow.ingest(
        MediaAsset(
            asset_id="stream-1042",
            creator_id="maya",
            title="Shipping the season finale",
            transcript=(
                "At 18 minutes, Maya explains how the lighting cue changed the finale. "
                "She then walks through the edit and the audience reaction."
            ),
        )
    )
    result = workflow.search("Where does Maya discuss the finale lighting cue?", limit=1)
    print(job.model_dump_json(indent=2))
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
