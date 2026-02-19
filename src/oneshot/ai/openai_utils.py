import os

from openai import OpenAI



def call_openai(model: str, pattern: str, prompt: str):
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    response = client.responses.create(
        instructions=pattern,
        input=prompt,
        model=model,
    )
    return response.output_text
