import asyncio
import sys
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client


class MCPClient:
    def __init__(self, session: ClientSession):
        self._session = session

    def session(self) -> ClientSession:
        return self._session

    async def list_tools(self) -> list[types.Tool]:
        result = await self.session().list_tools()
        return result.tools

    async def call_tool(self, tool_name: str, tool_input: dict) -> types.CallToolResult | None:
        return await self.session().call_tool(tool_name, tool_input)


async def main():
    # start your server as a subprocess, using the same Python you're running now
    server = StdioServerParameters(command=sys.executable, args=["mpc_server.py"])

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            client = MCPClient(session)

            print("Tools:")
            for tool in await client.list_tools():
                print(f"  {tool.name}: {tool.description}")

            result = await client.call_tool("read_doc_contents", {"doc_id": "report.pdf"})
            print("\nreport.pdf says:", result.content[0].text)

# implementing prompts in the client
# list_prompt
async def list_prompts(self) -> list[types.Prompt]:
    result = await self.session().list_prompts()
    return result.prompts

# individual prompts
async def get_prompt(self, prompt_name, args: dict[str, str]):
    result = await self.session().get_prompt(prompt_name, args)
    return result.messages

if __name__ == "__main__":
    asyncio.run(main())