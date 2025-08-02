#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import logging
from typing import Any, Dict, List, Optional
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("webapi-server")

class WebAPIServer:
    def __init__(self):
        self.server = Server("webapi-server")
        self.session = None
        self.setup_handlers()
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
        
    def setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available web API tools."""
            return [
                types.Tool(
                    name="get_request",
                    description="Make a GET request to a URL",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL to make the GET request to"
                            },
                            "headers": {
                                "type": "object",
                                "description": "Optional headers to include in the request",
                                "default": {}
                            },
                            "params": {
                                "type": "object",
                                "description": "Optional query parameters",
                                "default": {}
                            }
                        },
                        "required": ["url"]
                    }
                ),
                types.Tool(
                    name="post_request",
                    description="Make a POST request to a URL",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL to make the POST request to"
                            },
                            "data": {
                                "type": "object",
                                "description": "Data to send in the request body",
                                "default": {}
                            },
                            "headers": {
                                "type": "object",
                                "description": "Optional headers to include in the request",
                                "default": {}
                            },
                            "json_data": {
                                "type": "boolean",
                                "description": "Whether to send data as JSON",
                                "default": True
                            }
                        },
                        "required": ["url"]
                    }
                ),
                types.Tool(
                    name="put_request",
                    description="Make a PUT request to a URL",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL to make the PUT request to"
                            },
                            "data": {
                                "type": "object",
                                "description": "Data to send in the request body",
                                "default": {}
                            },
                            "headers": {
                                "type": "object",
                                "description": "Optional headers to include in the request",
                                "default": {}
                            },
                            "json_data": {
                                "type": "boolean",
                                "description": "Whether to send data as JSON",
                                "default": True
                            }
                        },
                        "required": ["url"]
                    }
                ),
                types.Tool(
                    name="delete_request",
                    description="Make a DELETE request to a URL",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL to make the DELETE request to"
                            },
                            "headers": {
                                "type": "object",
                                "description": "Optional headers to include in the request",
                                "default": {}
                            }
                        },
                        "required": ["url"]
                    }
                ),
                types.Tool(
                    name="fetch_json",
                    description="Fetch and parse JSON data from a URL",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL to fetch JSON data from"
                            },
                            "headers": {
                                "type": "object",
                                "description": "Optional headers to include in the request",
                                "default": {}
                            }
                        },
                        "required": ["url"]
                    }
                ),
                types.Tool(
                    name="check_status",
                    description="Check the HTTP status of a URL",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL to check"
                            }
                        },
                        "required": ["url"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict[str, Any] | None
        ) -> list[types.TextContent]:
            """Handle tool calls."""
            if arguments is None:
                arguments = {}

            try:
                if name == "get_request":
                    result = await self._get_request(
                        arguments.get("url", ""),
                        arguments.get("headers", {}),
                        arguments.get("params", {})
                    )
                    return [types.TextContent(type="text", text=result)]
                
                elif name == "post_request":
                    result = await self._post_request(
                        arguments.get("url", ""),
                        arguments.get("data", {}),
                        arguments.get("headers", {}),
                        arguments.get("json_data", True)
                    )
                    return [types.TextContent(type="text", text=result)]
                
                elif name == "put_request":
                    result = await self._put_request(
                        arguments.get("url", ""),
                        arguments.get("data", {}),
                        arguments.get("headers", {}),
                        arguments.get("json_data", True)
                    )
                    return [types.TextContent(type="text", text=result)]
                
                elif name == "delete_request":
                    result = await self._delete_request(
                        arguments.get("url", ""),
                        arguments.get("headers", {})
                    )
                    return [types.TextContent(type="text", text=result)]
                
                elif name == "fetch_json":
                    result = await self._fetch_json(
                        arguments.get("url", ""),
                        arguments.get("headers", {})
                    )
                    return [types.TextContent(type="text", text=result)]
                
                elif name == "check_status":
                    result = await self._check_status(arguments.get("url", ""))
                    return [types.TextContent(type="text", text=result)]
                
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def _ensure_session(self):
        """Ensure we have an active session."""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def _get_request(self, url: str, headers: Dict[str, str], params: Dict[str, str]) -> str:
        """Make a GET request."""
        if not url:
            return "Error: URL is required"
        
        try:
            await self._ensure_session()
            async with self.session.get(url, headers=headers, params=params) as response:
                status = response.status
                content_type = response.headers.get('content-type', '')
                text = await response.text()
                
                result = f"Status: {status}\n"
                result += f"Content-Type: {content_type}\n"
                result += f"Response Length: {len(text)} characters\n\n"
                
                # Try to format JSON if it's JSON content
                if 'application/json' in content_type:
                    try:
                        json_data = json.loads(text)
                        result += json.dumps(json_data, indent=2)
                    except json.JSONDecodeError:
                        result += text
                else:
                    # Truncate very long responses
                    if len(text) > 2000:
                        result += text[:2000] + "\n... (truncated)"
                    else:
                        result += text
                
                return result
                
        except Exception as e:
            return f"GET Request Error: {str(e)}"

    async def _post_request(self, url: str, data: Dict[str, Any], headers: Dict[str, str], json_data: bool) -> str:
        """Make a POST request."""
        if not url:
            return "Error: URL is required"
        
        try:
            await self._ensure_session()
            
            if json_data:
                headers['Content-Type'] = 'application/json'
                async with self.session.post(url, json=data, headers=headers) as response:
                    return await self._format_response(response)
            else:
                async with self.session.post(url, data=data, headers=headers) as response:
                    return await self._format_response(response)
                    
        except Exception as e:
            return f"POST Request Error: {str(e)}"

    async def _put_request(self, url: str, data: Dict[str, Any], headers: Dict[str, str], json_data: bool) -> str:
        """Make a PUT request."""
        if not url:
            return "Error: URL is required"
        
        try:
            await self._ensure_session()
            
            if json_data:
                headers['Content-Type'] = 'application/json'
                async with self.session.put(url, json=data, headers=headers) as response:
                    return await self._format_response(response)
            else:
                async with self.session.put(url, data=data, headers=headers) as response:
                    return await self._format_response(response)
                    
        except Exception as e:
            return f"PUT Request Error: {str(e)}"

    async def _delete_request(self, url: str, headers: Dict[str, str]) -> str:
        """Make a DELETE request."""
        if not url:
            return "Error: URL is required"
        
        try:
            await self._ensure_session()
            async with self.session.delete(url, headers=headers) as response:
                return await self._format_response(response)
                    
        except Exception as e:
            return f"DELETE Request Error: {str(e)}"

    async def _fetch_json(self, url: str, headers: Dict[str, str]) -> str:
        """Fetch and parse JSON data from a URL."""
        if not url:
            return "Error: URL is required"
        
        try:
            await self._ensure_session()
            async with self.session.get(url, headers=headers) as response:
                if response.status != 200:
                    return f"Error: HTTP {response.status}"
                
                json_data = await response.json()
                return json.dumps(json_data, indent=2)
                    
        except json.JSONDecodeError:
            return "Error: Response is not valid JSON"
        except Exception as e:
            return f"Fetch JSON Error: {str(e)}"

    async def _check_status(self, url: str) -> str:
        """Check the HTTP status of a URL."""
        if not url:
            return "Error: URL is required"
        
        try:
            await self._ensure_session()
            async with self.session.head(url) as response:
                status = response.status
                headers = dict(response.headers)
                
                result = f"URL: {url}\n"
                result += f"Status: {status}\n"
                result += f"Status Text: {response.reason}\n"
                result += f"Server: {headers.get('server', 'Unknown')}\n"
                result += f"Content-Type: {headers.get('content-type', 'Unknown')}\n"
                result += f"Content-Length: {headers.get('content-length', 'Unknown')}\n"
                
                return result
                    
        except Exception as e:
            return f"Status Check Error: {str(e)}"

    async def _format_response(self, response) -> str:
        """Format HTTP response for display."""
        status = response.status
        content_type = response.headers.get('content-type', '')
        text = await response.text()
        
        result = f"Status: {status}\n"
        result += f"Content-Type: {content_type}\n"
        result += f"Response Length: {len(text)} characters\n\n"
        
        # Try to format JSON if it's JSON content
        if 'application/json' in content_type:
            try:
                json_data = json.loads(text)
                result += json.dumps(json_data, indent=2)
            except json.JSONDecodeError:
                result += text
        else:
            # Truncate very long responses
            if len(text) > 2000:
                result += text[:2000] + "\n... (truncated)"
            else:
                result += text
        
        return result

async def main():
    """Main function to run the web API server."""
    async with WebAPIServer() as webapi_server:
        # Run the server using stdin/stdout streams
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await webapi_server.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="webapi-server",
                    server_version="0.1.0",
                    capabilities=webapi_server.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

if __name__ == "__main__":
    asyncio.run(main())