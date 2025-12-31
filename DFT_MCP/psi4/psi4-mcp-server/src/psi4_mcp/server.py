"""
Psi4 MCP Server - Main Server Implementation

A complete Model Context Protocol server for Psi4 quantum chemistry.
Provides 124 tools across 17 categories for quantum chemical calculations.

Usage:
    python -m psi4_mcp.server          # stdio transport (default)
    python -m psi4_mcp.server --http   # HTTP transport
"""

import asyncio
import logging
import sys
import os
from typing import Any, Optional
from contextlib import asynccontextmanager

# MCP imports
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool, TextContent, Resource, Prompt,
    GetPromptResult, PromptMessage, PromptArgument
)

# Psi4 initialization
import psi4

# Local imports
from psi4_mcp.tools.core.base_tool import TOOL_REGISTRY, BaseTool
from psi4_mcp.config import ServerConfig, get_config
from psi4_mcp import __version__

# Configure logging to stderr (CRITICAL for stdio transport)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("psi4_mcp")


class Psi4MCPServer:
    """
    Main Psi4 MCP Server class.
    
    Manages tool registration, Psi4 initialization, and request handling.
    """
    
    def __init__(self, config: Optional[ServerConfig] = None):
        self.config = config or get_config()
        self.server = Server("psi4-mcp-server")
        self._psi4_initialized = False
        self._setup_handlers()
        
    def _initialize_psi4(self) -> None:
        """Initialize Psi4 with optimal settings."""
        if self._psi4_initialized:
            return
            
        try:
            # Set scratch directory
            scratch_dir = os.environ.get('PSI_SCRATCH', '/tmp/psi4_scratch')
            os.makedirs(scratch_dir, exist_ok=True)
            psi4.core.IOManager.shared_object().set_default_path(scratch_dir)
            
            # Set memory
            psi4.set_memory(f"{self.config.default_memory} MB")
            
            # Set threads
            psi4.set_num_threads(self.config.default_threads)
            
            # Quiet output (redirect to null)
            psi4.core.set_output_file("/dev/null", False)
            
            # Set default options
            psi4.set_options({
                'basis': 'cc-pvdz',
                'scf_type': 'df',
                'e_convergence': 1e-8,
                'd_convergence': 1e-8,
            })
            
            self._psi4_initialized = True
            logger.info(f"Psi4 {psi4.__version__} initialized successfully")
            logger.info(f"  Memory: {self.config.default_memory} MB")
            logger.info(f"  Threads: {self.config.default_threads}")
            logger.info(f"  Scratch: {scratch_dir}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Psi4: {e}")
            raise
    
    def _setup_handlers(self) -> None:
        """Set up MCP protocol handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List all available tools."""
            self._ensure_tools_loaded()
            tools = []
            for name, tool_cls in TOOL_REGISTRY.items():
                tools.append(Tool(
                    name=name,
                    description=tool_cls.description,
                    inputSchema=tool_cls.get_input_schema()
                ))
            logger.debug(f"Listed {len(tools)} tools")
            return tools
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Execute a tool with given arguments."""
            self._initialize_psi4()
            
            if name not in TOOL_REGISTRY:
                return [TextContent(
                    type="text",
                    text=f"Error: Unknown tool '{name}'. Use list_tools to see available tools."
                )]
            
            tool_cls = TOOL_REGISTRY[name]
            tool = tool_cls()
            
            try:
                logger.info(f"Executing tool: {name}")
                result = tool.run(arguments)
                
                if result.success:
                    response = {
                        "success": True,
                        "message": result.message,
                        "data": result.data
                    }
                    if result.warnings:
                        response["warnings"] = result.warnings
                else:
                    response = {
                        "success": False,
                        "message": result.message,
                        "errors": [e.dict() for e in result.errors] if result.errors else []
                    }
                
                import json
                return [TextContent(type="text", text=json.dumps(response, indent=2, default=str))]
                
            except Exception as e:
                logger.exception(f"Tool execution failed: {name}")
                return [TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}"
                )]
        
        @self.server.list_resources()
        async def list_resources() -> list[Resource]:
            """List available resources."""
            from psi4_mcp.resources import RESOURCE_REGISTRY
            return [
                Resource(
                    uri=f"psi4://{name}",
                    name=name,
                    description=resource.description,
                    mimeType="application/json"
                )
                for name, resource in RESOURCE_REGISTRY.items()
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read a resource by URI."""
            from psi4_mcp.resources import RESOURCE_REGISTRY
            
            # Parse URI: psi4://resource_name or psi4://resource_name/subpath
            if uri.startswith("psi4://"):
                path = uri[7:]
            else:
                path = uri
            
            parts = path.split("/", 1)
            resource_name = parts[0]
            subpath = parts[1] if len(parts) > 1 else None
            
            if resource_name not in RESOURCE_REGISTRY:
                return f"Error: Unknown resource '{resource_name}'"
            
            resource = RESOURCE_REGISTRY[resource_name]
            return resource.get(subpath)
        
        @self.server.list_prompts()
        async def list_prompts() -> list[Prompt]:
            """List available prompt templates."""
            from psi4_mcp.prompts import PROMPT_REGISTRY
            return [
                Prompt(
                    name=name,
                    description=prompt.description,
                    arguments=prompt.arguments
                )
                for name, prompt in PROMPT_REGISTRY.items()
            ]
        
        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: dict) -> GetPromptResult:
            """Get a prompt with filled arguments."""
            from psi4_mcp.prompts import PROMPT_REGISTRY
            
            if name not in PROMPT_REGISTRY:
                return GetPromptResult(
                    description=f"Unknown prompt: {name}",
                    messages=[]
                )
            
            prompt = PROMPT_REGISTRY[name]
            return prompt.render(arguments)
    
    def _ensure_tools_loaded(self) -> None:
        """Ensure all tools are loaded into registry."""
        if len(TOOL_REGISTRY) < 50:  # Should have 100+ tools
            self._load_all_tools()
    
    def _load_all_tools(self) -> None:
        """Import all tool modules to register them."""
        tool_categories = [
            'core', 'vibrational', 'properties', 'spectroscopy',
            'excited_states', 'coupled_cluster', 'perturbation_theory',
            'configuration_interaction', 'mcscf', 'sapt', 'solvation',
            'dft', 'basis_sets', 'analysis', 'composite', 'advanced', 'utilities'
        ]
        
        for category in tool_categories:
            try:
                __import__(f'psi4_mcp.tools.{category}')
                logger.debug(f"Loaded tools from {category}")
            except ImportError as e:
                logger.warning(f"Failed to load {category}: {e}")
        
        logger.info(f"Loaded {len(TOOL_REGISTRY)} tools from {len(tool_categories)} categories")
    
    async def run_stdio(self) -> None:
        """Run server with stdio transport."""
        self._load_all_tools()
        logger.info(f"Starting Psi4 MCP Server v{__version__} (stdio)")
        logger.info(f"Registered {len(TOOL_REGISTRY)} tools")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )
    
    async def run_http(self, host: str = "localhost", port: int = 8080) -> None:
        """Run server with HTTP transport."""
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Route
        import uvicorn
        
        self._load_all_tools()
        logger.info(f"Starting Psi4 MCP Server v{__version__} (HTTP)")
        logger.info(f"Listening on http://{host}:{port}")
        
        sse = SseServerTransport("/messages")
        
        async def handle_sse(request):
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await self.server.run(
                    streams[0], streams[1],
                    self.server.create_initialization_options()
                )
        
        async def handle_messages(request):
            await sse.handle_post_message(request.scope, request.receive, request._send)
        
        app = Starlette(
            routes=[
                Route("/sse", endpoint=handle_sse),
                Route("/messages", endpoint=handle_messages, methods=["POST"]),
            ]
        )
        
        config = uvicorn.Config(app, host=host, port=port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()


def create_server(config: Optional[ServerConfig] = None) -> Psi4MCPServer:
    """Factory function to create server instance."""
    return Psi4MCPServer(config)


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Psi4 MCP Server")
    parser.add_argument("--http", action="store_true", help="Use HTTP transport")
    parser.add_argument("--host", default="localhost", help="HTTP host")
    parser.add_argument("--port", type=int, default=8080, help="HTTP port")
    parser.add_argument("--memory", type=int, default=4000, help="Default memory (MB)")
    parser.add_argument("--threads", type=int, default=4, help="Default threads")
    args = parser.parse_args()
    
    config = ServerConfig(
        default_memory=args.memory,
        default_threads=args.threads
    )
    
    server = create_server(config)
    
    if args.http:
        await server.run_http(args.host, args.port)
    else:
        await server.run_stdio()


if __name__ == "__main__":
    asyncio.run(main())
