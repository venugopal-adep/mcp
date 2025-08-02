# Terminal Server MCP

A simple MCP server that lets you run terminal commands inside your workspace, designed for integration with Claude Desktop.

## Features

- Run shell commands securely in your workspace directory.
- Easy integration with Claude Desktop via MCP protocol.

---

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (fast Python package manager)
- Claude Desktop (for MCP integration)

---

## Setup Instructions

### 1. Install `uv`

```sh
pip install uv
```
Or, for faster installation:
```sh
curl -Ls https://astral.sh/uv/install.sh | sh
```

### 2. Initialize `uv` and Create Virtual Environment

Navigate to the project directory:

```sh
cd servers/terminal_server
```

Create a virtual environment:

```sh
uv venv .venv
```

Activate the virtual environment:

- **macOS/Linux:**
  ```sh
  source .venv/bin/activate
  ```
- **Windows:**
  ```sh
  .venv\Scripts\activate
  ```

### 3. Install Dependencies

```sh
uv pip install -r requirements.txt
```
Or, if using `pyproject.toml`:
```sh
uv pip install .
```

---

### 4. Download Claude Desktop

Get Claude Desktop from [Anthropic's official site](https://www.anthropic.com/claude-desktop) and install it.

---

### 5. Configure Claude Desktop for MCP

Edit your Claude Desktop config file (usually at  
`~/Library/Application Support/Claude/claude_desktop_config.json`) and add:

```json
{
    "mcpServers": {
        "terminal": {
            "command": "/opt/anaconda3/bin/uv",
            "args": [
                "--directory", "/Users/venugopal.adep/mcp/servers/terminal_server",
                "run", 
                "terminal_server.py"
            ]
        }
    }
}
```

---

## Usage

1. **Start Claude Desktop**  
   Launch Claude Desktop. It will automatically start the MCP terminal server.

2. **Run Terminal Commands**  
   Use Claude Desktop's interface to send terminal commands.  
   The server will execute them in your workspace directory (`~/mcp/workspace`).

3. **Example Command**  
   To list files in your workspace:
   ```
   ls
   ```

---

## Project Structure

- `terminal_server.py` — MCP server implementation
- `hello.py` — Example script
- `.venv` — Virtual environment (after setup)
- `pyproject.toml` — Project dependencies

---

## Troubleshooting

- Ensure Python 3.12+ is installed.
- Activate your virtual environment before running commands.
- Check your Claude Desktop config for correct paths.

---

## License

MIT
