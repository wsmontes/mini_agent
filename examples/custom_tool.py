"""
Custom Tool Example
Demonstrates how to create and use custom tools.
"""

from agent import QwenAgent
from tools.base import BaseTool
from typing import Dict, Any
import random


class DiceRollTool(BaseTool):
    """Roll dice with specified sides."""
    
    name = "roll_dice"
    description = "Roll one or more dice with specified number of sides"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "num_dice": {
                    "type": "integer",
                    "description": "Number of dice to roll (1-10)",
                    "minimum": 1,
                    "maximum": 10
                },
                "num_sides": {
                    "type": "integer",
                    "description": "Number of sides on each die (4, 6, 8, 10, 12, 20)",
                    "enum": [4, 6, 8, 10, 12, 20]
                }
            },
            "required": ["num_dice", "num_sides"]
        }
        
    def execute(self, num_dice: int, num_sides: int) -> Dict[str, Any]:
        """Roll the dice."""
        rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
        
        return {
            "num_dice": num_dice,
            "num_sides": num_sides,
            "rolls": rolls,
            "total": sum(rolls),
            "formatted": f"Rolled {num_dice}d{num_sides}: {rolls} = {sum(rolls)}"
        }


class CoinFlipTool(BaseTool):
    """Flip a coin."""
    
    name = "flip_coin"
    description = "Flip a coin and get heads or tails"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "num_flips": {
                    "type": "integer",
                    "description": "Number of times to flip (1-10)",
                    "minimum": 1,
                    "maximum": 10
                }
            },
            "required": ["num_flips"]
        }
        
    def execute(self, num_flips: int = 1) -> Dict[str, Any]:
        """Flip the coin."""
        flips = [random.choice(["heads", "tails"]) for _ in range(num_flips)]
        
        return {
            "num_flips": num_flips,
            "results": flips,
            "heads": flips.count("heads"),
            "tails": flips.count("tails")
        }


def main():
    print("=" * 60)
    print("Custom Tool Example")
    print("=" * 60)
    
    # Initialize agent
    agent = QwenAgent()
    
    # Register custom tools
    agent.register_tool(DiceRollTool())
    agent.register_tool(CoinFlipTool())
    
    print(f"\n✓ Registered custom tools:")
    for tool_name in agent.tools.keys():
        print(f"  • {tool_name}")
    
    # Example queries
    queries = [
        "Roll 3 six-sided dice",
        "Flip a coin 5 times",
        "Roll 2 twenty-sided dice and tell me the total",
    ]
    
    for query in queries:
        print(f"\n{'-' * 60}")
        print(f"Query: {query}")
        print(f"{'-' * 60}")
        
        response = agent.query(query)
        print(f"\nResponse: {response}")
        
    print(f"\n{'=' * 60}")
    print("Demo completed!")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
