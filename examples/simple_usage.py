"""
Simple usage example demonstrating basic agent setup and usage.
"""

from agent import QwenAgent
from tools import WeatherTool, CalculatorTool


def main():
    """Simple example of using the agent."""
    
    # 1. Create the agent
    agent = QwenAgent()
    
    # 2. Register tools
    agent.register_tool(WeatherTool())
    agent.register_tool(CalculatorTool())
    
    # 3. Set system message (optional)
    agent.set_system_message(
        "You are a helpful assistant. Use tools when necessary."
    )
    
    # 4. Query the agent
    response = agent.query("What's the weather in Tokyo?")
    print("Response:", response)
    
    # 5. Continue conversation
    response = agent.query("And what's 42 * 37?")
    print("Response:", response)
    
    # 6. Get detailed metadata
    response = agent.query(
        "Calculate the square root of 256",
        return_metadata=True
    )
    
    print("\nDetailed response:")
    print(f"  Success: {response['success']}")
    print(f"  Content: {response['content']}")
    print(f"  Tool calls: {len(response.get('tool_calls', []))}")


if __name__ == "__main__":
    main()
