import asyncio
import logging
import os
import re
from pathlib import Path


def write_to_disk(content: str):
    pattern = r'FILENAME:\s*([\w\.-]+\.\w+)'
    file_path = ""
    file_content = ""
    for line in content.split("\n"):
        match = re.search(pattern, line)
        if match:
            write_file(file_content, file_path)
            file_path = match.group(1)
            file_content = ""
        else:
            file_content += f"{line}\n"

    if not write_file(file_content, file_path):
        print(file_content)


def write_file(content: str, path: str) -> bool:
    if content and path:
        path = Path(f"{os.curdir}/{path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.strip())
        logging.info(f"Writing: {path}")
        return True
    else:
        return False


async def generate_patterns(output_path: str, pattern_paths: list[str]):
    for path in pattern_paths:
        if not os.path.exists(path):
            logging.error(f"Template path does not exist: {path}")
            continue
        logging.info(f"Rendering: {path}")
        files = list(Path(path).glob("**/system.md"))
        for file in files:
            cmd = f"gomplate -f {file} -t {path}/templates -o {output_path}/{file.parent.name}/{file.name}"
            res = await asyncio.create_subprocess_shell(cmd,
                                                       stdout=asyncio.subprocess.PIPE,
                                                       stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await res.communicate()
            if res.returncode != 0:
                logging.error(f'[stderr]\n{stderr.decode()}')
