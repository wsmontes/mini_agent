# Mini Agent - Qwen3 Function Calling Agent

A robust AI agent system using Qwen3-4B-toolcalling model via LM Studio with advanced function calling capabilities.

## Features

- 🤖 **Qwen3-4B Integration**: Optimized for local deployment with LM Studio
- 🛠️ **Function Calling**: Hermes-style tool use protocol
- 🔧 **Extensible Tools**: Easy-to-add custom tools and functions
- 💬 **Conversational**: Maintains context across interactions
- 🎯 **Type-Safe**: Pydantic models for validation
- 🎨 **Rich CLI**: Beautiful terminal interface

## Prerequisites

1. **LM Studio**: Download from [lmstudio.ai](https://lmstudio.ai)
2. **Model**: Load the Qwen3-4B-toolcalling model in LM Studio
   - Search for "Qwen3-4B" in LM Studio
   - Download and load the model
   - Start the local server (default: http://localhost:1234)

## Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd mini_agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings
```

## Quick Start

```bash
# Run the interactive agent
python main.py

# Run example demos
python examples/weather_demo.py
python examples/calculator_demo.py
python examples/multi_tool_demo.py
```

## Usage

### Basic Agent Usage

```python
from agent import QwenAgent
from tools import WeatherTool, CalculatorTool

# Initialize agent
agent = QwenAgent(
    model_name="qwen3-4b-toolcall",
    base_url="http://localhost:1234/v1"
)

# Register tools
agent.register_tool(WeatherTool())
agent.register_tool(CalculatorTool())

# Query the agent
response = agent.query("What's the weather in San Francisco?")
print(response)
```

### Creating Custom Tools

```python
from tools.base import BaseTool
from pydantic import Field

class MyCustomTool(BaseTool):
    name = "my_custom_tool"
    description = "Description of what this tool does"
    
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Description of param1"
                }
            },
            "required": ["param1"]
        }
    
    def execute(self, param1: str) -> dict:
        # Your tool logic here
        return {"result": f"Processed {param1}"}
```

## Architecture

```
mini_agent/
├── agent.py           # Core agent implementation
├── tools/             # Tool implementations
│   ├── base.py       # Base tool class
│   ├── weather.py    # Weather tool
│   ├── calculator.py # Calculator tool
│   └── web.py        # Web search tool
├── examples/          # Example scripts
├── tests/            # Unit tests
└── main.py           # Interactive CLI
```

## Configuration

Edit `.env` to configure:

- `LM_STUDIO_BASE_URL`: Your LM Studio API endpoint
- `MODEL_NAME`: Model identifier
- `MAX_TOKENS`: Maximum response length
- `TEMPERATURE`: Creativity level (0.0-1.0)
- `TOP_P`: Nucleus sampling parameter

## Available Tools

### Weather Tool
Get current weather or forecast for any location.

### Calculator Tool
Perform mathematical calculations and expressions.

### Web Search Tool
Search the web for information (simulated).

### File Operations Tool
Read, write, and manage files.

## Development

```bash
# Run tests
python -m pytest tests/

# Format code
black .

# Type checking
mypy agent.py tools/
```

## Troubleshooting

### LM Studio Connection Issues
- Ensure LM Studio server is running
- Check the port (default: 1234)
- Verify model is loaded

### Function Calling Not Working
- Ensure using Qwen3 model with tool calling support
- Check tool definitions follow JSON Schema format
- Enable thinking mode if needed

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or submit a PR.

## Acknowledgments

- [Qwen Team](https://github.com/QwenLM/Qwen) for the amazing models
- [LM Studio](https://lmstudio.ai) for the local inference platform
