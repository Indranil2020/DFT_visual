"""
Base Tool Class for MCP Tools.

This module provides the abstract base class for all MCP tools,
implementing the MCP protocol interface and common functionality.

Key Classes:
    - BaseTool: Abstract base class for all tools
    - ToolInput: Base input schema
    - ToolOutput: Base output schema
    - ToolMetadata: Tool metadata for registration
    - ToolRegistry: Central registry for all tools
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, TypeVar, Generic, Type, ClassVar
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import json

from pydantic import BaseModel, Field

from psi4_mcp.models.errors import Result, CalculationError


logger = logging.getLogger(__name__)

# Type variables
TInput = TypeVar('TInput', bound='ToolInput')
TOutput = TypeVar('TOutput', bound='ToolOutput')


# =============================================================================
# TOOL ENUMS
# =============================================================================

class ToolCategory(str, Enum):
    """Tool categories for organization."""
    CORE = "core"
    VIBRATIONAL = "vibrational"
    PROPERTIES = "properties"
    SPECTROSCOPY = "spectroscopy"
    EXCITED_STATES = "excited_states"
    COUPLED_CLUSTER = "coupled_cluster"
    PERTURBATION = "perturbation_theory"
    CI = "configuration_interaction"
    MCSCF = "mcscf"
    SAPT = "sapt"
    SOLVATION = "solvation"
    DFT = "dft"
    BASIS = "basis_sets"
    ANALYSIS = "analysis"
    COMPOSITE = "composite"
    ADVANCED = "advanced"
    UTILITIES = "utilities"
    # Additional categories used by tools
    CORRELATED = "correlated"
    MULTISCALE = "multiscale"
    OPTIMIZATION = "optimization"
    THERMOCHEMISTRY = "thermochemistry"
    MULTIREFERENCE = "multireference"
    INTERMOLECULAR = "intermolecular"
    UTILITY = "utility"


class ToolStatus(str, Enum):
    """Tool execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# =============================================================================
# BASE SCHEMAS
# =============================================================================

class ToolInput(BaseModel):
    """
    Base input schema for all MCP tools.
    
    All tool inputs should inherit from this class.
    """
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"  # Allow additional fields
        validate_assignment = True


class ToolOutput(BaseModel):
    """
    Base output schema for all MCP tools.
    
    Attributes:
        success: Whether the tool executed successfully.
        message: Human-readable message.
        data: Tool-specific output data.
        error: Error information if failed.
        execution_time: Time taken in seconds.
        timestamp: Completion timestamp.
    """
    
    success: bool = True
    message: str = ""
    data: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
    
    def to_mcp_response(self) -> dict[str, Any]:
        """Convert to MCP response format."""
        return {
            "content": [
                {
                    "type": "text",
                    "text": self.message if self.success else f"Error: {self.error}",
                }
            ],
            "isError": not self.success,
            "_meta": {
                "success": self.success,
                "execution_time": self.execution_time,
                "timestamp": self.timestamp.isoformat(),
            },
        }
    
    @classmethod
    def from_result(
        cls,
        result: Result[Any],
        execution_time: Optional[float] = None,
    ) -> "ToolOutput":
        """Create ToolOutput from a Result."""
        if result.is_success:
            data = result.value
            if hasattr(data, "model_dump"):
                data = data.model_dump()
            elif hasattr(data, "__dict__"):
                data = vars(data)
            
            return cls(
                success=True,
                message="Calculation completed successfully",
                data=data if isinstance(data, dict) else {"result": data},
                execution_time=execution_time,
            )
        else:
            return cls(
                success=False,
                message="Calculation failed",
                error=str(result.error),
                execution_time=execution_time,
            )


# =============================================================================
# TOOL METADATA
# =============================================================================

