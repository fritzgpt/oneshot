import asyncio
import logging
import os
import select
import sys
import pattern as p
import ai.anthropic_utils as anthropic
import ai.openai_utils as openai
import ai.xai_utils as xai
import generator
from dotenv import load_dotenv
import typer
from typing import List


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

oneshot = typer.Typer(help="Oneshot AI CLI")
shoot = typer.Typer(help="Shoot query against the AI")
pattern = typer.Typer(help="Manage your Fabric pattern files")
list_patterns = typer.Typer(help="List Fabric pattern files")
generate_patterns = typer.Typer(help="Generate Fabric pattern files with gomplate")
oneshot.add_typer(shoot)
oneshot.add_typer(pattern, name="pattern")
pattern.add_typer(list_patterns)
pattern.add_typer(generate_patterns)

@shoot.command()
def shoot(
    pattern_name: str = typer.Option("general", "--pattern", "-p", help="Predefined prompt pattern"),
    pattern_dir: str = typer.Option("", "--pattern-dir", help="Directory where prompt patterns are located", envvar="OS_PATTERN_DIR"),
    env_file: str = typer.Option("", "--env-file", help="Path to file with env vars with API credentials in Fabric format", envvar="OS_ENV_FILE"),
    with_tools: bool = typer.Option(False, "--with-tools", "-t", help="Activate MCP Tool usage"),
    output_to_disk: bool = typer.Option(False, "--output-to-disk", "-o", help="Write LLM output back to disk"),
    model: str = typer.Option(..., "--model", "-m", help="LLM model to use", envvar="DEFAULT_MODEL"),
    prompt: List[str] = typer.Argument("", help="User prompt")
):
    if env_file == "":
        env_file = os.getenv("HOME") + "/.config/fabric/.env"
    if pattern_dir == "":
        pattern_dir = os.getenv("HOME") + "/.config/fabric/patterns"

    stdin = read_stdin_or_continue()
    pattern_content = p.get_pattern(pattern_dir, pattern_name)

    if pattern_content is None:
        return

    if not load_dotenv(env_file):
        logging.error(f"Failed to read: {env_file}")
        return

    logging.info(f"Calling model: {model}")
    logging.info(f"Using pattern: {pattern_name}")

    llm_resp: str = ""
    if model.startswith("claude"):
        llm_resp = anthropic.call_anthropic(model, p.create_complete_pattern(model, pattern_content), p.create_complete_prompt(str(prompt), stdin))
    elif model.startswith("gpt"):
        llm_resp = openai.call_openai(model, p.create_complete_pattern(model, pattern_content), p.create_complete_prompt(str(prompt), stdin))
    elif model.startswith("grok"):
        llm_resp = xai.call_xai(model, p.create_complete_pattern(model, pattern_content), p.create_complete_prompt(str(prompt), stdin))

    if output_to_disk:
        generator.write_to_disk(llm_resp)
    else:
        print(llm_resp)

@list_patterns.command(name="list")
def list_patterns(
        pattern_dir: str = typer.Option("", "--pattern-dir", help="Directory where prompt patterns are located", envvar="OS_PATTERN_DIR"),
):
    if pattern_dir == "":
        pattern_dir = os.getenv("HOME") + "/.config/fabric/patterns"
    logging.info(f"Listing patterns in: {pattern_dir}")
    p.list_patterns(pattern_dir)

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
    asyncio.run(generator.generate_patterns(output_dir, pattern_template_dir))

def read_stdin_or_continue(timeout=0.0):
    """Read STDIN if available, otherwise return None."""
    if select.select([sys.stdin], [], [], timeout)[0]:
        return sys.stdin.read()
    return None

if __name__ == "__main__":
    oneshot()
