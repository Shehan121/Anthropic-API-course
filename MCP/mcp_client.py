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


asyncio.run(main())