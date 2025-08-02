# Web API MCP Server

A Model Context Protocol (MCP) server that provides tools for making HTTP requests and interacting with web APIs.

## Features

- **GET Requests**: Fetch data from URLs with optional headers and query parameters
- **POST Requests**: Send data to APIs with JSON or form data support
- **PUT Requests**: Update resources with JSON or form data
- **DELETE Requests**: Remove resources from APIs
- **JSON Fetching**: Specialized tool for fetching and parsing JSON data
- **Status Checking**: Check HTTP status and basic information about URLs

## Installation

1. Navigate to the webapi_server directory:
```bash
cd servers/webapi_server
```

2. Install dependencies:
```bash
uv sync
```

## Usage

### Running the Server

```bash
python webapi_server.py
```

Or using uv:
```bash
uv run webapi-server
```

### Available Tools

#### 1. get_request
Make a GET request to a URL.

**Parameters:**
- `url` (required): The URL to request
- `headers` (optional): HTTP headers as key-value pairs
- `params` (optional): Query parameters as key-value pairs

**Example:**
```json
{
  "url": "https://jsonplaceholder.typicode.com/posts/1",
  "headers": {"User-Agent": "MCP-WebAPI-Server"},
  "params": {"format": "json"}
}
```

#### 2. post_request
Make a POST request to a URL.

**Parameters:**
- `url` (required): The URL to request
- `data` (optional): Data to send in request body
- `headers` (optional): HTTP headers as key-value pairs
- `json_data` (optional): Whether to send data as JSON (default: true)

**Example:**
```json
{
  "url": "https://jsonplaceholder.typicode.com/posts",
  "data": {
    "title": "foo",
    "body": "bar",
    "userId": 1
  },
  "headers": {"Content-Type": "application/json"}
}
```

#### 3. put_request
Make a PUT request to a URL.

**Parameters:**
- `url` (required): The URL to request
- `data` (optional): Data to send in request body
- `headers` (optional): HTTP headers as key-value pairs
- `json_data` (optional): Whether to send data as JSON (default: true)

#### 4. delete_request
Make a DELETE request to a URL.

**Parameters:**
- `url` (required): The URL to request
- `headers` (optional): HTTP headers as key-value pairs

#### 5. fetch_json
Fetch and parse JSON data from a URL.

**Parameters:**
- `url` (required): The URL to fetch JSON from
- `headers` (optional): HTTP headers as key-value pairs

**Example:**
```json
{
  "url": "https://api.github.com/users/octocat"
}
```

#### 6. check_status
Check the HTTP status and basic information about a URL.

**Parameters:**
- `url` (required): The URL to check

**Example:**
```json
{
  "url": "https://www.google.com"
}
```

## Configuration with Claude Desktop

Add this server to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "webapi": {
      "command": "python",
      "args": ["/path/to/your/servers/webapi_server/webapi_server.py"]
    }
  }
}
```

Or using uv:

```json
{
  "mcpServers": {
    "webapi": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/your/servers/webapi_server", "webapi-server"]
    }
  }
}
```

## Example Use Cases

1. **API Testing**: Test REST APIs by making different types of HTTP requests
2. **Data Fetching**: Retrieve JSON data from public APIs
3. **Web Scraping**: Fetch web page content (text/HTML)
4. **Health Monitoring**: Check if websites and APIs are responding
5. **API Integration**: Interact with third-party services and APIs

## Error Handling

The server includes comprehensive error handling for:
- Invalid URLs
- Network timeouts
- HTTP errors (4xx, 5xx status codes)
- JSON parsing errors
- Connection issues

## Dependencies

- `aiohttp`: For async HTTP requests
- `mcp`: Model Context Protocol implementation

## License

MIT License