import logging
import os.path
from pathlib import Path

def list_files(path: str) -> list[str]:
    if not os.path.exists(path):
        logging.error(f"Path not found: {path}")
        return []

    logging.info(f"Listing files in: {path}")
    files = list(Path(path).glob("**/*.md"))
    res: list[str] = []
    for f in files:
        if not ".trash" in str(f):
            res.append(str(f))
    res.sort()
    return res
