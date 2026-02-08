from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
import asyncio, json, sys, webbrowser, tempfile, os

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
           print("\n" + "="*50)
           print("Available Tools:")
           print("="*50)
           for i, tool in enumerate(tools.tools, 1):
               print(f"{i}. {tool.name}")
               print(f"   Description: {tool.description}")
           
           # If more than 1 tool, let user pick
           selected_tool = None
           if len(tools.tools) > 1:
               print("\n" + "="*50)
               while True:
                   try:
                       choice = input(f"\nSelect a tool (1-{len(tools.tools)}): ").strip()
                       choice_idx = int(choice) - 1
                       if 0 <= choice_idx < len(tools.tools):
                           selected_tool = tools.tools[choice_idx]
                           break
                       else:
                           print(f"Invalid choice. Please enter a number between 1 and {len(tools.tools)}")
                   except ValueError:
                       print(f"Invalid input. Please enter a number between 1 and {len(tools.tools)}")
           else:
               selected_tool = tools.tools[0]
               print(f"\nAuto-selected tool: {selected_tool.name}")
           
           # Call the selected tool
           log(f"Calling tool: {selected_tool.name}")
           tool_args = {}
           
           # Get tool arguments from user if needed
           if selected_tool.inputSchema.get("properties"):
               print(f"\n{selected_tool.name} requires the following inputs:")
               for prop_name, prop_info in selected_tool.inputSchema.get("properties", {}).items():
                   if prop_name not in selected_tool.inputSchema.get("required", []):
                       prompt_text = f"  {prop_name} (optional, default: {prop_info.get('description', '')}): "
                   else:
                       prompt_text = f"  {prop_name} (required): "
                   user_input = input(prompt_text).strip()
                   if user_input:
                       tool_args[prop_name] = user_input
           
           result = await session.call_tool(selected_tool.name, tool_args)
           log(f"{selected_tool.name} tool returned")
           
           # Check if content is HTML or text
           content_text = result.content[0].text
           
           # Detect HTML by checking if content starts with HTML markers
           if content_text.strip().startswith('<'):
               # Display HTML in browser
               print(f"\n{selected_tool.name} Result:")
               print("="*50)
               print("Opening interactive HTML interface in browser...")
               
               # Create temporary HTML file
               with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                   f.write(content_text)
                   temp_html_path = f.name
               
               # Open in default browser
               webbrowser.open(f'file://{os.path.abspath(temp_html_path)}')
               print(f"HTML interface opened in your default browser.")
               print(f"Temporary file: {temp_html_path}")
               input("\nPress Enter to close the temporary HTML file...")
               try:
                   os.unlink(temp_html_path)
               except:
                   pass
           else:
               # Display text content
               print(f"\n{selected_tool.name} Result:")
               print("="*50)
               print(content_text)

log("Starting asyncio.run(main())")
asyncio.run(main())
log("Completed")