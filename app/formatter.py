import json

def format_reply(answer):
    try:
        answer = json.loads(answer)
    except Exception:
        pass

    return json.dumps(
        {
            "answer": answer,
            "log_url": "https://example.com/run.jsonl",
        },
        ensure_ascii=False,
    )
