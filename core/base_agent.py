from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import uuid
import asyncio
from datetime import datetime

class AgentType(Enum):
    ORCHESTRATOR = "orchestrator"
    SPECIALIST = "specialist"
    TOOL = "tool"

class WorkflowType(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"

@dataclass
class AgentMessage:
    id: str
    sender_id: str
    receiver_id: str
    content: str
    message_type: str
    timestamp: datetime
    metadata: Dict[str, Any] = None

@dataclass
class AgentContext:
    session_id: str
    user_query: str
    conversation_history: List[Dict[str, str]]
    current_step: int
    workflow_state: Dict[str, Any]

class BaseAgent(ABC):
    def __init__(self, agent_id: str, agent_type: AgentType, name: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.name = name
        self.tools: List['BaseTool'] = []
        self.capabilities: List[str] = []
        
    @abstractmethod
    async def process(self, message: AgentMessage, context: AgentContext) -> str:
        pass
    
    def add_tool(self, tool: 'BaseTool'):
        self.tools.append(tool)
    
    async def use_tool(self, tool_name: str, **kwargs) -> Any:
        for tool in self.tools:
            if tool.name == tool_name:
                return await tool.execute(**kwargs)
        raise ValueError(f"Tool {tool_name} not found")
    
    def can_handle(self, query: str) -> float:
        """Return confidence score (0-1) for handling this query"""
        return 0.0
