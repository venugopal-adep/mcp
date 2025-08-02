#!/usr/bin/env python3

import asyncio
import sqlite3
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("database-server")

# Database configuration
DB_DIR = Path(__file__).parent / "databases"
SQLITE_DB = DB_DIR / "sample.db"

class DatabaseServer:
    def __init__(self):
        self.server = Server("database-server")
        self.setup_handlers()
        
    def setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available database tools."""
            return [
                types.Tool(
                    name="execute_query",
                    description="Execute a SQL query on the database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "SQL query to execute"
                            },
                            "database": {
                                "type": "string",
                                "description": "Database type (sqlite or mysql)",
                                "enum": ["sqlite", "mysql"],
                                "default": "sqlite"
                            },
                            "params": {
                                "type": "array",
                                "description": "Parameters for prepared statements",
                                "items": {"type": "string"},
                                "default": []
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="list_tables",
                    description="List all tables in the database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "database": {
                                "type": "string",
                                "description": "Database type (sqlite or mysql)",
                                "enum": ["sqlite", "mysql"],
                                "default": "sqlite"
                            }
                        }
                    }
                ),
                types.Tool(
                    name="describe_table",
                    description="Get table schema information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "table_name": {
                                "type": "string",
                                "description": "Name of the table to describe"
                            },
                            "database": {
                                "type": "string",
                                "description": "Database type (sqlite or mysql)",
                                "enum": ["sqlite", "mysql"],
                                "default": "sqlite"
                            }
                        },
                        "required": ["table_name"]
                    }
                ),
                types.Tool(
                    name="init_sample_data",
                    description="Initialize database with sample tables and data",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "database": {
                                "type": "string",
                                "description": "Database type (sqlite or mysql)",
                                "enum": ["sqlite", "mysql"],
                                "default": "sqlite"
                            }
                        }
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
                if name == "execute_query":
                    result = await self._execute_query(
                        arguments.get("query", ""),
                        arguments.get("database", "sqlite"),
                        arguments.get("params", [])
                    )
                    return [types.TextContent(type="text", text=result)]
                
                elif name == "list_tables":
                    result = await self._list_tables(arguments.get("database", "sqlite"))
                    return [types.TextContent(type="text", text=result)]
                
                elif name == "describe_table":
                    result = await self._describe_table(
                        arguments.get("table_name", ""),
                        arguments.get("database", "sqlite")
                    )
                    return [types.TextContent(type="text", text=result)]
                
                elif name == "init_sample_data":
                    result = await self._init_sample_data(arguments.get("database", "sqlite"))
                    return [types.TextContent(type="text", text=result)]
                
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def _execute_query(self, query: str, database: str, params: List[str]) -> str:
        """Execute a SQL query."""
        if not query.strip():
            return "Error: Query cannot be empty"
        
        if database == "sqlite":
            return await self._execute_sqlite_query(query, params)
        elif database == "mysql":
            return await self._execute_mysql_query(query, params)
        else:
            return f"Error: Unsupported database type: {database}"

    async def _execute_sqlite_query(self, query: str, params: List[str]) -> str:
        """Execute SQLite query."""
        try:
            # Ensure database directory exists
            DB_DIR.mkdir(exist_ok=True)
            
            conn = sqlite3.connect(SQLITE_DB)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith(('SELECT', 'WITH', 'PRAGMA')):
                rows = cursor.fetchall()
                if rows:
                    columns = [description[0] for description in cursor.description]
                    result = f"Columns: {', '.join(columns)}\n\n"
                    for row in rows:
                        result += " | ".join(str(row[col]) for col in columns) + "\n"
                    return result
                else:
                    return "No results found"
            else:
                conn.commit()
                return f"Query executed successfully. Rows affected: {cursor.rowcount}"
                
        except Exception as e:
            return f"SQLite Error: {str(e)}"
        finally:
            if 'conn' in locals():
                conn.close()

    async def _execute_mysql_query(self, query: str, params: List[str]) -> str:
        """Execute MySQL query."""
        try:
            import mysql.connector
            
            # Default MySQL connection (you can modify these)
            config = {
                'host': 'localhost',
                'user': 'root',
                'password': '',
                'database': 'test_db'
            }
            
            conn = mysql.connector.connect(**config)
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith(('SELECT', 'WITH', 'SHOW', 'DESCRIBE')):
                rows = cursor.fetchall()
                if rows:
                    columns = [description[0] for description in cursor.description]
                    result = f"Columns: {', '.join(columns)}\n\n"
                    for row in rows:
                        result += " | ".join(str(col) for col in row) + "\n"
                    return result
                else:
                    return "No results found"
            else:
                conn.commit()
                return f"Query executed successfully. Rows affected: {cursor.rowcount}"
                
        except ImportError:
            return "Error: mysql-connector-python not installed. Run: pip install mysql-connector-python"
        except Exception as e:
            return f"MySQL Error: {str(e)}"
        finally:
            if 'conn' in locals():
                conn.close()

    async def _list_tables(self, database: str) -> str:
        """List all tables in the database."""
        if database == "sqlite":
            query = "SELECT name FROM sqlite_master WHERE type='table';"
            return await self._execute_sqlite_query(query, [])
        elif database == "mysql":
            query = "SHOW TABLES;"
            return await self._execute_mysql_query(query, [])
        else:
            return f"Error: Unsupported database type: {database}"

    async def _describe_table(self, table_name: str, database: str) -> str:
        """Get table schema information."""
        if not table_name:
            return "Error: Table name is required"
            
        if database == "sqlite":
            query = f"PRAGMA table_info({table_name});"
            return await self._execute_sqlite_query(query, [])
        elif database == "mysql":
            query = f"DESCRIBE {table_name};"
            return await self._execute_mysql_query(query, [])
        else:
            return f"Error: Unsupported database type: {database}"

    async def _init_sample_data(self, database: str) -> str:
        """Initialize database with sample tables and data."""
        if database == "sqlite":
            return await self._init_sqlite_sample_data()
        elif database == "mysql":
            return await self._init_mysql_sample_data()
        else:
            return f"Error: Unsupported database type: {database}"

    async def _init_sqlite_sample_data(self) -> str:
        """Initialize SQLite with sample data."""
        try:
            DB_DIR.mkdir(exist_ok=True)
            conn = sqlite3.connect(SQLITE_DB)
            cursor = conn.cursor()
            
            # Drop existing tables
            cursor.execute("DROP TABLE IF EXISTS orders")
            cursor.execute("DROP TABLE IF EXISTS customers")
            cursor.execute("DROP TABLE IF EXISTS products")
            
            # Create tables
            cursor.execute('''
                CREATE TABLE customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    city TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price DECIMAL(10, 2) NOT NULL,
                    category TEXT,
                    stock INTEGER DEFAULT 0
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER,
                    product_id INTEGER,
                    quantity INTEGER NOT NULL,
                    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers (id),
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')
            
            # Insert sample data
            customers_data = [
                ('John Doe', 'john@example.com', 'New York'),
                ('Jane Smith', 'jane@example.com', 'Los Angeles'),
                ('Mike Johnson', 'mike@example.com', 'Chicago'),
                ('Sarah Williams', 'sarah@example.com', 'Houston'),
                ('David Brown', 'david@example.com', 'Phoenix')
            ]
            
            cursor.executemany(
                'INSERT INTO customers (name, email, city) VALUES (?, ?, ?)',
                customers_data
            )
            
            products_data = [
                ('Laptop', 999.99, 'Electronics', 50),
                ('Smartphone', 699.99, 'Electronics', 100),
                ('Desk Chair', 199.99, 'Furniture', 25),
                ('Coffee Mug', 15.99, 'Kitchen', 200),
                ('Notebook', 5.99, 'Stationery', 150)
            ]
            
            cursor.executemany(
                'INSERT INTO products (name, price, category, stock) VALUES (?, ?, ?, ?)',
                products_data
            )
            
            orders_data = [
                (1, 1, 2),
                (2, 2, 1),
                (3, 3, 5),
                (1, 4, 3),
                (4, 1, 1),
                (5, 5, 10)
            ]
            
            cursor.executemany(
                'INSERT INTO orders (customer_id, product_id, quantity) VALUES (?, ?, ?)',
                orders_data
            )
            
            conn.commit()
            conn.close()
            
            return f"SQLite sample data initialized successfully at {SQLITE_DB}"
            
        except Exception as e:
            return f"Error initializing SQLite sample data: {str(e)}"

    async def _init_mysql_sample_data(self) -> str:
        """Initialize MySQL with sample data."""
        return "MySQL sample data initialization not implemented yet. Use SQLite for now."

async def main():
    # Create server instance
    db_server = DatabaseServer()
    
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await db_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="database-server",
                server_version="0.1.0",
                capabilities=db_server.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())