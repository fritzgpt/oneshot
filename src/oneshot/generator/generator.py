import asyncio
import logging
import os
import re
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


def write_to_disk(content: str):
    pattern = r'^FILENAME:\s*(.+?)\s*$'
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

def render_jinja2_templates(output_path: str, pattern_paths: list[str]) -> None:


    output_path = Path(output_path)

    # Initialize Jinja2 environment with the template root
    env = Environment(
        loader=FileSystemLoader([Path(path) for path in pattern_paths]),
        keep_trailing_newline=True,  # Preserve newlines (important for configs)
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # files
    context: dict = {
        "recipes": get_files_in_dir(str(Path(os.getenv('OBSIDIAN_BASE_PATH')) / os.getenv('OBSIDIAN_VAULT_PATH_2'))),
        "workouts": get_files_in_dir(str(Path(os.getenv('OBSIDIAN_BASE_PATH')) / os.getenv('OBSIDIAN_VAULT_PATH_1') / "Workouts")),
    }
    # Walk through all files
    for path in pattern_paths:
        logging.info(f"Root path: {path}")
        for root, dirs, files in os.walk(path):
            for filename in files:
                if not filename.endswith('.j2'):
                    logging.info(f"Skipping: {filename}")
                    continue

                # Calculate relative path from template root
                full_path = Path(root) / filename
                rel_path = full_path.relative_to(path)

                # Render template
                template = env.get_template(str(rel_path))
                logging.info(f"Rendering: {template.name}")
                rendered = template.render(**context)

                # Write output (strip .j2 extension)
                out_file = output_path / str(rel_path).removesuffix('.j2')
                out_file.parent.mkdir(parents=True, exist_ok=True)
                out_file.write_text(rendered)
                logging.info(f"Rendered: {out_file}")

def get_files_in_dir(root_dir: str) -> list[str]:
    logging.info(f"Getting files in: {root_dir}")
    res = []
    if not os.path.exists(root_dir):
        logging.error(f"Directory does not exist: {root_dir}")
        return res

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for file in files:
            res.append(os.path.join(root, file))

    return res
