import json
import logging
import os
from pathlib import Path

def get_pattern(path: str, pattern: str) -> str | None:
    pattern_path = f"{path}/{pattern}/system.md"
    try:
        with open(pattern_path) as f:
            return f.read()
    except FileNotFoundError:
        logging.error(f"Error: File '{pattern_path}' not found")
        return None

def list_patterns(path: str) -> str | None:
    files = list(Path(path).glob("**/system.md"))
    res: list[str] = []
    for f in files:
        res.append(f.parent.name)
    res.sort()
    print(json.dumps(res))

def create_complete_prompt(prompt: str, stdin: str) -> str:
    return f"""
        Specific User Request: {prompt}
        {stdin}
    """

def create_complete_pattern(model: str, pattern: str) -> str:
    return f"""
        Current model: {model}
        Current directory: {os.curdir}
        {pattern}
    """
