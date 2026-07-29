import pandas as pd
import requests
from pathlib import Path


DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


def download_csv(url: str) -> Path:
    filename = DATA_DIR / url.split("/")[-1]

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    filename.write_bytes(response.content)

    return filename


def load_csv(path: Path):
    return pd.read_csv(path)
