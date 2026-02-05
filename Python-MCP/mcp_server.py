from mcp.server import Server, InitializationOptions
import mcp.server.stdio
import mcp.types as types
import asyncio, json, os, sys
import httpx

# Enable stderr output for debugging
def log(msg):
    print(msg, file=sys.stderr, flush=True)

server = Server("knowledge-base-server")
log("Server created")

@server.list_tools()
async def list_tools():
   log("list_tools called")
   return [
       types.Tool(
           name="get_kb",
           description="Fetch KB data",
           inputSchema={"type": "object","properties":{}}
       ),
       types.Tool(
           name="openai_query",
           description="Run a prompt against an OpenAI-compatible endpoint (Azure or OpenAI). Provide 'prompt' and either 'deployment' (Azure) or 'model' (OpenAI).",
           inputSchema={
               "type": "object",
               "properties":{
                   "prompt": {"type":"string"},
                   "deployment": {"type":"string"},
                   "model": {"type":"string"},
                   "max_tokens": {"type":"integer"}
               },
               "required":["prompt"]
           }
       )
   ]

@server.call_tool()
async def call_tool(name, args):
   log(f"call_tool called with name={name} args={args}")
   if name == "get_kb":
       with open("data/kb.json") as f:
           data = json.load(f)
       return [types.TextContent(type="text", text=json.dumps(data))]

   if name == "openai_query":
       prompt = args.get("prompt")
       if not prompt:
           raise ValueError("'prompt' is required for openai_query")
       deployment = args.get("deployment")
       model = args.get("model")
       max_tokens = args.get("max_tokens", 256)

       endpoint = os.environ.get("OPENAI_ENDPOINT")
       api_key = os.environ.get("OPENAI_API_KEY")
       if not api_key:
           raise ValueError("OPENAI_API_KEY must be set in environment variables")

       # Build request depending on Azure vs standard OpenAI
       if deployment:
           # Azure-style endpoint
           url = f"{endpoint.rstrip('/')}/openai/deployments/{deployment}/chat/completions?api-version=2023-10-01"
           headers = {"api-key": api_key, "Content-Type": "application/json"}
       elif model:
           # Standard OpenAI API style
           url = f"{endpoint.rstrip('/')}/v1/chat/completions"
           headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
       else:
           raise ValueError("For Azure provide 'deployment', for OpenAI provide 'model' (or set a deployment)")

       payload = {
           "messages": [{"role": "user", "content": prompt}],
           "max_tokens": max_tokens
       }

       try:
           async with httpx.AsyncClient() as client:
               r = await client.post(url, json=payload, headers=headers, timeout=30.0)
               r.raise_for_status()
               data = r.json()
               # Extract content (support both Azure and OpenAI response shapes)
               try:
                   content = data["choices"][0]["message"]["content"]
               except Exception:
                   content = data.get("choices", [{}])[0].get("text") or json.dumps(data)
               return [types.TextContent(type="text", text=content)]
       except Exception as e:
           log(f"Error calling OpenAI endpoint: {e}")
           raise

   raise ValueError("Unknown tool")
async def main():
   log("main() started")
   async with mcp.server.stdio.stdio_server() as (r, w):
       log("stdio_server started")
       try:
           init_options = InitializationOptions(
               server_name="knowledge-base-server",
               server_version="1.0.0",
               capabilities=types.ServerCapabilities(tools=types.ToolsCapability())
           )
           await server.run(r, w, init_options)
       except Exception as e:
           log(f"Error in server.run: {e}")
           raise
if __name__ == "__main__":
   asyncio.run(main())