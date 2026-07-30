import requests
import pandas as pd
from pathlib import Path


def download(url: str, directory="data"):
    Path(directory).mkdir(exist_ok=True)

    filename = url.split("/")[-1]
    path = Path(directory) / filename

    r = requests.get(url, timeout=30)
    r.raise_for_status()

    path.write_bytes(r.content)
    return str(path)


def load(path: str):
    if path.endswith(".csv"):
        return pd.read_csv(path)

    if path.endswith(".json"):
        return pd.read_json(path)

    if path.endswith(".xlsx"):
        return pd.read_excel(path)

    raise ValueError(f"Unsupported file type: {path}")
