# Creating Custom Tools

## Overview

Tools extend the agent's capabilities. Each tool is a Python class that follows a specific interface.

## Basic Tool Structure

```python
from tools.base import BaseTool
from typing import Dict, Any


class MyTool(BaseTool):
    """Tool description."""
    
    # Tool identifier (used by the model)
    name = "my_tool"
    
    # Description for the model to understand when to use it
    description = "What this tool does and when to use it"
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Define the tool's parameters using JSON Schema.
        """
        return {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Description of param1"
                },
                "param2": {
                    "type": "integer",
                    "description": "Description of param2",
                    "minimum": 0,
                    "maximum": 100
                }
            },
            "required": ["param1"]  # Required parameters
        }
    
    def execute(self, param1: str, param2: int = 10) -> Dict[str, Any]:
        """
        Execute the tool logic.
        
        Args:
            param1: First parameter
            param2: Second parameter (optional, defaults to 10)
            
        Returns:
            Dictionary with results
        """
        # Your tool logic here
        result = f"Processed {param1} with {param2}"
        
        return {
            "success": True,
            "result": result,
            "param1": param1,
            "param2": param2
        }
```

## Real-World Example: Stock Price Tool

```python
from tools.base import BaseTool
from typing import Dict, Any
import requests


class StockPriceTool(BaseTool):
    """Get current stock price for a symbol."""
    
    name = "get_stock_price"
    description = (
        "Get the current stock price and basic information "
        "for a given stock symbol (e.g., AAPL, GOOGL, MSFT)"
    )
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., 'AAPL' for Apple)"
                },
                "currency": {
                    "type": "string",
                    "enum": ["USD", "EUR", "GBP"],
                    "description": "Currency for the price (default: USD)"
                }
            },
            "required": ["symbol"]
        }
    
    def execute(self, symbol: str, currency: str = "USD") -> Dict[str, Any]:
        """
        Fetch stock price.
        
        In production, integrate with:
        - Alpha Vantage API
        - Yahoo Finance API
        - IEX Cloud
        """
        try:
            # Simulated API call
            # In production: response = requests.get(api_url)
            
            # Simulated response
            return {
                "symbol": symbol.upper(),
                "price": 150.25,  # Simulated
                "currency": currency,
                "change": +2.5,
                "change_percent": +1.69,
                "timestamp": "2024-01-14T10:30:00Z"
            }
            
        except Exception as e:
            return {
                "error": f"Failed to fetch stock price: {str(e)}",
                "symbol": symbol
            }
```

## Parameter Types

### String Parameters

```python
"param_name": {
    "type": "string",
    "description": "Description",
    "minLength": 1,
    "maxLength": 100,
    "pattern": "^[A-Z]+$"  # Regex pattern
}
```

### Number Parameters

```python
"param_name": {
    "type": "integer",  # or "number" for float
    "description": "Description",
    "minimum": 0,
    "maximum": 100,
    "multipleOf": 5
}
```

### Boolean Parameters

```python
"param_name": {
    "type": "boolean",
    "description": "Description"
}
```

### Enum Parameters

```python
"param_name": {
    "type": "string",
    "enum": ["option1", "option2", "option3"],
    "description": "Choose one option"
}
```

### Array Parameters

```python
"param_name": {
    "type": "array",
    "items": {
        "type": "string"
    },
    "description": "List of items",
    "minItems": 1,
    "maxItems": 10
}
```

### Object Parameters

```python
"param_name": {
    "type": "object",
    "properties": {
        "nested_param": {
            "type": "string"
        }
    },
    "required": ["nested_param"]
}
```

## Best Practices

### 1. Clear Names and Descriptions

```python
# Good
name = "search_wikipedia"
description = "Search Wikipedia and return article summaries"

# Bad
name = "wiki"
description = "wiki stuff"
```

### 2. Detailed Parameter Descriptions

```python
# Good
"location": {
    "type": "string",
    "description": "City name in format: 'City, State, Country' (e.g., 'San Francisco, CA, USA')"
}

# Bad
"location": {
    "type": "string",
    "description": "location"
}
```

### 3. Error Handling

```python
def execute(self, **kwargs) -> Dict[str, Any]:
    try:
        # Tool logic
        result = do_something()
        return {"success": True, "result": result}
        
    except ValueError as e:
        return {"error": f"Invalid input: {e}"}
        
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}
```

### 4. Validation

```python
def execute(self, email: str) -> Dict[str, Any]:
    # Validate input
    if "@" not in email:
        return {"error": "Invalid email format"}
        
    # Process
    # ...
```

### 5. Consistent Return Format

```python
# Success case
{
    "success": True,
    "result": "data",
    "metadata": {...}
}

# Error case
{
    "error": "Error message",
    "code": "ERROR_CODE"
}
```

## Advanced Example: Database Query Tool

```python
import sqlite3
from tools.base import BaseTool
from typing import Dict, Any


class DatabaseQueryTool(BaseTool):
    """Execute SQL queries on a database."""
    
    name = "query_database"
    description = (
        "Execute read-only SQL queries on the database. "
        "Use for SELECT queries only. No modifications allowed."
    )
    
    def __init__(self, db_path: str):
        """Initialize with database path."""
        self.db_path = db_path
        
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "SQL SELECT query to execute"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of rows to return",
                    "minimum": 1,
                    "maximum": 1000,
                    "default": 100
                }
            },
            "required": ["query"]
        }
    
    def execute(self, query: str, limit: int = 100) -> Dict[str, Any]:
        """Execute SQL query."""
        # Security: Only allow SELECT queries
        if not query.strip().upper().startswith("SELECT"):
            return {
                "error": "Only SELECT queries are allowed",
                "query": query
            }
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Add LIMIT if not present
            if "LIMIT" not in query.upper():
                query += f" LIMIT {limit}"
                
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            conn.close()
            
            # Format results
            results = [
                dict(zip(columns, row))
                for row in rows
            ]
            
            return {
                "success": True,
                "query": query,
                "columns": columns,
                "rows": results,
                "count": len(results)
            }
            
        except sqlite3.Error as e:
            return {
                "error": f"Database error: {str(e)}",
                "query": query
            }
```

## Registering Custom Tools

```python
from agent import QwenAgent
from my_tools import StockPriceTool, DatabaseQueryTool

# Initialize agent
agent = QwenAgent()

# Register tools
agent.register_tool(StockPriceTool())
agent.register_tool(DatabaseQueryTool("/path/to/database.db"))

# Use the agent
response = agent.query("What's the price of AAPL stock?")
```

## Testing Custom Tools

```python
import unittest
from my_tools import StockPriceTool


class TestStockPriceTool(unittest.TestCase):
    def setUp(self):
        self.tool = StockPriceTool()
        
    def test_valid_symbol(self):
        result = self.tool.execute("AAPL")
        self.assertIn("price", result)
        self.assertEqual(result["symbol"], "AAPL")
        
    def test_invalid_symbol(self):
        result = self.tool.execute("INVALID")
        self.assertIn("error", result)
```

## Tips for Model Compatibility

1. **Use descriptive names**: The model uses the name and description to decide when to call the tool
2. **Be specific**: Clear parameter descriptions help the model extract the right values
3. **Provide examples**: In the description, show example inputs
4. **Handle edge cases**: Return helpful error messages

## Example Collection

Check the `tools/` directory for more examples:
- `weather.py`: API integration patterns
- `calculator.py`: Pure computation tools
- `web.py`: External service calls
- `file_ops.py`: File system operations

## Next Steps

1. Create your custom tool
2. Test it independently
3. Register it with the agent
4. Test with the agent
5. Refine descriptions based on model behavior
