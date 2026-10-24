import json
import importlib
import asyncio
import dotenv
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

# Get the absolute path to the directory where server.py is located
BASE_DIR = Path(__file__).parent.resolve()

# Load environment variables globally for all providers
dotenv.load_dotenv(dotenv_path=BASE_DIR / ".env", override=True)

def load_config(config_filename="config.json"):
    config_path = BASE_DIR / config_filename
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

async def main():
    config = load_config()
    
    app = Server("tiny-mcp-server")
    
    providers = {}
    tools_list = []
    tool_registry = {}  # Maps full_tool_name → (namespace, method) for robust lookup
    
    for server_cfg in config.get("servers", []):
        mcp_name = server_cfg["mcp_name"]
        class_path = server_cfg["class"]
        
        module_name, class_name = class_path.rsplit(".", 1)
        mod = importlib.import_module(module_name)
        cls = getattr(mod, class_name)
        
        provider_instance = cls()
        providers[mcp_name] = provider_instance
        
        for tool_cfg in server_cfg.get("tools", []):
            tool_name = tool_cfg["name"]
            full_tool_name = f"{mcp_name}_{tool_name}"
            
            # Register the mapping: full_name → (namespace, method)
            tool_registry[full_tool_name] = (mcp_name, tool_name)
            
            tool_obj = types.Tool(
                name=full_tool_name,
                description=tool_cfg.get("description", ""),
                inputSchema=tool_cfg.get("inputSchema", {"type": "object", "properties": {}})
            )
            tools_list.append(tool_obj)
            
    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        return tools_list
        
    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        # Use lookup mapping for robust name resolution (handles namespaces with underscores)
        if name not in tool_registry:
            raise ValueError(f"Unknown tool: {name}")
            
        namespace, tool_method = tool_registry[name]
        
        provider = providers[namespace]
        
        try:
            params = {"name": tool_method, "arguments": arguments}
            result = provider._rpc_tool_execute(params)
            
            if isinstance(result, dict) and result.get("status") == "error":
                is_error = True
                text = f"Error: {result.get('message', 'Unknown error')}"
                if "error" in result:
                    text = f"Error: {result['error']}"
                return [types.TextContent(type="text", text=text)]
                
            if not isinstance(result, str):
                result = json.dumps(result, indent=2, ensure_ascii=False)
                
            return [types.TextContent(type="text", text=result)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Tool Execution Exception: {str(e)}")]

    # Start stdio MCP server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
