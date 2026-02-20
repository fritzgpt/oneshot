import os

import anthropic
import mcp
import mcp.client
from mcp.client.streamable_http import streamable_http_client

MAX_TOKENS=1024

def call_anthropic(model: str, pattern: str, prompt: str) -> str:
    client = anthropic.Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY"),  # This is the default and can be omitted
    )
    message = client.messages.create(
        max_tokens=MAX_TOKENS,
        messages = create_messages(pattern, prompt),
        model=model
    )
    return str(message.content[0].text)

async def call_anthropic_with_tools(mcp_url: str, model: str, pattern: str, prompt: str) -> str:

    async with streamable_http_client(f"{mcp_url}/mcp") as (
            read_stream,
            write_stream,
            _,
    ):
        client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY"),  # This is the default and can be omitted
        )

        # Create a session using the client streams
        async with mcp.ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()

            response = await session.list_tools()
            available_tools = []
            for tool in response.tools:
                available_tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                })
            messages = create_messages(pattern, prompt)
            response = client.messages.create(
                model=model,
                max_tokens=MAX_TOKENS,
                messages=messages,
                tools=available_tools
            )
            # make sure tool blocks are part of message
            messages.append({
                "role": "assistant",
                "content": response.content
            })

            # Call Tools as indicated by LLM
            final_text: list[str] = []
            tool_result_contents = []
            for content in response.content:
                if content.type == 'tool_use':
                    tool_name = content.name
                    tool_args = content.input

                    # Execute tool call
                    result = await session.call_tool(tool_name, tool_args)
                    final_text.append(f"Calling tool: {tool_name} with args: {tool_args}")
                    content = {
                        "type": "tool_result",
                        "tool_use_id": content.id,
                        "content": result.content
                    }
                    tool_result_contents.append(content)

            messages.append({
                "role": "user",
                "content": tool_result_contents
            })

            # Second call to LLM with tool results
            response = client.messages.create(
                model=model,
                max_tokens=MAX_TOKENS,
                messages=messages,
                tools=available_tools
            )

            final_text.append(response.content[0].text)

            return "\n".join(final_text)

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
