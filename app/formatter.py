import json

def json_reply(answer):
    return json.dumps(answer, separators=(",", ":"))
