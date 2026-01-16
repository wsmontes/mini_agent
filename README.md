# Mini Agent - Qwen3 Function Calling Agent

A robust AI agent system using Qwen3-4B-toolcalling model via LM Studio with advanced function calling capabilities and **hierarchical coordination architecture**.

## Features

- 🤖 **Qwen3-4B Integration**: Optimized for local deployment with LM Studio
- 🎯 **Hierarchical Coordination**: Gemma-3-4B orchestrates Qwen for complex tasks
- 🗂️ **Tool Clustering**: Intelligent tool organization by domain (WEB, MATH, DATA, etc.)
- 🛠️ **Function Calling**: Hermes-style tool use protocol
- 🔧 **Extensible Tools**: Easy-to-add custom tools and functions
- 💬 **Conversational**: Maintains context across interactions
- 🎨 **Rich CLI**: Beautiful terminal interface
- 🔄 **Auto-Recovery**: Detects loops and automatically escalates issues

## Architecture Overview

Mini Agent uses a **two-level hierarchical architecture** for handling complex, multi-step tasks:

### Level 1: Task Executor (Qwen Agent)
- **Role**: Executes specific tool calls
- **Model**: Qwen3-4B with function calling
- **Responsibilities**:
  - Receives specific instructions
  - Selects and executes appropriate tools
  - Returns execution results

### Level 2: Task Coordinator (Gemma Coordinator)
- **Role**: Plans and orchestrates multi-step tasks
- **Model**: Gemma-3-4B for reasoning and planning
- **Responsibilities**:
  - Breaks down user requests into tasks and subtasks
  - Selects appropriate tool clusters dynamically
  - Formulates specific instructions for Qwen
  - Evaluates results and decides next actions
  - Detects loops and escalates when stuck

### Tool Clustering System
Tools are organized into semantic clusters:
- **WEB**: Browser automation, navigation, page interaction
- **MATH**: Calculations, statistics, currency conversion
- **DATA**: File operations, CSV/JSON processing
- **TEXT**: Language processing, translation, summarization
- **COMMUNICATION**: Email, APIs, notifications
- **SYSTEM**: File system, datetime, commands
- **CODE**: Programming, debugging, code generation

**Benefits**:
- Only loads relevant tools per task (efficiency)
- Sliding window keeps recent tools accessible
- Reduces token usage and improves focus
- Dynamic cluster re-selection based on task evolution

### Workflow Example

```
User: "Search Google for Python creator, find his birth year"

[Gemma] Creates TODO:
  1. Navigate to Google
  2. Search for Python creator
  3. Extract birth year

[Gemma] Task 1 → Subtasks:
  - Open Google
  - Find search box
  - Enter query

[Gemma] Selects WEB cluster → loads browser tools

[Qwen] Executes: "Open URL https://google.com"
[Qwen] Executes: "Fill form with query='Python creator'"
[Qwen] Executes: "Submit search"

[Gemma] Evaluates: ✅ Search complete
[Gemma] Next task...
```

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
# Validate setup first
python validate_setup.py

# Run the basic interactive agent
python main.py

# Run with hierarchical coordination (recommended for complex tasks)
python test_step_by_step.py

# Run example demos
python examples/weather_demo.py
python examples/calculator_demo.py
python examples/multi_tool_demo.py
```

## Usage

### Basic Agent Usage (Single-level)

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

### Hierarchical Coordination (Two-level)

```python
from cluster_manager import create_default_cluster_manager
from outlines_agent import OutlinesQwenAgent
from gemma_cluster_coordinator import GemmaClusterCoordinator

# Setup
cluster_manager = create_default_cluster_manager()
qwen_agent = OutlinesQwenAgent(verbose=False)

# Create coordinator
coordinator = GemmaClusterCoordinator(
    cluster_manager=cluster_manager,
    qwen_agent=qwen_agent,
    gemma_model="google/gemma-3-4b",
    max_iterations=15,
    verbose=True
)

# Execute complex multi-step task
result = coordinator.query_step_by_step(
    "Search Google for Python creator and find his birth year"
)
print(result)
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
├── agent.py                      # Core Qwen agent (executor)
├── outlines_agent.py             # Enhanced Qwen with context support
├── gemma_coordinator.py          # Simple Gemma coordinator
├── gemma_cluster_coordinator.py  # Advanced coordinator with clustering
├── cluster_manager.py            # Tool clustering system
├── validate_setup.py             # Setup validation script
├── tools/                        # Tool implementations
│   ├── base.py                   # Base tool class
│   ├── browser_tools.py          # Web automation
│   ├── calculator.py             # Math operations
│   ├── general_tools.py          # Misc utilities
│   ├── extract_links_tool.py     # Link extraction
│   └── click_link_by_index_tool.py # Link clicking
├── examples/                     # Example scripts
├── tests/                        # Unit tests
└── main.py                       # Interactive CLI
```

### Component Roles

| Component | Purpose | Model |
|-----------|---------|-------|
| **QwenAgent** | Execute specific tool calls | Qwen3-4B |
| **OutlinesQwenAgent** | Enhanced executor with context | Qwen3-4B |
| **GemmaCoordinator** | Simple multi-query coordination | Gemma-3-4B |
| **GemmaClusterCoordinator** | Full hierarchical system | Gemma-3-4B |
| **ClusterManager** | Organize tools by domain | N/A |

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
