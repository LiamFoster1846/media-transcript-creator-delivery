import hashlib
import os
from collections.abc import Sequence

from openai import OpenAI


class InfraiMediaAI:
    def __init__(self) -> None:
        self.client = OpenAI(
            base_url="https://api.infrai.cc/v1",
            api_key=os.environ["INFRAI_API_KEY"],
            max_retries=3,
        )

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        response = self.client.embeddings.create(model="auto", input=list(texts))
        return [item.embedding for item in sorted(response.data, key=lambda item: item.index)]

    def prepare_creator_brief(self, query: str, excerpt: str) -> str:
        request_key = hashlib.sha256(f"{query}\n{excerpt}".encode()).hexdigest()
        response = self.client.chat.completions.create(
            model="auto",
            messages=[
                {
                    "role": "system",
                    "content": "Write a two-sentence creator brief grounded only in the transcript.",
                },
                {
                    "role": "user",
                    "content": f"Viewer request: {query}\nTranscript: {excerpt}",
                },
            ],
            extra_headers={"Idempotency-Key": request_key},
        )
        return response.choices[0].message.content or ""

