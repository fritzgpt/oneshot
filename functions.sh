#!/bin/bash

SCRIPT_DIR="$(dirname -- "${BASH_SOURCE[0]:-${0}}")"

activate_env() {
  source "$SCRIPT_DIR"/.venv/bin/activate
}

ai() {
  activate_env
  python3 "$SCRIPT_DIR"/src/oneshot/oneshot.py shoot "$@"
}

ai_general_prompt() {
  activate_env
  python3 "$SCRIPT_DIR"/src/oneshot/oneshot.py shoot -p general "$@"
}

ai_devops_question() {
  activate_env
  python3 "$SCRIPT_DIR"/src/oneshot/oneshot.py shoot -p devops_quick_question "$@"
}

# generate code single file
ai_code_bash() {
  activate_env
  python3 "$SCRIPT_DIR"/src/oneshot/oneshot.py shoot -p devops_code_bash "$@"
}

ai_code() {
  activate_env
  python3 "$SCRIPT_DIR"/src/oneshot/oneshot.py shoot -p devops_code "$@"
}

# act on multiple files
ai_multi() {
  activate_env
  python3 "$SCRIPT_DIR"/src/oneshot/oneshot.py shoot -p general -o "$@"
}

# generate code multiple files
ai_code_multi() {
  activate_env
  python3 "$SCRIPT_DIR"/src/oneshot/oneshot.py shoot -p devops_code -o "$@"
}

ai_code_multi_bash() {
  activate_env
  python3 "$SCRIPT_DIR"/src/oneshot/oneshot.py shoot -p devops_code_bash -o "$@"
}

ai_code_multi_go() {
  activate_env
  python3 "$SCRIPT_DIR"/src/oneshot/oneshot.py shoot -p devops_code_go -o "$@"
}

ai_code_multi_python() {
  activate_env
  python3 "$SCRIPT_DIR"/src/oneshot/oneshot.py shoot -p devops_code_python -o "$@"
}

# git
ai_git() {
  activate_env
  python3 "$SCRIPT_DIR"/src/oneshot/oneshot.py shoot -p devops_gitcommit "$@"
}

collect() {
  activate_env
  python3 "$SCRIPT_DIR"/src/oneshot/oneshot.py collect "$@"
}

# pattern generator
ai_generate_patterns() {
  activate_env
  python3 "$SCRIPT_DIR"/src/oneshot/oneshot.py pattern generate \
      -o $HOME/.config/fabric/patterns \
      -t $HOME/projects/github/fritzgpt/oneshot/patterns \
      -t $HOME/projects/github/fritzgpt/oneshot/patterns/templates \
      -t $HOME/Sync/FritzSync/patterns \
      -t $HOME/Sync/FritzSync/patterns/templates \
      "$@"
}

# configuration
model_claude() {
  export DEFAULT_MODEL=claude-sonnet-4-5
}

model_claude_opus() {
  export DEFAULT_MODEL=claude-opus-4-5
}

model_claude_haiku() {
  export DEFAULT_MODEL=claude-haiku-4-5
}

model_chatgpt5() {
  export DEFAULT_MODEL=gpt-5.2
}

model_chatgpt5_codex() {
  export DEFAULT_MODEL=gpt-5.1-codex
}

model_grok_code() {
  export DEFAULT_MODEL=grok-code-fast-1
}

model_grok() {
  export DEFAULT_MODEL=grok-4-0709
}

model() {
  echo $DEFAULT_MODEL
}

model_chatgpt5
