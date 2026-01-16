"""
Multi-Tool Demo
Demonstrates complex queries requiring multiple tools.
"""

from agent import QwenAgent
from tools import (
    CurrentWeatherTool,
    ForecastWeatherTool,
    CalculatorTool,
    WebSearchTool,
    FileListTool
)


def main():
    print("=" * 60)
    print("Multi-Tool Agent Demo")
    print("=" * 60)
    
    # Initialize agent with thinking mode
    agent = QwenAgent(
        enable_thinking=False,
        auto_execute_tools=True
    )
    
    # Register multiple tools
    tools = [
        CurrentWeatherTool(),
        ForecastWeatherTool(),
        CalculatorTool(),
        WebSearchTool(),
        FileListTool()
    ]
    
    for tool in tools:
        agent.register_tool(tool)
        
    print(f"\n✓ Registered {len(agent.tools)} tools:")
    for tool_name in agent.tools.keys():
        print(f"  • {tool_name}")
    
    # Complex queries requiring multiple tools
    queries = [
        "What's the temperature in San Francisco and New York right now? "
        "Then calculate the difference.",
        
        "Search the web for 'Python programming tutorials' and list "
        "the files in the current directory.",
        
        "Calculate 15 * 23, then tell me the weather for that temperature value.",
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'=' * 60}")
        print(f"Complex Query {i}:")
        print(f"{'-' * 60}")
        print(f"{query}")
        print(f"{'=' * 60}")
        
        response = agent.query(query, return_metadata=True)
        
        if response.get("success"):
            # Show tool usage
            if tool_calls := response.get("tool_calls"):
                print(f"\n🛠️  Used {len(tool_calls)} tools:")
                for j, tc in enumerate(tool_calls, 1):
                    status = "✓" if tc.get("success") else "✗"
                    print(f"  {j}. {status} {tc['function_name']}")
                    
            # Show response
            print(f"\n💬 Agent Response:")
            print(f"{'-' * 60}")
            content = response.get('content', '')
            for line in content.split('\n'):
                print(f"   {line}")
                
            print(f"\n📊 Stats:")
            print(f"   Iterations: {response.get('iterations', 0)}")
            print(f"   Finish reason: {response.get('finish_reason', 'unknown')}")
        else:
            print(f"\n❌ Error: {response.get('error')}")
            
    print(f"\n{'=' * 60}")
    print("Demo completed!")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
