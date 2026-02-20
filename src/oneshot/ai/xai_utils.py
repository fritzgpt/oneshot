import logging
import os

from xai_sdk import Client

from xai_sdk.chat import system, user

def call_xai(model: str, pattern: str, prompt: str):

    client = Client(
        api_key=os.environ.get("GROKAI_API_KEY"),  # This is the default and can be omitted
    )

    messages = [system(pattern), user(prompt)]
    chat = client.chat.create(
        model=model,
        messages=messages
    )
    response = chat.sample()

    return response.content
