# Database Server MCP

A powerful MCP server that enables database operations through Claude Desktop. Connect to SQLite and MySQL databases, execute queries, and manage your data seamlessly.

## Features

- **SQLite Support**: Built-in SQLite database with sample data
- **MySQL Support**: Connect to local or remote MySQL databases
- **Query Execution**: Run any SQL query safely
- **Schema Inspection**: List tables and describe table structures
- **Sample Data**: Pre-loaded sample tables for practice

## Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (fast Python package manager)
- Claude Desktop (for MCP integration)
- MySQL (optional, for MySQL support)

## Setup Instructions

### 1. Install `uv`

```sh
pip install uv
```
Or, for faster installation:
```sh
curl -Ls https://astral.sh/uv/install.sh | sh
```

### 2. Navigate to Database Server Directory

```sh
cd servers/database_server
```

### 3. Create Virtual Environment

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

### 4. Install Dependencies

```sh
uv pip install .
```

### 5. Configure Claude Desktop

Edit your Claude Desktop config file at  
`~/Library/Application Support/Claude/claude_desktop_config.json` and add:

```json
{
    "mcpServers": {
        "database": {
            "command": "/opt/anaconda3/bin/uv",
            "args": [
                "--directory", "/Users/venugopal.adep/mcp/servers/database_server",
                "run", 
                "database_server.py"
            ]
        }
    }
}
```

## Usage

### 1. Initialize Sample Data

First, create sample tables with practice data:

```
Use the init_sample_data tool to create sample tables (customers, products, orders)
```

### 2. Available Tools

- **execute_query**: Run any SQL query
- **list_tables**: See all available tables
- **describe_table**: Get table schema information
- **init_sample_data**: Create sample data for practice

### 3. Example Queries

Once sample data is initialized, try these queries:

**List all customers:**
```sql
SELECT * FROM customers;
```

**Find orders with customer details:**
```sql
SELECT c.name, c.email, p.name as product, o.quantity, o.order_date
FROM orders o
JOIN customers c ON o.customer_id = c.id
JOIN products p ON o.product_id = p.id;
```

**Get total sales by category:**
```sql
SELECT p.category, SUM(p.price * o.quantity) as total_sales
FROM orders o
JOIN products p ON o.product_id = p.id
GROUP BY p.category;
```

## Sample Database Schema

The server includes three sample tables:

### Customers
- `id` (Primary Key)
- `name`
- `email`
- `city`
- `created_at`

### Products
- `id` (Primary Key)
- `name`
- `price`
- `category`
- `stock`

### Orders
- `id` (Primary Key)
- `customer_id` (Foreign Key)
- `product_id` (Foreign Key)
- `quantity`
- `order_date`

## MySQL Configuration

To use MySQL instead of SQLite, modify the MySQL connection settings in `database_server.py`:

```python
config = {
    'host': 'your_host',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'your_database'
}
```

Then install MySQL connector:
```sh
uv pip install mysql-connector-python
```

## File Structure

- `database_server.py` — Main MCP server implementation
- `pyproject.toml` — Project dependencies and configuration
- `databases/` — Directory for SQLite databases (auto-created)
- `.venv/` — Virtual environment (after setup)

## Troubleshooting

- **SQLite Issues**: Database files are created automatically in the `databases/` folder
- **MySQL Connection**: Ensure MySQL server is running and credentials are correct
- **Permissions**: Make sure the server has write access to the databases directory

## License

MIT