import os
import re
from pathlib import Path


def collect_files(collect_expr: str, include_token: bool, count_tokens: bool) -> None:
    pattern = re.compile(rf"{collect_expr}")
    for root, dirs, files in os.walk("."):

        # remove hidden
        if not include_token:
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            files = [f for f in files if not f.startswith(".")]

        for filename in files:
            full_path = Path(root) / filename
            if pattern.search(str(full_path)):
                print(f"FILENAME: {full_path}")
                print("\n")
                print(Path(full_path).read_text())