@dataclass
class ToolMetadata:
    """
    Metadata for tool registration and discovery.
    
    Attributes:
        name: Unique tool name.
        description: Human-readable description.
        category: Tool category for organization.
        input_schema: JSON schema for input validation.
        version: Tool version string.
        author: Tool author.
        tags: Searchable tags.
        examples: Usage examples.
        deprecated: Whether tool is deprecated.
        replacement: Replacement tool if deprecated.
    """
    
    name: str
    description: str
    category: ToolCategory
    input_schema: dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"
    author: str = "psi4-mcp"
    tags: list[str] = field(default_factory=list)
    examples: list[dict[str, Any]] = field(default_factory=list)
    deprecated: bool = False
    replacement: Optional[str] = None
    
    def to_mcp_tool(self) -> dict[str, Any]:
        """Convert to MCP tool definition format."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": self.input_schema,
            },
        }


# =============================================================================
# BASE TOOL CLASS
# =============================================================================

class BaseTool(ABC, Generic[TInput, TOutput]):
    """
    Abstract base class for all MCP tools.
    
    This class defines the interface that all tools must implement.
    It handles common functionality like logging, validation, and
    error handling.
    
    Subclasses must implement:
        - _execute: Core tool logic
        - get_metadata: Return tool metadata
    
    Type Parameters:
        TInput: Input type (subclass of ToolInput)
        TOutput: Output type (subclass of ToolOutput)
    """
    
    # Class-level metadata (override in subclasses)
    name: ClassVar[str] = "base_tool"
    description: ClassVar[str] = "Base tool"
    category: ClassVar[ToolCategory] = ToolCategory.CORE
    version: ClassVar[str] = "1.0.0"
    
    def __init__(self):
        """Initialize the tool."""
        self._logger = logging.getLogger(f"{__name__}.{self.name}")
    
    # =========================================================================
    # ABSTRACT METHODS
    # =========================================================================
    
    @abstractmethod
    def _execute(self, input_data: TInput) -> Result[TOutput]:
        """
        Execute the tool logic.
        
        Subclasses must implement this method.
        
        Args:
            input_data: Validated input data.
            
        Returns:
            Result containing output or error.
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_input_schema(cls) -> dict[str, Any]:
        """
        Get the JSON schema for input validation.
        
        Returns:
            JSON schema dictionary.
        """
        pass
    
    # =========================================================================
    # PUBLIC METHODS
    # =========================================================================
    
    def run(self, input_data: dict[str, Any]) -> ToolOutput:
        """
        Run the tool with the given input.
        
        This is the main entry point called by the MCP server.
        
        Args:
            input_data: Raw input dictionary from MCP request.
            
        Returns:
            ToolOutput with results or error.
        """
        start_time = datetime.now()
        
        try:
            # Validate and parse input
            parsed_input = self._validate_input(input_data)
            if isinstance(parsed_input, ToolOutput):
                return parsed_input  # Validation error
            
            self._logger.info(f"Executing {self.name}")
            
            # Execute tool logic
            result = self._execute(parsed_input)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Convert result to output
            output = ToolOutput.from_result(result, execution_time)
            
            self._logger.info(
                f"Completed {self.name} in {execution_time:.2f}s "
                f"(success={output.success})"
            )
            
            return output
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self._logger.exception(f"Error in {self.name}: {e}")
            
            return ToolOutput(
                success=False,
                message="Tool execution failed",
                error=str(e),
                execution_time=execution_time,
            )
    
    async def run_async(self, input_data: dict[str, Any]) -> ToolOutput:
        """
        Async version of run for non-blocking execution.
        
        Args:
            input_data: Raw input dictionary from MCP request.
            
        Returns:
            ToolOutput with results or error.
        """
        # Default implementation just calls sync version
        # Subclasses can override for true async support
        import asyncio
        return await asyncio.get_event_loop().run_in_executor(
            None, self.run, input_data
        )
    
    @classmethod
    def get_metadata(cls) -> ToolMetadata:
        """
        Get tool metadata for registration.
        
        Returns:
            ToolMetadata instance.
        """
        return ToolMetadata(
            name=cls.name,
            description=cls.description,
            category=cls.category,
            input_schema=cls.get_input_schema(),
            version=cls.version,
        )
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _validate_input(
        self,
        input_data: dict[str, Any],
    ) -> TInput | ToolOutput:
        """
        Validate and parse input data.
        
        Args:
            input_data: Raw input dictionary.
            
        Returns:
            Parsed input or ToolOutput with error.
        """
        try:
            # Get input class from type hints
            input_class = self._get_input_class()
            if input_class is None:
                return input_data  # No validation
            
            return input_class(**input_data)
            
        except Exception as e:
            self._logger.warning(f"Input validation failed: {e}")
            return ToolOutput(
                success=False,
                message="Invalid input",
                error=str(e),
            )
    
    def _get_input_class(self) -> Optional[Type[ToolInput]]:
        """Get the input class from generic type parameters."""
        # Try to extract from __orig_bases__
        for base in getattr(self.__class__, '__orig_bases__', []):
            if hasattr(base, '__args__') and len(base.__args__) >= 1:
                input_type = base.__args__[0]
                if isinstance(input_type, type) and issubclass(input_type, ToolInput):
                    return input_type
        return None


