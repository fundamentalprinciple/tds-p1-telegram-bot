import json
from datetime import datetime
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "requests.jsonl"


def log_interaction(chat_id, question, response, code=None, stdout=None, stderr=None):
    entry = {
        "chat_id": chat_id,
        "question": question,
        "response": response,
        "code": code,
        "stdout": stdout,
        "stderr": stderr,
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
