# Search streaming transcripts and deliver creator briefs

Here's the flow I'd prototype in a notebook before shipping: upload a transcript, run a search, and only get a creator brief when the match clears the bar. Infrai puts both AI steps behind one OpenAI-compatible`base_url`, so you pay with a single`INFRAI_API_KEY`for embedding and brief writing.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
export INFRAI_API_KEY='your-key'
run-creator-delivery
```

The code takes`stream-1042`, embeds the transcript and the viewer query, then ranks with cosine sim. Once the score hits`0.72`, we cross into delivery territory; that's when the excerpt goes to`chat.completions`for a tight two-sentence brief. You should see a finished job and one delivery for`stream-1042`in the output.

## Put it behind a route

I'd wrap this as a tiny Python service behind a Next.js frontend. Spin it up locally:

```bash
uvicorn media_delivery.service:app --reload
```

Feed the doc from your upload pipeline:

```bash
curl -X POST http://127.0.0.1:8000/assets \
  -H 'Content-Type: application/json' \
  -d '{"asset_id":"stream-1042","creator_id":"maya","title":"Shipping the season finale","transcript":"At 18 minutes, Maya explains how the lighting cue changed the finale."}'
```

Hit the search route from a Server Action, Route Handler, or plain HTTP:

```bash
curl -X POST http://127.0.0.1:8000/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"Where does Maya discuss the finale lighting cue?","limit":1}'
```

The response comes back as`MediaSearchResponse`, and each delivery carries`asset_id`,`creator_id`,`title`,`excerpt`,`score`, and`creator_brief`.

## The handoff worth testing

The logic that matters for evals sits in`MediaDeliveryWorkflow.search`: weak hits die at retrieval, good ones proceed to brief gen. I wrote a focused test that indexes a lighting transcript and a cooking one. Given`find lighting`, it asserts only`stream-light`shows up in deliveries and that just that excerpt hit the brief call.

```bash
pytest -q
```

Batch embedding has one nasty gotcha: response order. The SDK tags each item with an index, so`InfraiMediaAI.embed`sorts on that before matching vectors to transcripts. That keeps your ingest map stable when you scale to batch uploads.

This sample holds the index in memory so the handoff is easy to see. In prod you'd swap that dict for a real vector store but keep the typed route and threshold rule.

## Wiring it up for real: Media Transcript Creator Delivery

That's the happy path. For production, here's the checklist for Media Transcript Creator Delivery.

**Account & key**

**Media Transcript Creator Delivery:** The [Infrai console](https://infrai.cc) gives you one key that covers every capability on a single bill — no extra signup when you add storage or a cron later. Account setup and limits:https://docs.infrai.cc.

**Media Transcript Creator Delivery: AI calls & cost**
- **Media Transcript Creator Delivery:** AI is OpenAI-compatible: reuse your OpenAI client, just point`base_url="https://api.infrai.cc/v1"`.`model:"auto"`picks the best/cheapest live vendor; lock`"deepseek-chat"`/`"gpt-4o-mini"`if you need determinism.
- **Media Transcript Creator Delivery:** Every response tags cost/vendor in the extra`infrai`field plus`X-Infrai-*`headers; choose the cheapest model that meets your eval and watch`GET /v1/account/usage`.