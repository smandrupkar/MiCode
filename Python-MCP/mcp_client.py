from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
import asyncio, json, sys

def log(msg):
    print(f"[CLIENT] {msg}", file=sys.stderr, flush=True)

async def main():
   log("main() started")
   params = StdioServerParameters(command="python", args=["mcp_server.py"])
   log(f"Created params: {params}")
   
   async with stdio_client(params) as (read_stream, write_stream):
       log("stdio_client context manager entered")
       async with ClientSession(read_stream, write_stream) as session:
           log("ClientSession context manager entered")
           log("Calling session.initialize()")
           await session.initialize()
           log("session.initialize() completed")
           tools = await session.list_tools()
           log(f"Got {len(tools.tools)} tools")
           print("Available tools:")
           for tool in tools.tools:
               print(f"  - {tool.name}: {tool.description}")
           
           # Test calling the get_kb tool
           log("Calling get_kb tool")
           result = await session.call_tool("get_kb", {})
           #result = await session.call_tool("openai_query", {"prompt": "What is the purpose of MCP?", "model": "gpt-4", "max_tokens": 100})
           log("get_kb tool returned")
           print("\nKnowledge Base Content:")
           print(result.content[0].text)

log("Starting asyncio.run(main())")
asyncio.run(main())
log("Completed")