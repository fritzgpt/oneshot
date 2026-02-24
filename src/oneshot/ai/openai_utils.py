import os

import mcp
import mcp.client
from mcp.client.streamable_http import streamable_http_client
from openai import OpenAI


def call_openai(model: str, pattern: str, prompt: str) -> str:
    client = create_client()
    messages = create_messages(pattern, prompt)
    response = client.chat.completions.create(
        messages=messages,
        model=model,
    )
    return response.choices[0].message.content

async def call_openai_with_tools(mcp_url: str, model: str, pattern: str, prompt: str) -> str:
    async with streamable_http_client(f"{mcp_url}/mcp") as (
            read_stream,
            write_stream,
            _,
    ):
        client = create_client()

        # Create a session using the client streams
        async with mcp.ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()

            input_list = create_messages(pattern, prompt)
            available_tools = await mcp_to_openai_tools(session)
            response = client.completions.create(
                model=model,
                prompt=prompt
            )

            return "\n".join(response)


def create_client() -> OpenAI:
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    return client


def create_messages(pattern: str, prompt: str):
    return [
        {
            "role": "assistant",
            "content": pattern,
        },
        {
            "role": "user",
            "content": prompt,
        }
    ]


async def mcp_to_openai_tools(session: mcp.ClientSession) -> list:
    """Convert MCP tools to OpenAI function format."""
    mcp_tools = await session.list_tools()
    openai_tools = []
    for tool in mcp_tools.tools:
        openai_tools.append({
            "type": "function",
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.inputSchema
        })
    return openai_tools
