"""Calculator tool for mathematical operations."""

from typing import Dict, Any
import math
import operator
from tools.base import BaseTool


class CalculatorTool(BaseTool):
    """Perform mathematical calculations and expressions."""
    
    name = "calculator"
    description = (
        "Evaluate mathematical expressions and perform calculations. "
        "Supports basic arithmetic, trigonometry, and common math functions."
    )
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": (
                        "Mathematical expression to evaluate. "
                        "Examples: '2 + 2', 'sqrt(16)', 'sin(pi/2)', '(5 * 3) + 10'"
                    )
                }
            },
            "required": ["expression"]
        }
        
    def execute(self, expression: str) -> Dict[str, Any]:
        """
        Evaluate a mathematical expression safely.
        
        Args:
            expression: Math expression as string
            
        Returns:
            Result or error message
        """
        # Safe namespace for evaluation
        safe_namespace = {
            # Math functions
            "sqrt": math.sqrt,
            "pow": math.pow,
            "abs": abs,
            "round": round,
            "floor": math.floor,
            "ceil": math.ceil,
            
            # Trigonometry
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "asin": math.asin,
            "acos": math.acos,
            "atan": math.atan,
            
            # Logarithms
            "log": math.log,
            "log10": math.log10,
            "log2": math.log2,
            "exp": math.exp,
            
            # Constants
            "pi": math.pi,
            "e": math.e,
            
            # Basic operators
            "max": max,
            "min": min,
            "sum": sum,
        }
        
        try:
            # Clean the expression
            expression = expression.strip()
            
            # Evaluate safely
            result = eval(expression, {"__builtins__": {}}, safe_namespace)
            
            return {
                "expression": expression,
                "result": result,
                "formatted": str(result)
            }
            
        except ZeroDivisionError:
            return {
                "expression": expression,
                "error": "Division by zero"
            }
        except (SyntaxError, NameError, TypeError) as e:
            return {
                "expression": expression,
                "error": f"Invalid expression: {str(e)}"
            }
        except Exception as e:
            return {
                "expression": expression,
                "error": f"Calculation error: {str(e)}"
            }


class SimpleCalculatorTool(BaseTool):
    """Simple arithmetic calculator for basic operations."""
    
    name = "simple_calculator"
    description = "Perform basic arithmetic operations: add, subtract, multiply, divide"
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "The arithmetic operation to perform"
                },
                "a": {
                    "type": "number",
                    "description": "First number"
                },
                "b": {
                    "type": "number",
                    "description": "Second number"
                }
            },
            "required": ["operation", "a", "b"]
        }
        
    def execute(self, operation: str, a: float, b: float) -> Dict[str, Any]:
        """Perform simple arithmetic."""
        operations = {
            "add": operator.add,
            "subtract": operator.sub,
            "multiply": operator.mul,
            "divide": operator.truediv
        }
        
        try:
            if operation == "divide" and b == 0:
                return {
                    "error": "Cannot divide by zero",
                    "operation": operation,
                    "a": a,
                    "b": b
                }
                
            result = operations[operation](a, b)
            
            return {
                "operation": operation,
                "a": a,
                "b": b,
                "result": result,
                "formatted": f"{a} {operation} {b} = {result}"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "operation": operation,
                "a": a,
                "b": b
            }
