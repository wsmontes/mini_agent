# LM Studio Setup Guide

## Step 1: Download and Install LM Studio

1. Visit [lmstudio.ai](https://lmstudio.ai)
2. Download for your platform (macOS, Windows, Linux)
3. Install the application

## Step 2: Download the Qwen3-4B Model

1. Open LM Studio
2. Click on the search icon (🔍)
3. Search for: `Qwen3-4B` or `qwen3-4b-toolcalling`
4. Look for models with these characteristics:
   - **GGUF format** (optimized for local inference)
   - **4B parameters** (balanced size/performance)
   - **Tool calling** or **function calling** support

### Recommended Model Files

Search for one of these:
- `Manojb/Qwen3-4B-toolcalling-gguf-codex`
- `Qwen/Qwen3-4B-Instruct` (GGUF version)

Choose quantization based on your hardware:
- **Q4_K_M**: Balanced (recommended for most systems)
- **Q5_K_M**: Higher quality, more memory
- **Q8_0**: Best quality, requires more RAM

## Step 3: Load the Model

1. Click the downloaded model
2. Click "Load Model" button
3. Wait for the model to load (shows in the top status bar)

## Step 4: Start the Local Server

1. Go to the "Local Server" tab (🌐)
2. Click "Start Server"
3. Default settings:
   - **Port**: 1234
   - **Host**: localhost
   - **API**: OpenAI Compatible

### Server Configuration

Optional settings to adjust:

```json
{
  "host": "localhost",
  "port": 1234,
  "cors": true,
  "api_key": "lm-studio",
  "gpu_layers": -1
}
```

## Step 5: Test the Connection

In LM Studio, you can test with the built-in playground:

1. Go to "Chat" tab
2. Type a test message
3. Verify the model responds

Or test with curl:

```bash
curl http://localhost:1234/v1/models
```

Expected response:
```json
{
  "object": "list",
  "data": [
    {
      "id": "qwen3-4b-toolcall",
      "object": "model",
      ...
    }
  ]
}
```

## Step 6: Configure Mini Agent

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env`:
   ```bash
   LM_STUDIO_BASE_URL=http://localhost:1234/v1
   LM_STUDIO_API_KEY=lm-studio
   MODEL_NAME=qwen3-4b-toolcall
   ```

3. Test the connection:
   ```bash
   python examples/simple_usage.py
   ```

## Troubleshooting

### Server Won't Start

- Check if port 1234 is already in use
- Try a different port and update `.env`
- Restart LM Studio

### Model Not Loading

- Ensure you have enough RAM (8GB minimum)
- Try a smaller quantization (Q4 instead of Q8)
- Check available disk space

### Connection Refused

```bash
# Verify server is running
curl http://localhost:1234/v1/models

# Check the base URL in .env matches LM Studio
cat .env | grep BASE_URL
```

### Slow Responses

- Reduce `max_tokens` in agent configuration
- Use CPU if GPU is busy
- Try a smaller quantization

## Performance Tips

### GPU Acceleration (NVIDIA)

1. In LM Studio settings, enable "GPU Offload"
2. Set layers to offload (try -1 for all layers)
3. Monitor GPU usage with `nvidia-smi`

### Apple Silicon (M1/M2/M3)

1. LM Studio automatically uses Metal acceleration
2. Models run efficiently on unified memory
3. 8GB RAM minimum, 16GB recommended

### CPU-Only

1. Choose Q4 quantization
2. Reduce context length
3. Enable thread count optimization in settings

## Alternative: Using Ollama

If you prefer Ollama:

```bash
# Pull the model
ollama pull qwen3:4b

# Start server
ollama serve

# Update .env
LM_STUDIO_BASE_URL=http://localhost:11434/v1
```

## Model Card Reference

The Qwen3-4B-toolcalling model:

- **Parameters**: 4 billion
- **Context Length**: Up to 262K tokens
- **Training**: Fine-tuned on 60K function calling examples
- **Format**: GGUF (optimized)
- **Size**: ~4GB download
- **VRAM**: 6GB+ recommended
- **License**: MIT / Apache 2.0

## Next Steps

Once setup is complete:

1. Run the interactive agent: `python main.py`
2. Try the examples: `python examples/weather_demo.py`
3. Create custom tools for your needs
4. Build your AI application!

## Resources

- [LM Studio Documentation](https://lmstudio.ai/docs)
- [Qwen3 Model Card](https://huggingface.co/Qwen)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
