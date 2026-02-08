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
       ),
       types.Tool(
           name="ColorPickerHTMLTool",
           description="Interactive HTML color picker tool. Returns an interactive color picker interface.",
           inputSchema={
               "type": "object",
               "properties":{
                   "default_color": {"type":"string", "description":"Default color in hex format (e.g., #FF5733)"}
               }
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

   if name == "ColorPickerHTMLTool":
       default_color = args.get("default_color", "#FF5733")
       
       html_content = f"""
       <div style="font-family: Arial, sans-serif; display: flex; flex-direction: column; align-items: center; gap: 20px; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; min-height: 300px; justify-content: center;">
           <h2 style="color: white; margin: 0;">Interactive Color Picker</h2>
           
           <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
               <label for="colorPicker" style="display: block; margin-bottom: 10px; font-weight: bold; color: #333;">Select a Color:</label>
               <div style="display: flex; gap: 15px; align-items: center;">
                   <input type="color" id="colorPicker" value="{default_color}" style="width: 80px; height: 80px; border: none; cursor: pointer; border-radius: 8px;">
                   <div style="display: flex; flex-direction: column; gap: 10px;">
                       <div style="background: white; padding: 10px; border-radius: 5px; border: 1px solid #ddd;">
                           <label style="font-weight: bold; color: #555;">Hex Value:</label>
                           <input type="text" id="hexValue" value="{default_color}" readonly style="width: 120px; padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-family: monospace; margin-top: 5px; background: #f5f5f5;">
                       </div>
                       <div style="background: white; padding: 10px; border-radius: 5px; border: 1px solid #ddd;">
                           <label style="font-weight: bold; color: #555;">RGB Value:</label>
                           <input type="text" id="rgbValue" value="RGB(255, 87, 51)" readonly style="width: 120px; padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-family: monospace; margin-top: 5px; background: #f5f5f5;">
                       </div>
                   </div>
               </div>
           </div>
           
           <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); width: 100%; max-width: 300px;">
               <p style="margin-top: 0; color: #666; font-size: 14px;">Color Preview:</p>
               <div id="colorPreview" style="width: 100%; height: 120px; background-color: {default_color}; border-radius: 8px; border: 2px solid #ddd; transition: background-color 0.2s ease;"></div>
               <p style="text-align: center; color: #999; font-size: 12px; margin-bottom: 0;">Color updates in real-time</p>
           </div>
       </div>
       
       <script>
           const colorPicker = document.getElementById('colorPicker');
           const hexValue = document.getElementById('hexValue');
           const rgbValue = document.getElementById('rgbValue');
           const colorPreview = document.getElementById('colorPreview');
           
           function hexToRgb(hex) {{
               const r = parseInt(hex.slice(1, 3), 16);
               const g = parseInt(hex.slice(3, 5), 16);
               const b = parseInt(hex.slice(5, 7), 16);
               return `RGB(${{r}}, ${{g}}, ${{b}})`;
           }}
           
           colorPicker.addEventListener('change', function() {{
               hexValue.value = this.value.toUpperCase();
               rgbValue.value = hexToRgb(this.value);
               colorPreview.style.backgroundColor = this.value;
           }});
           
           colorPicker.addEventListener('input', function() {{
               colorPreview.style.backgroundColor = this.value;
           }});
       </script>
       """
       return [types.TextContent(type="text", text=html_content)]
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