from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseTool(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Return tool schema for agent understanding"""
        pass
