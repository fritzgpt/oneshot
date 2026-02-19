import os

from anthropic import Anthropic

MAX_TOKENS=1024


def call_anthropic(model: str, pattern: str, prompt: str):
    client = Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY"),  # This is the default and can be omitted
    )
    message = client.messages.create(
        max_tokens=MAX_TOKENS,
        messages=[
            {
                "role": "assistant",
                "content": pattern,
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=model,
    )
    return str(message.content[0].text)
