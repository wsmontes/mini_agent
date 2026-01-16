# Project Structure

```
mini_agent/
│
├── agent.py                    # Core QwenAgent class
├── main.py                     # Interactive CLI entry point
│
├── tools/                      # Tool implementations
│   ├── __init__.py            # Tool exports
│   ├── base.py                # BaseTool abstract class
│   ├── calculator.py          # Math calculation tools
│   ├── weather.py             # Weather information tools
│   ├── web.py                 # Web search tools
│   └── file_ops.py            # File system operation tools
│
├── examples/                   # Example scripts
│   ├── simple_usage.py        # Basic usage example
│   ├── weather_demo.py        # Weather tool demo
│   ├── calculator_demo.py     # Calculator demo
│   ├── multi_tool_demo.py     # Multi-tool orchestration
│   └── custom_tool.py         # Custom tool creation example
│
├── tests/                      # Unit tests
│   ├── README.md              # Testing guide
│   ├── test_agent.py          # Agent tests
│   └── test_tools.py          # Tool tests
│
├── docs/                       # Documentation
│   ├── LM_STUDIO_SETUP.md     # LM Studio setup guide
│   ├── CUSTOM_TOOLS.md        # Custom tool creation guide
│   └── API_REFERENCE.md       # API documentation
│
├── .env.example               # Environment template
├── .env                       # Environment config (not committed)
├── .gitignore                 # Git ignore rules
│
├── requirements.txt           # Python dependencies
├── setup.sh                   # Quick setup script
│
├── README.md                  # Main documentation
├── QUICKSTART.md              # Quick start guide
└── PROJECT_STRUCTURE.md       # This file
```

## Core Files

### agent.py
Main agent implementation with:
- OpenAI-compatible API client
- Tool registration and execution
- Conversation management
- Hermes-style tool calling protocol

### main.py
Interactive CLI interface with:
- Rich terminal UI
- Command handling
- Tool visualization
- Error display

## Tools Directory

### Base Tool System
- `base.py`: Abstract base class defining tool interface
- All tools inherit from `BaseTool`
- Standard JSON Schema parameter definitions

### Tool Categories

**Calculation Tools** (`calculator.py`)
- `CalculatorTool`: Advanced math expressions
- `SimpleCalculatorTool`: Basic arithmetic

**Weather Tools** (`weather.py`)
- `WeatherTool`: General weather queries
- `CurrentWeatherTool`: Current temperature
- `ForecastWeatherTool`: Date-specific forecasts

**Web Tools** (`web.py`)
- `WebSearchTool`: General web search
- `WikipediaSearchTool`: Wikipedia queries
- `NewsSearchTool`: News article search

**File Tools** (`file_ops.py`)
- `FileReadTool`: Read file contents
- `FileWriteTool`: Write to files
- `FileListTool`: Directory listings

## Examples Directory

Demonstrates various usage patterns:

1. **simple_usage.py**: Minimal example for getting started
2. **weather_demo.py**: Weather-specific queries
3. **calculator_demo.py**: Mathematical calculations
4. **multi_tool_demo.py**: Complex multi-tool workflows
5. **custom_tool.py**: How to create custom tools

## Tests Directory

Unit tests organized by component:
- `test_agent.py`: Agent functionality tests
- `test_tools.py`: Tool implementation tests

Run with: `python -m pytest tests/`

## Documentation

### User Guides
- `README.md`: Overview and installation
- `QUICKSTART.md`: 5-minute setup guide
- `docs/LM_STUDIO_SETUP.md`: Detailed LM Studio setup

### Developer Guides
- `docs/CUSTOM_TOOLS.md`: Creating custom tools
- `docs/API_REFERENCE.md`: Complete API documentation
- `tests/README.md`: Testing guide

## Configuration Files

### .env
Runtime configuration:
```bash
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_API_KEY=lm-studio
MODEL_NAME=qwen3-4b-toolcall
TEMPERATURE=0.7
TOP_P=0.8
MAX_TOKENS=2048
```

### requirements.txt
Python dependencies:
- `openai`: API client
- `python-dotenv`: Environment management
- `requests`: HTTP requests
- `pydantic`: Data validation
- `rich`: Terminal UI

## Adding New Components

### New Tool
1. Create in `tools/` directory
2. Inherit from `BaseTool`
3. Implement required methods
4. Add to `tools/__init__.py`
5. Create test in `tests/test_tools.py`
6. Add example in `examples/`

### New Example
1. Create in `examples/` directory
2. Import agent and tools
3. Demonstrate specific use case
4. Add comments for clarity

### New Documentation
1. Create in `docs/` directory
2. Use Markdown format
3. Link from main `README.md`
4. Keep consistent style

## File Naming Conventions

- **Python files**: `lowercase_with_underscores.py`
- **Classes**: `PascalCase`
- **Functions/methods**: `lowercase_with_underscores()`
- **Constants**: `UPPERCASE_WITH_UNDERSCORES`
- **Documentation**: `UPPERCASE.md` (guides), `lowercase.md` (technical)

## Import Structure

```python
# Standard library
import os
import json
from typing import Dict, Any

# Third-party
from openai import OpenAI
from dotenv import load_dotenv

# Local
from agent import QwenAgent
from tools import BaseTool, CalculatorTool
```

## Development Workflow

1. **Feature development**:
   - Create feature branch
   - Implement in appropriate directory
   - Add tests
   - Update documentation

2. **Testing**:
   ```bash
   python -m pytest tests/
   ```

3. **Code style**:
   ```bash
   black .
   mypy agent.py tools/
   ```

4. **Documentation**:
   - Update relevant .md files
   - Add examples if needed
   - Update API reference

## Extension Points

The architecture supports:

1. **Custom tools**: Extend `BaseTool`
2. **Custom agents**: Extend `QwenAgent`
3. **Custom prompts**: Override system messages
4. **Custom CLI**: Build on `main.py` structure
5. **API integration**: Use agent programmatically

## Dependencies

### Production
- `openai>=1.12.0`: API client
- `python-dotenv>=1.0.0`: Config management
- `requests>=2.31.0`: HTTP requests
- `pydantic>=2.5.0`: Data validation
- `rich>=13.7.0`: Terminal UI

### Development
- `pytest`: Testing framework
- `black`: Code formatter
- `mypy`: Type checker

## Performance Considerations

- Tool schemas cached in memory
- Conversation history grows with use
- Use `reset_conversation()` to clear memory
- Adjust `max_tokens` for speed/quality trade-off
- Use `enable_thinking=False` for faster responses

## Security Notes

- `.env` file contains sensitive config
- Never commit `.env` to version control
- Validate tool inputs
- Restrict file operations in production
- Use read-only database connections where possible
