# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- Python 3.11+
- LM Studio installed
- 8GB+ RAM

## Step 1: Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd mini_agent

# Run setup script
chmod +x setup.sh
./setup.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

## Step 2: LM Studio

1. **Download LM Studio**: [lmstudio.ai](https://lmstudio.ai)

2. **Search for model**: "Qwen3-4B-toolcalling"

3. **Download** the GGUF version (Q4_K_M recommended)

4. **Load the model** in LM Studio

5. **Start local server**: 
   - Go to "Local Server" tab
   - Click "Start Server"
   - Default: `http://localhost:1234`

## Step 3: Test Connection

```bash
# Test with curl
curl http://localhost:1234/v1/models

# Or run simple example
python examples/simple_usage.py
```

## Step 4: Run the Agent

### Interactive Mode

```bash
python main.py
```

You'll see:

```
╔══════════════════════════════════════════╗
║   🤖 Qwen3-4B Function Calling Agent    ║
║                                          ║
║   Powered by LM Studio                   ║
║   Model: Qwen3-4B-toolcalling           ║
╚══════════════════════════════════════════╝

⚙️  Initializing agent...
📦 Loading tools...
✓ Loaded 5 tools

Available tools:
  • get_current_temperature
  • get_temperature_date
  • calculator
  • web_search
  • list_directory

✨ Agent ready! Type your message or 'help' for commands

You: 
```

### Try These Queries

```
What's the temperature in San Francisco?

Calculate the square root of 144

Search the web for Python tutorials

What's 25 * 4 + 10?

List files in the current directory
```

## Step 5: Explore Examples

```bash
# Weather queries
python examples/weather_demo.py

# Math calculations
python examples/calculator_demo.py

# Multi-tool orchestration
python examples/multi_tool_demo.py

# Custom tool creation
python examples/custom_tool.py
```

## Quick Code Example

```python
from agent import QwenAgent
from tools import CalculatorTool, WeatherTool

# Initialize agent
agent = QwenAgent()

# Register tools
agent.register_tool(CalculatorTool())
agent.register_tool(WeatherTool())

# Query
response = agent.query("What's the weather in Tokyo?")
print(response)
```

## Troubleshooting

### "Connection refused"

- Ensure LM Studio server is running
- Check the port (default: 1234)
- Verify `.env` has correct BASE_URL

### "Model not found"

- Load the model in LM Studio first
- Check the model name in `.env`

### Slow responses

- Use Q4 quantization (smaller model)
- Reduce `max_tokens` in `.env`
- Enable GPU acceleration in LM Studio

## Next Steps

1. **Read the docs**:
   - [LM Studio Setup](docs/LM_STUDIO_SETUP.md)
   - [Creating Custom Tools](docs/CUSTOM_TOOLS.md)
   - [API Reference](docs/API_REFERENCE.md)

2. **Create custom tools** for your use case

3. **Build your application** using the agent

4. **Join the community** (if applicable)

## Configuration

Edit `.env` to customize:

```bash
# LM Studio
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_API_KEY=lm-studio

# Model
MODEL_NAME=qwen3-4b-toolcall
MAX_TOKENS=2048
TEMPERATURE=0.7

# Agent
ENABLE_THINKING=false
AUTO_EXECUTE_TOOLS=true
```

## Commands

Interactive mode commands:

- `help` - Show help
- `clear` - Clear conversation
- `exit` or `quit` - Exit

## Resources

- [Qwen3 Documentation](https://qwen.readthedocs.io/)
- [LM Studio Docs](https://lmstudio.ai/docs)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

## Support

- Check [docs/](docs/) for detailed guides
- Run tests: `python -m pytest tests/`
- Review [examples/](examples/) for patterns

Happy building! 🚀
