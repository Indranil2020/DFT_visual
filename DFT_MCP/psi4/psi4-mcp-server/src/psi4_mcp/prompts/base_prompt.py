"""Base Prompt class and registry."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, ClassVar
from mcp.types import GetPromptResult, PromptMessage, PromptArgument

PROMPT_REGISTRY: Dict[str, 'BasePrompt'] = {}

def register_prompt(cls):
    instance = cls()
    PROMPT_REGISTRY[instance.name] = instance
    return cls

class BasePrompt(ABC):
    name: ClassVar[str]
    description: ClassVar[str]
    arguments: ClassVar[List[PromptArgument]]
    
    @abstractmethod
    def render(self, args: Dict[str, Any]) -> GetPromptResult:
        pass