# =============================================================================
# TOOL REGISTRY
# =============================================================================

class ToolRegistry:
    """
    Central registry for all MCP tools.
    
    Provides tool discovery, registration, and lookup functionality.
    """
    
    _instance: Optional["ToolRegistry"] = None
    _tools: dict[str, Type[BaseTool]] = {}
    _metadata: dict[str, ToolMetadata] = {}
    
    def __new__(cls) -> "ToolRegistry":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def register(cls, tool_class: Type[BaseTool]) -> Type[BaseTool]:
        """
        Register a tool class.
        
        Args:
            tool_class: Tool class to register.
            
        Returns:
            The registered tool class (for decorator use).
        """
        metadata = tool_class.get_metadata()
        cls._tools[metadata.name] = tool_class
        cls._metadata[metadata.name] = metadata
        
        logger.debug(f"Registered tool: {metadata.name}")
        return tool_class
    
    @classmethod
    def get(cls, name: str) -> Optional[Type[BaseTool]]:
        """
        Get a tool class by name.
        
        Args:
            name: Tool name.
            
        Returns:
            Tool class or None if not found.
        """
        return cls._tools.get(name)
    
    @classmethod
    def get_instance(cls, name: str) -> Optional[BaseTool]:
        """
        Get a tool instance by name.
        
        Args:
            name: Tool name.
            
        Returns:
            Tool instance or None if not found.
        """
        tool_class = cls.get(name)
        if tool_class:
            return tool_class()
        return None
    
    @classmethod
    def list_tools(cls) -> list[ToolMetadata]:
        """
        List all registered tools.
        
        Returns:
            List of tool metadata.
        """
        return list(cls._metadata.values())
    
    @classmethod
    def list_by_category(cls, category: ToolCategory) -> list[ToolMetadata]:
        """
        List tools by category.
        
        Args:
            category: Tool category to filter by.
            
        Returns:
            List of matching tool metadata.
        """
        return [m for m in cls._metadata.values() if m.category == category]
    
    @classmethod
    def search(cls, query: str) -> list[ToolMetadata]:
        """
        Search tools by name, description, or tags.
        
        Args:
            query: Search query string.
            
        Returns:
            List of matching tool metadata.
        """
        query_lower = query.lower()
        results = []
        
        for metadata in cls._metadata.values():
            if (query_lower in metadata.name.lower() or
                query_lower in metadata.description.lower() or
                any(query_lower in tag.lower() for tag in metadata.tags)):
                results.append(metadata)
        
        return results
    
    @classmethod
    def to_mcp_tools(cls) -> list[dict[str, Any]]:
        """
        Convert all tools to MCP tool definitions.
        
        Returns:
            List of MCP tool definition dictionaries.
        """
        return [m.to_mcp_tool() for m in cls._metadata.values()]
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registered tools (for testing)."""
        cls._tools.clear()
        cls._metadata.clear()


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def register_tool(tool_class: Type[BaseTool]) -> Type[BaseTool]:
    """
    Decorator to register a tool class.
    
    Usage:
        @register_tool
        class MyTool(BaseTool):
            ...
    """
    return ToolRegistry.register(tool_class)


def get_tool(name: str) -> Optional[BaseTool]:
    """
    Get a tool instance by name.
    
    Args:
        name: Tool name.
        
    Returns:
        Tool instance or None.
    """
    return ToolRegistry.get_instance(name)


def list_tools(category: Optional[ToolCategory] = None) -> list[ToolMetadata]:
    """
    List available tools.
    
    Args:
        category: Optional category filter.
        
    Returns:
        List of tool metadata.
    """
    if category:
        return ToolRegistry.list_by_category(category)
    return ToolRegistry.list_tools()


def run_tool(name: str, input_data: dict[str, Any]) -> ToolOutput:
    """
    Run a tool by name.
    
    Args:
        name: Tool name.
        input_data: Tool input data.
        
    Returns:
        Tool output.
    """
    tool = get_tool(name)
    if tool is None:
        return ToolOutput(
            success=False,
            message=f"Tool not found: {name}",
            error=f"No tool registered with name '{name}'",
        )
    
    return tool.run(input_data)


# Module-level alias for compatibility
TOOL_REGISTRY = ToolRegistry
