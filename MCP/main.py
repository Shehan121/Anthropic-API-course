import asyncio
import sys
from dotenv import load_dotenv
from anthropic import AsyncAnthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp_client import MCPClient

load_dotenv()
claude = AsyncAnthropic()  # reads ANTHROPIC_API_KEY from .env
MODEL = "claude-sonnet-5-5"


async def chat_turn(client: MCPClient, messages: list, tools: list) -> str:
    while True:
        response = await claude.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=messages,
            tools=tools,
        )
        messages.append({"role": "assistant", "content": response.content})

        # Claude is done, no more tools needed
        if response.stop_reason != "tool_use":
            return "".join(b.text for b in response.content if b.type == "text")

        # Claude wants tools: run each one through the MCP client
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"  [calling {block.name} with {block.input}]")
                result = await client.call_tool(block.name, block.input)
                text = "\n".join(c.text for c in result.content if c.type == "text")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": text,
                    "is_error": result.isError,
                })

        # send the results back so Claude can continue
        messages.append({"role": "user", "content": tool_results})


async def main():
    server = StdioServerParameters(command=sys.executable, args=["mcp_server.py"])

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            client = MCPClient(session)

            # convert MCP tools into the format the Anthropic API expects
            tools = [
                {
                    "name": t.name,
                    "description": t.description,
                    "input_schema": t.inputSchema,
                }
                for t in await client.list_tools()
            ]

            messages = []
            print("Chat with Claude (type 'quit' to exit)\n")
            while True:
                user_input = await asyncio.to_thread(input, "You: ")
                if user_input.strip().lower() == "quit":
                    break
                messages.append({"role": "user", "content": user_input})
                reply = await chat_turn(client, messages, tools)
                print(f"\nClaude: {reply}\n")


if __name__ == "__main__":
    asyncio.run(main())