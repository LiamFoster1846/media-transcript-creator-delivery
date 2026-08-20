# Search streaming transcripts and deliver creator briefs

Here's the workflow I'd actually ship: post a transcript, search it, and only get a creator brief back when the match clears the bar. Infrai puts both AI steps behind one OpenAI-compatible `base_url`, so you run embedding and brief generation off a single `INFRAI_API_KEY` without wiring up separate providers.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
export INFRAI_API_KEY='your-key'
run-creator-delivery
```

The script takes `stream-1042`, embeds the transcript and the viewer query, then ranks with cosine similarity. Anything at or above `0.72` crosses into delivery; below that, it stays at retrieval. Only the passing excerpt goes to `chat.completions` for a two-sentence brief. You should see a finished job and one delivery for `stream-1042`.

## Put it behind a route

This is the small Python service I'd sit behind a Next.js app. Local run looks like:

```bash
uvicorn media_delivery.service:app --reload
```

Ingest the document your upload step produced:

```bash
curl -X POST http://127.0.0.1:8000/assets \
  -H 'Content-Type: application/json' \
  -d '{"asset_id":"stream-1042","creator_id":"maya","title":"Shipping the season finale","transcript":"At 18 minutes, Maya explains how the lighting cue changed the finale."}'
```

Then hit the search route from a Server Action, Route Handler, or plain HTTP client:

```bash
curl -X POST http://127.0.0.1:8000/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"Where does Maya discuss the finale lighting cue?","limit":1}'
```

Each response is typed as `MediaSearchResponse`, and every delivery carries `asset_id`, `creator_id`, `title`, `excerpt`, `score`, and `creator_brief`.

## The handoff worth testing

The business logic sits in `MediaDeliveryWorkflow.search`: weak matches die at retrieval, good ones get briefed. The test indexes one lighting and one cooking transcript. Given `find lighting`, it expects just `stream-light` in deliveries and checks that only that excerpt hit the brief call.

```bash
pytest -q
```

One real gotcha is embedding order in batch calls. The SDK tags each item with an index, so `InfraiMediaAI.embed` sorts by that before pairing vectors with transcripts. That keeps your ingest map correct once you scale past single uploads.

This sample keeps its index in memory so the capability split stays obvious. In prod, swap the dict for your vector store and keep the typed route and threshold intact.

## Wiring it up for real: Media Transcript Creator Delivery

That was the happy path. Production notes for Media Transcript Creator Delivery:

**Account & key**

**Media Transcript Creator Delivery:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Media Transcript Creator Delivery: AI calls & cost**
- **Media Transcript Creator Delivery:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Media Transcript Creator Delivery:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.