"""Base Resource class and registry."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, ClassVar
import json

RESOURCE_REGISTRY: Dict[str, 'BaseResource'] = {}


def register_resource(cls):
    """Decorator to register a resource."""
    instance = cls()
    RESOURCE_REGISTRY[instance.name] = instance
    return cls


class BaseResource(ABC):
    """Base class for all resources."""
    
    name: ClassVar[str]
    description: ClassVar[str]
    
    @abstractmethod
    def get(self, subpath: Optional[str] = None) -> str:
        """Get resource content, optionally filtered by subpath."""
        pass
    
    def to_json(self, data: Any) -> str:
        """Convert data to JSON string."""
        return json.dumps(data, indent=2, default=str)
