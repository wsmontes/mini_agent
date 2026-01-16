"""
Weather Tool Demo
Demonstrates weather-related queries and tool calling.
"""

from agent import QwenAgent
from tools import CurrentWeatherTool, ForecastWeatherTool
from datetime import datetime, timedelta


def main():
    print("=" * 60)
    print("Weather Tool Demo")
    print("=" * 60)
    
    # Initialize agent
    agent = QwenAgent(
        enable_thinking=False,
        auto_execute_tools=True
    )
    
    # Register weather tools
    agent.register_tool(CurrentWeatherTool())
    agent.register_tool(ForecastWeatherTool())
    
    print(f"\n✓ Registered {len(agent.tools)} weather tools")
    print(f"  - {', '.join(agent.tools.keys())}")
    
    # Example queries
    queries = [
        "What's the current temperature in San Francisco?",
        f"What will the temperature be in New York on {(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')}?",
        "Tell me the current temperature in London and Paris",
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'-' * 60}")
        print(f"Query {i}: {query}")
        print(f"{'-' * 60}")
        
        response = agent.query(query, return_metadata=True)
        
        if response.get("success"):
            # Show tool calls
            if tool_calls := response.get("tool_calls"):
                print("\n🛠️  Tool Calls:")
                for tc in tool_calls:
                    print(f"  • {tc['function_name']}")
                    print(f"    Args: {tc.get('arguments', {})}")
                    if tc.get("success"):
                        print(f"    Result: {tc.get('result', {})}")
                        
            # Show response
            print(f"\n💬 Response:")
            print(f"   {response.get('content', '')}")
        else:
            print(f"\n❌ Error: {response.get('error')}")
            
    print(f"\n{'=' * 60}")
    print("Demo completed!")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
