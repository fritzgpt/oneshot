import logging
import os
from pathlib import Path
from completion import complete

from flask import Flask, request

# curl localhost:8080/patterns/names
# curl localhost:8080/chat
# const prompt: [{
#         userInput: text,
#         model,
#         contextName: "general_context.md",
#         patternName: pattern,
#         MARKDOWNFile: obs
# }],
# curl -X POST localhost:8080/patterns/generate
# curl localhost:8080/MARKDOWN/files | jq
# curl -X localhost:8080/telegram/send
# curl -X localhost:8080/MARKDOWN/store

from pattern import pattern
from pattern import render
from markdown import markdown
from social import telegram

log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = Flask(__name__)

@app.route("/completion", methods=["POST"])
def completion():
    data = request.get_json()
    env_file = f"{os.getenv("HOME")}/{os.getenv("FABRIC_CONFIG_HOME")}/.env"
    pattern_dir = f"{os.getenv("HOME")}/{os.getenv("FABRIC_CONFIG_HOME")}/patterns"
    base_path = os.getenv("MARKDOWN_BASE_PATH")
    markdown_file = ""
    with os.read(f"{base_path}/{data.markdownFile}") as f:
        markdown_file = f
    return complete(env_file, pattern_dir, data.patternName, markdown_file, data.userInput, data.model, os.getenv("MCP_URL"))

@app.route("/patterns/names")
def pattern_names():
    pattern_dir = pattern.get_pattern_dir("")
    logging.info(f"Listing patterns in: {pattern_dir}")
    patterns = pattern.list_patterns(pattern_dir)
    return patterns

@app.route("/patterns/generate", methods=["POST"])
def generate_patterns():
    output_dir = Path(os.getenv("FABRIC_CONFIG_HOME")) / "patterns"
    pattern_dir = os.getenv("FABRIC_PATTERN_PATH")
    pattern_template_dir = Path(os.getenv("FABRIC_PATTERN_PATH")) / "templates"
    render.render_jinja2_templates(str(output_dir), [pattern_dir, str(pattern_template_dir)])
    return "OK"

@app.route("/markdown/paths")
def markdown_paths():
    paths: list[str] = []
    count: int = 1
    base_path = os.getenv("MARKDOWN_BASE_PATH")
    while os.getenv(f"MARKDOWN_VAULT_PATH_{count}"):
        path = os.getenv(f"MARKDOWN_VAULT_PATH_{count}")
        paths.extend(markdown.list_files(f"{base_path}/{path}"))
        count = count + 1
    # trim base_path
    paths = [ path.replace(f"{base_path}/", "") for path in paths]
    return paths

@app.route("/markdown/store", methods=["POST"])
def markdown_store():
    path = request.args.get("path")
    data = request.get_data()
    base_path = os.getenv("MARKDOWN_BASE_PATH")
    with open(f"{base_path}/{path}") as f:
        f.write(data)

@app.route("/telegram/send", methods=["POST"])
def markdown_store():
    data = request.get_data()
    telegram.send(data, os.getenv("TELEGRAM_BOT_TOKEN"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082, debug=True)
