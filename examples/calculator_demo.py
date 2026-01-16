"""
Calculator Tool Demo
Demonstrates mathematical calculations with the agent.
"""

from agent import QwenAgent
from tools import CalculatorTool


def main():
    print("=" * 60)
    print("Calculator Tool Demo")
    print("=" * 60)
    
    # Initialize agent
    agent = QwenAgent(
        enable_thinking=False,
        auto_execute_tools=True
    )
    
    # Register calculator tool
    agent.register_tool(CalculatorTool())
    
    print(f"\n✓ Registered calculator tool")
    
    # Example queries
    queries = [
        "What is 25 multiplied by 4?",
        "Calculate the square root of 144",
        "What is sin(pi/2)?",
        "Solve: (15 + 27) * 3 - 10",
        "What is 2 to the power of 10?",
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'-' * 60}")
        print(f"Query {i}: {query}")
        print(f"{'-' * 60}")
        
        response = agent.query(query, return_metadata=True)
        
        if response.get("success"):
            # Show tool calls
            if tool_calls := response.get("tool_calls"):
                print("\n🛠️  Tool Call:")
                for tc in tool_calls:
                    if tc.get("success"):
                        result = tc.get("result", {})
                        print(f"  Expression: {result.get('expression')}")
                        print(f"  Result: {result.get('result')}")
                        
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
