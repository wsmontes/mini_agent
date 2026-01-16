# API Reference

## QwenAgent Class

Main agent class for interacting with the Qwen3-4B model.

### Constructor

```python
QwenAgent(
    model_name: Optional[str] = None,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: float = 0.7,
    top_p: float = 0.8,
    max_tokens: int = 2048,
    enable_thinking: bool = False,
    auto_execute_tools: bool = True
)
```

**Parameters:**

- `model_name` (str, optional): Model identifier. Defaults to env `MODEL_NAME`.
- `base_url` (str, optional): LM Studio API base URL. Defaults to env `LM_STUDIO_BASE_URL`.
- `api_key` (str, optional): API key. Defaults to env `LM_STUDIO_API_KEY`.
- `temperature` (float): Sampling temperature (0.0-1.0). Higher = more creative.
- `top_p` (float): Nucleus sampling parameter (0.0-1.0).
- `max_tokens` (int): Maximum tokens to generate.
- `enable_thinking` (bool): Enable reasoning/thinking mode.
- `auto_execute_tools` (bool): Automatically execute tool calls.

**Example:**

```python
agent = QwenAgent(
    temperature=0.7,
    enable_thinking=False,
    auto_execute_tools=True
)
```

### Methods

#### set_system_message()

Set the system message for the agent.

```python
agent.set_system_message(message: str)
```

**Example:**

```python
agent.set_system_message("You are a helpful coding assistant.")
```

#### register_tool()

Register a tool for the agent to use.

```python
agent.register_tool(tool: BaseTool)
```

**Example:**

```python
from tools import CalculatorTool

agent.register_tool(CalculatorTool())
```

#### unregister_tool()

Remove a tool from the agent.

```python
agent.unregister_tool(tool_name: str)
```

**Example:**

```python
agent.unregister_tool("calculator")
```

#### clear_tools()

Remove all registered tools.

```python
agent.clear_tools()
```

#### reset_conversation()

Clear conversation history.

```python
agent.reset_conversation()
```

#### query()

Send a query to the agent and get a response.

```python
agent.query(
    message: str,
    max_tool_iterations: int = 5,
    return_metadata: bool = False
) -> str | Dict[str, Any]
```

**Parameters:**

- `message` (str): User message/query
- `max_tool_iterations` (int): Maximum tool calling rounds
- `return_metadata` (bool): Return full metadata

**Returns:**

- If `return_metadata=False`: String response
- If `return_metadata=True`: Dictionary with metadata

**Example (simple):**

```python
response = agent.query("What's 2 + 2?")
print(response)  # "The result is 4."
```

**Example (with metadata):**

```python
response = agent.query("Calculate sqrt(144)", return_metadata=True)

if response["success"]:
    print(f"Content: {response['content']}")
    print(f"Tool calls: {len(response['tool_calls'])}")
    print(f"Iterations: {response['iterations']}")
```

**Metadata Response Structure:**

```python
{
    "success": bool,              # Whether the query succeeded
    "content": str,               # Agent's response
    "tool_calls": List[Dict],     # Tool calls made
    "iterations": int,            # Number of tool calling rounds
    "finish_reason": str,         # Why generation stopped
    "error": str                  # Error message (if failed)
}
```

**Tool Call Structure:**

```python
{
    "call_id": str,               # Unique call ID
    "function_name": str,         # Tool name
    "arguments": dict,            # Tool arguments
    "success": bool,              # Whether execution succeeded
    "result": dict,               # Tool result
    "content": str,               # JSON-formatted result
    "error": str                  # Error message (if failed)
}
```

#### chat()

Interactive chat mode in the terminal.

```python
agent.chat(enable_input: bool = True)
```

**Example:**

```python
agent.chat()  # Starts interactive session
```

## BaseTool Class

Abstract base class for creating tools.

### Properties

```python
name: str           # Tool identifier
description: str    # Tool description
```

### Methods

#### get_parameters()

Return JSON Schema for tool parameters.

```python
def get_parameters(self) -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": { ... },
        "required": [ ... ]
    }
```

#### execute()

Execute the tool logic.

```python
def execute(self, **kwargs) -> Dict[str, Any]:
    # Tool implementation
    return {"result": "..."}
```

## Built-in Tools

### WeatherTool

Get weather information for a location.

```python
from tools import WeatherTool

tool = WeatherTool()
result = tool.execute(
    location="San Francisco, CA, USA",
    date="2024-12-25",          # Optional
    unit="celsius"               # or "fahrenheit"
)
```

### CurrentWeatherTool

Get current temperature only.

```python
from tools import CurrentWeatherTool

tool = CurrentWeatherTool()
result = tool.execute(
    location="Tokyo, Japan",
    unit="celsius"
)
```

### ForecastWeatherTool

Get temperature for a specific date.

```python
from tools import ForecastWeatherTool

tool = ForecastWeatherTool()
result = tool.execute(
    location="London, UK",
    date="2024-12-25",
    unit="celsius"
)
```

### CalculatorTool

Evaluate mathematical expressions.

```python
from tools import CalculatorTool

tool = CalculatorTool()
result = tool.execute(expression="sqrt(144) + 10")
# Returns: {"result": 22.0, "expression": "sqrt(144) + 10"}
```

### SimpleCalculatorTool

Basic arithmetic operations.

```python
from tools import SimpleCalculatorTool

tool = SimpleCalculatorTool()
result = tool.execute(
    operation="multiply",  # add, subtract, multiply, divide
    a=5,
    b=3
)
# Returns: {"result": 15}
```

### WebSearchTool

Search the web (simulated).

```python
from tools import WebSearchTool

tool = WebSearchTool()
result = tool.execute(
    query="Python programming",
    num_results=5
)
```

### WikipediaSearchTool

Search Wikipedia (simulated).

```python
from tools import WikipediaSearchTool

tool = WikipediaSearchTool()
result = tool.execute(topic="Artificial Intelligence")
```

### NewsSearchTool

Search for news articles (simulated).

```python
from tools import NewsSearchTool

tool = NewsSearchTool()
result = tool.execute(
    query="technology",
    days=7
)
```

### FileReadTool

Read contents of a file.

```python
from tools import FileReadTool

tool = FileReadTool()
result = tool.execute(
    filepath="/path/to/file.txt",
    encoding="utf-8"
)
```

### FileWriteTool

Write content to a file.

```python
from tools import FileWriteTool

tool = FileWriteTool()
result = tool.execute(
    filepath="/path/to/output.txt",
    content="Hello, World!",
    mode="write"  # or "append"
)
```

### FileListTool

List files in a directory.

```python
from tools import FileListTool

tool = FileListTool()
result = tool.execute(
    path="/path/to/directory",
    pattern="*.txt"  # Optional glob pattern
)
```

## Environment Variables

Configure via `.env` file:

```bash
# LM Studio Configuration
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_API_KEY=lm-studio

# Model Configuration
MODEL_NAME=qwen3-4b-toolcall
MAX_TOKENS=2048
TEMPERATURE=0.7
TOP_P=0.8
```

## Error Handling

The agent and tools return error information in the response:

```python
response = agent.query("...", return_metadata=True)

if not response["success"]:
    print(f"Error: {response['error']}")
```

Tool execution errors:

```python
result = tool.execute(invalid_param="...")

if "error" in result:
    print(f"Tool error: {result['error']}")
```

## Type Hints

All classes and methods include type hints for better IDE support:

```python
from typing import Dict, Any, List, Optional

def query(
    message: str,
    max_tool_iterations: int = 5,
    return_metadata: bool = False
) -> str | Dict[str, Any]:
    ...
```
