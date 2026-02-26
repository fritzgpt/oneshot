import logging
import os
from pathlib import Path
import ai_utils

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
    env_file = os.getenv("OS_CONFIG_ENV_FILE")
    pattern_dir = os.getenv("OS_CONFIG_PATTERN_DIR")
    base_path = os.getenv("OS_MARKDOWN_BASE_DIR")
    markdown_file = ""
    markdown_path = data["markdown"]
    if markdown_path:
        markdown_file = Path(f"{base_path}/{markdown_path}").read_text()
    return ai_utils.complete(env_file, pattern_dir, data["pattern"], markdown_file, data["message"], data["model"], os.getenv("MCP_URL"))

@app.route("/patterns/names")
def pattern_names():
    pattern_dir = os.getenv("OS_CONFIG_PATTERN_DIR")
    logging.info(f"Listing patterns in: {pattern_dir}")
    patterns = pattern.list_patterns(pattern_dir)
    return patterns

@app.route("/models/names")
def model_names(
):
    env_file = os.getenv("OS_CONFIG_ENV_FILE")
    return ai_utils.list_models(env_file)

@app.route("/patterns/generate", methods=["POST"])
def generate_patterns():
    output_dir = os.getenv("OS_CONFIG_PATTERN_DIR")
    pattern_dir = os.getenv("OS_PATTERN_TEMPLATE_DIR")
    pattern_template_dir = Path(os.getenv("OS_PATTERN_TEMPLATE_DIR")) / "templates"
    render.render_jinja2_templates(output_dir, [pattern_dir, str(pattern_template_dir)])
    return "OK"

@app.route("/markdown/paths")
def markdown_paths():
    paths: list[str] = []
    count: int = 1
    base_path = os.getenv("OS_MARKDOWN_BASE_DIR")
    while os.getenv(f"OS_MARKDOWN_VAULT_DIR_{count}"):
        path = os.getenv(f"OS_MARKDOWN_VAULT_DIR_{count}")
        paths.extend(markdown.list_files(f"{base_path}/{path}"))
        count = count + 1
    # trim base_path
    paths = [ path.replace(f"{base_path}/", "") for path in paths]
    return paths

@app.route("/markdown/store", methods=["POST"])
def markdown_store():
    data = request.get_json()
    path = data["path"]
    md = data["markdown"]
    base_path = os.getenv("OS_MARKDOWN_BASE_DIR")
    with open(f"{base_path}/{path}") as f:
        f.write(md)

@app.route("/telegram/send", methods=["POST"])
def telegram_send():
    data = request.get_json()
    telegram.send(data["message"], os.getenv("TELEGRAM_BOT_TOKEN"))

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082, debug=True)
