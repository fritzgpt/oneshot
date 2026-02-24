#! python3
import json
import logging
import os
import select
import sys
from typing import List

import typer

from collector import collector as c
from completion import complete
from generator import generator
from pattern import pattern as p
from pattern import render

log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

oneshot = typer.Typer(help="Oneshot AI CLI")
shoot = typer.Typer(help="Shoot query against the AI")
pattern = typer.Typer(help="Manage your Fabric pattern files")
collect = typer.Typer(help="Collect files to be handed to the AI")
list_patterns = typer.Typer(help="List Fabric pattern files")
generate_patterns = typer.Typer(help="Generate Fabric pattern files with gomplate")
oneshot.add_typer(shoot)
oneshot.add_typer(collect)
oneshot.add_typer(pattern, name="pattern")
pattern.add_typer(list_patterns)
pattern.add_typer(generate_patterns)

@shoot.command()
def shoot(
    pattern_name: str = typer.Option("general", "--pattern", "-p", help="Predefined prompt pattern"),
    pattern_dir: str = typer.Option("", "--pattern-dir", help="Directory where prompt patterns are located", envvar="OS_PATTERN_DIR"),
    env_file: str = typer.Option("", "--env-file", help="Path to file with env vars with API credentials in Fabric format", envvar="OS_ENV_FILE"),
    mcp_url: str = typer.Option("", "--mcp-url", "-u", help="MCP server url", envvar="MCP_URL"),
    output_to_disk: bool = typer.Option(False, "--output-to-disk", "-o", help="Write LLM output back to disk"),
    model: str = typer.Option(..., "--model", "-m", help="LLM model to use", envvar="DEFAULT_MODEL"),
    prompt: List[str] = typer.Argument("", help="User prompt")
):
    if env_file == "":
        env_file = os.getenv("HOME") + "/.config/fabric/.env"
    if pattern_dir == "":
        pattern_dir = os.getenv("HOME") + "/.config/fabric/patterns"

    stdin = read_stdin_or_continue()
    prompt_str: str = " ".join(prompt)

    llm_resp = complete(env_file, pattern_dir, pattern_name, stdin, prompt_str, model, mcp_url)

    if output_to_disk:
        generator.write_to_disk(llm_resp)
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(llm_resp)

@collect.command()
def collect(
        collect_dir: str = typer.Argument(".", help="Collect directory or regex"),
        include_hidden: bool = typer.Argument(False, help="Include hidden files in collection"),
        count_tokens: bool = typer.Argument(False, help="Count tokens to estimate costs of AI-call")
):
    c.collect_files(collect_dir, include_hidden, count_tokens)

@list_patterns.command(name="list")
def list_patterns(
        pattern_dir: str = typer.Option("", "--pattern-dir", help="Directory where prompt patterns are located", envvar="OS_PATTERN_DIR"),
):
    pattern_dir = p.get_pattern_dir(pattern_dir)
    logging.info(f"Listing patterns in: {pattern_dir}")
    patterns = p.list_patterns(pattern_dir)
    print(json.dumps(patterns))


@generate_patterns.command(name="generate")
def generate_patterns(
        output_dir: str = typer.Option(
            ...,
            "--output-dir", "-o",
            help="Output directory for generated pattern files"
        ),
        pattern_template_dir: List[str] = typer.Option(
            ...,
            "--template-dir", "-t",
            help="Template directories with Fabric pattern templates to process (can be used multiple times)"
        )
):
    if not os.path.exists(output_dir):
        logging.error(f"Output dir does not exist: {output_dir}")
        return

    render.render_jinja2_templates(output_dir, pattern_template_dir)

def read_stdin_or_continue(timeout=1.0):
    """Read STDIN if available, otherwise return None."""
    if select.select([sys.stdin], [], [], timeout)[0]:
        return sys.stdin.read()
    return None

if __name__ == "__main__":
    oneshot()
