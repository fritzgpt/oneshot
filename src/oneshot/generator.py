import asyncio
import logging
import os
import re
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


def write_to_disk(content: str):
    pattern = r'^\s*FILENAME:\s*(.+?)\s*$'
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
        logging.warning("Writing back to disk failed. Writing to stdout")
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


def render_templates(output_path: str, pattern_paths: list[str], context: dict) -> None:

    output_path = Path(output_path)

    # Initialize Jinja2 environment with the template root
    env = Environment(
        loader=FileSystemLoader([Path(path) for path in pattern_paths]),
        keep_trailing_newline=True,  # Preserve newlines (important for configs)
        trim_blocks=True,
        lstrip_blocks=True
    )

    # Walk through all files
    for path in pattern_paths:
        for root, dirs, files in os.walk(path):
            for filename in files:
                if not filename.endswith('.j2'):
                    continue

                # Calculate relative path from template root
                full_path = Path(root) / filename
                rel_path = full_path.relative_to(path)

                # Render template
                template = env.get_template(str(rel_path))
                rendered = template.render(**context)

                # Write output (strip .j2 extension)
                out_file = output_path / str(rel_path).removesuffix('.j2')
                out_file.parent.mkdir(parents=True, exist_ok=True)
                out_file.write_text(rendered)
                print(f"Rendered: {out_file}")
