# Advanced Usage Guide

## Table of Contents
1. [Conversation Management](#conversation-management)
2. [Tool Configuration](#tool-configuration)
3. [Error Handling](#error-handling)
4. [Performance Optimization](#performance-optimization)
5. [Production Deployment](#production-deployment)
6. [Advanced Patterns](#advanced-patterns)

## Conversation Management

### Maintaining Context

The agent maintains conversation history automatically:

```python
agent = QwenAgent()
agent.register_tool(WeatherTool())

# First query
agent.query("What's the weather in Tokyo?")

# Follow-up (agent remembers Tokyo)
agent.query("How about tomorrow?")

# Another follow-up
agent.query("Compare it with yesterday")
```

### System Messages

Set behavioral guidelines:

```python
agent.set_system_message("""
You are an expert data analyst assistant.
- Always be precise with numbers
- Show your reasoning when analyzing data
- Ask for clarification if inputs are ambiguous
- Format responses in markdown when appropriate
""")
```

### Resetting Context

Clear conversation when needed:

```python
# Long conversation
for query in queries:
    agent.query(query)

# Reset for new conversation
agent.reset_conversation()
agent.query("Start fresh topic...")
```

### Conversation Persistence

Save and restore conversations:

```python
import json

# Save conversation
with open("conversation.json", "w") as f:
    json.dump(agent.messages, f)

# Restore conversation
with open("conversation.json", "r") as f:
    agent.messages = json.load(f)
```

## Tool Configuration

### Conditional Tool Registration

Enable tools based on context:

```python
class AdaptiveAgent:
    def __init__(self):
        self.agent = QwenAgent()
        self.available_tools = {
            "weather": WeatherTool(),
            "calculator": CalculatorTool(),
            "web": WebSearchTool(),
            "files": FileReadTool(),
        }
    
    def enable_tools(self, tool_names):
        """Enable specific tools."""
        self.agent.clear_tools()
        for name in tool_names:
            if name in self.available_tools:
                self.agent.register_tool(self.available_tools[name])
    
    def query_with_tools(self, message, tools):
        """Query with specific tool set."""
        self.enable_tools(tools)
        return self.agent.query(message)

# Usage
adaptive = AdaptiveAgent()

# Weather query with only weather tools
response = adaptive.query_with_tools(
    "What's the weather?",
    tools=["weather"]
)

# Math query with calculator
response = adaptive.query_with_tools(
    "Calculate 25 * 4",
    tools=["calculator"]
)
```

### Tool Whitelisting/Blacklisting

Control tool access:

```python
class RestrictedAgent(QwenAgent):
    def __init__(self, allowed_tools=None, **kwargs):
        super().__init__(**kwargs)
        self.allowed_tools = allowed_tools or []
        
    def register_tool(self, tool):
        if self.allowed_tools and tool.name not in self.allowed_tools:
            print(f"Tool {tool.name} not in whitelist")
            return
        super().register_tool(tool)

# Usage
agent = RestrictedAgent(allowed_tools=["calculator", "web_search"])
agent.register_tool(CalculatorTool())  # OK
agent.register_tool(FileWriteTool())   # Blocked
```

## Error Handling

### Graceful Degradation

```python
def safe_query(agent, message, fallback="I couldn't process that."):
    """Query with fallback."""
    try:
        response = agent.query(message, return_metadata=True)
        
        if response.get("success"):
            return response["content"]
        else:
            error = response.get("error", "Unknown error")
            print(f"Error: {error}")
            return fallback
            
    except Exception as e:
        print(f"Exception: {e}")
        return fallback

# Usage
response = safe_query(agent, "Complex query...")
```

### Retry Logic

```python
import time

def query_with_retry(agent, message, max_retries=3, backoff=1):
    """Query with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            response = agent.query(message, return_metadata=True)
            
            if response.get("success"):
                return response
                
            # Handle specific errors
            error = response.get("error", "")
            if "rate limit" in error.lower():
                wait = backoff * (2 ** attempt)
                print(f"Rate limited. Waiting {wait}s...")
                time.sleep(wait)
                continue
            else:
                return response
                
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(backoff * (2 ** attempt))
            
    return {"success": False, "error": "Max retries exceeded"}
```

### Tool Execution Monitoring

```python
class MonitoredAgent(QwenAgent):
    def _execute_tool_call(self, tool_call):
        """Execute tool with monitoring."""
        result = super()._execute_tool_call(tool_call)
        
        # Log execution
        fn_name = tool_call.function.name
        success = result.get("success", False)
        
        if not success:
            print(f"⚠️  Tool {fn_name} failed: {result.get('error')}")
        else:
            print(f"✓ Tool {fn_name} succeeded")
            
        return result
```

## Performance Optimization

### Token Management

Control token usage:

```python
# Shorter responses
agent = QwenAgent(max_tokens=512)

# Adjust temperature for speed
agent = QwenAgent(temperature=0.3)  # Less creative, faster

# Reduce tool iteration limit
response = agent.query(message, max_tool_iterations=2)
```

### Batch Processing

Process multiple queries efficiently:

```python
def batch_query(agent, queries, reset_between=True):
    """Process multiple queries."""
    results = []
    
    for query in queries:
        if reset_between:
            agent.reset_conversation()
            
        result = agent.query(query, return_metadata=True)
        results.append({
            "query": query,
            "response": result.get("content"),
            "tool_calls": len(result.get("tool_calls", []))
        })
        
    return results

# Usage
queries = [
    "What's 2 + 2?",
    "Weather in Tokyo?",
    "Search for Python"
]

results = batch_query(agent, queries)
for r in results:
    print(f"Q: {r['query']}")
    print(f"A: {r['response']}\n")
```

### Caching Tool Results

```python
from functools import lru_cache
from tools.base import BaseTool

class CachedWeatherTool(BaseTool):
    name = "cached_weather"
    description = "Get cached weather data"
    
    @lru_cache(maxsize=100)
    def _fetch_weather(self, location: str):
        """Cached weather fetch."""
        # Expensive API call here
        return {"temperature": 20, "location": location}
    
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            },
            "required": ["location"]
        }
    
    def execute(self, location: str):
        return self._fetch_weather(location)
```

## Production Deployment

### Configuration Management

```python
from dataclasses import dataclass
from typing import List

@dataclass
class AgentConfig:
    model_name: str
    base_url: str
    temperature: float = 0.7
    max_tokens: int = 2048
    enabled_tools: List[str] = None
    
    @classmethod
    def from_env(cls):
        """Load from environment."""
        import os
        return cls(
            model_name=os.getenv("MODEL_NAME", "qwen3-4b"),
            base_url=os.getenv("LM_STUDIO_BASE_URL"),
            temperature=float(os.getenv("TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("MAX_TOKENS", "2048"))
        )

# Usage
config = AgentConfig.from_env()
agent = QwenAgent(
    model_name=config.model_name,
    base_url=config.base_url,
    temperature=config.temperature
)
```

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class LoggedAgent(QwenAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        
    def query(self, message, **kwargs):
        self.logger.info(f"Query: {message}")
        response = super().query(message, **kwargs)
        self.logger.info(f"Response: {response}")
        return response
```

### Health Checks

```python
def check_agent_health(agent):
    """Verify agent is functional."""
    checks = {
        "api_connection": False,
        "tools_loaded": False,
        "basic_query": False
    }
    
    # Test API connection
    try:
        agent.client.models.list()
        checks["api_connection"] = True
    except Exception as e:
        print(f"API connection failed: {e}")
        
    # Check tools
    checks["tools_loaded"] = len(agent.tools) > 0
    
    # Test basic query
    try:
        response = agent.query("test", return_metadata=True)
        checks["basic_query"] = response.get("success", False)
    except Exception as e:
        print(f"Basic query failed: {e}")
        
    return all(checks.values()), checks

# Usage
healthy, status = check_agent_health(agent)
print(f"Agent healthy: {healthy}")
print(f"Status: {status}")
```

## Advanced Patterns

### Multi-Agent System

```python
class AgentOrchestrator:
    """Coordinate multiple specialized agents."""
    
    def __init__(self):
        self.agents = {
            "weather": self._create_weather_agent(),
            "math": self._create_math_agent(),
            "research": self._create_research_agent()
        }
        
    def _create_weather_agent(self):
        agent = QwenAgent()
        agent.register_tool(WeatherTool())
        agent.set_system_message("You are a weather expert.")
        return agent
    
    def _create_math_agent(self):
        agent = QwenAgent()
        agent.register_tool(CalculatorTool())
        agent.set_system_message("You are a math expert.")
        return agent
    
    def _create_research_agent(self):
        agent = QwenAgent()
        agent.register_tool(WebSearchTool())
        agent.set_system_message("You are a research assistant.")
        return agent
    
    def route_query(self, query: str):
        """Route query to appropriate agent."""
        query_lower = query.lower()
        
        if "weather" in query_lower or "temperature" in query_lower:
            return self.agents["weather"].query(query)
        elif any(word in query_lower for word in ["calculate", "math", "solve"]):
            return self.agents["math"].query(query)
        elif "search" in query_lower or "find" in query_lower:
            return self.agents["research"].query(query)
        else:
            # Default to research agent
            return self.agents["research"].query(query)

# Usage
orchestrator = AgentOrchestrator()
response = orchestrator.route_query("What's the weather in Tokyo?")
```

### Streaming Responses

```python
def stream_query(agent, message):
    """Stream response as it's generated."""
    # Note: Requires streaming support in API
    call_params = {
        "model": agent.model_name,
        "messages": agent._prepare_messages() + [
            {"role": "user", "content": message}
        ],
        "tools": agent.tool_schemas,
        "stream": True
    }
    
    response = agent.client.chat.completions.create(**call_params)
    
    for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

### Chain of Thought

```python
def chain_of_thought_query(agent, problem):
    """Use CoT prompting."""
    cot_prompt = f"""
    Problem: {problem}
    
    Let's solve this step by step:
    1. First, identify what we need to find
    2. Then, determine what tools or information we need
    3. Execute the necessary steps
    4. Finally, provide the answer
    
    Please show your reasoning at each step.
    """
    
    return agent.query(cot_prompt)
```

### Tool Chaining

```python
def chain_tools(agent, tasks):
    """Chain multiple tool calls."""
    results = []
    context = ""
    
    for task in tasks:
        prompt = f"{context}\n\n{task}" if context else task
        response = agent.query(prompt, return_metadata=True)
        
        results.append(response)
        context = response.get("content", "")
        
    return results

# Usage
tasks = [
    "Get the weather in San Francisco",
    "Calculate what the temperature would be in Fahrenheit",
    "Search for typical weather patterns in that city"
]

results = chain_tools(agent, tasks)
```

## Best Practices

1. **Always handle errors gracefully**
2. **Reset conversation for unrelated queries**
3. **Use specific system messages for better results**
4. **Monitor token usage in production**
5. **Cache expensive tool calls**
6. **Log all interactions for debugging**
7. **Test tools independently first**
8. **Use type hints for better IDE support**
9. **Document custom tools thoroughly**
10. **Keep tool descriptions clear and concise**
