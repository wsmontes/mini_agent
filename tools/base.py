"""Base tool class for creating custom tools."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseTool(ABC):
    """
    Abstract base class for all tools.
    
    Subclasses must implement:
    - name: Tool identifier
    - description: What the tool does
    - get_parameters(): JSON Schema for parameters
    - execute(**kwargs): Tool logic
    """
    
    name: str = "base_tool"
    description: str = "Base tool class"
    
    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """
        Return JSON Schema for tool parameters.
        
        Example:
        {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Description"
                }
            },
            "required": ["param1"]
        }
        """
        pass
        
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool logic.
        
        Args:
            **kwargs: Parameters matching the schema
            
        Returns:
            Dictionary with results
        """
        pass
        
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name}>"
