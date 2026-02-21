import json
import os

import mcp
import mcp.client
from mcp.client.streamable_http import streamable_http_client
from openai import OpenAI


def call_openai(model: str, pattern: str, prompt: str) -> str:
    client = create_client()
    messages = create_messages(pattern, prompt)
    response = client.responses.create(
        instructions=pattern,
        input=messages,
        model=model,
    )
    return response.output_text

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
            response = client.responses.create(
                tools=available_tools,
                model=model,
                input=input_list
            )

            # make sure tool blocks are part of message
            input_list += response.output

            # Call Tools as indicated by LLM
            final_text: list[str] = []
            for item in response.output:
                if item.type == 'function_call':
                    tool_name = item.name
                    tool_args = json.loads(item.arguments)
                    result = await session.call_tool(tool_name, tool_args)
                    final_text.append(f"Calling tool: {tool_name} with args: {tool_args}")
                    input_list.append({
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": result.content[0].text
                    })

            # Second call to LLM with tool results
            response = client.responses.create(
                input=input_list,
                model=model,
                tools=available_tools
            )

            final_text.append(response.output[0].content[0].text)

            return "\n".join(final_text)


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
