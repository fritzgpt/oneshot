{% macro obsidian_files() %}
{% set root = "/home/fritz/Sync/FritzSync/private" %}
{% for path in walk(root) %}
{% if not isdir(path) %}
  {% if path.endswith(".md") %}
    {{ path }}
  {% endif %}
{% endif %}
{% endfor %}
{% endmacro %}