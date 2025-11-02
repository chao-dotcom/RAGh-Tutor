"""Tool registry for agents"""
from typing import Dict, Callable, Any, List, Optional
from pydantic import BaseModel
import asyncio
import logging

logger = logging.getLogger(__name__)


class Tool(BaseModel):
    """Tool definition"""
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Callable
    
    class Config:
        arbitrary_types_allowed = True


class ToolRegistry:
    """Registry for agent tools"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
    
    def register(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        function: Callable
    ):
        """Register a new tool"""
        tool = Tool(
            name=name,
            description=description,
            parameters=parameters,
            function=function
        )
        self.tools[name] = tool
        logger.info(f"Registered tool: {name}")
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get tool by name"""
        return self.tools.get(name)
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get tool schemas for LLM"""
        schemas = []
        for tool in self.tools.values():
            schema = {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.parameters
            }
            schemas.append(schema)
        return schemas
    
    async def execute_tool(
        self,
        tool_name: str,
        tool_input: Dict[str, Any]
    ) -> Any:
        """Execute a tool"""
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")
        
        # Execute tool function
        if asyncio.iscoroutinefunction(tool.function):
            result = await tool.function(**tool_input)
        else:
            result = tool.function(**tool_input)
        
        return result
    
    # Backward compatibility methods
    def get(self, name: str) -> Callable:
        """Get a tool function by name"""
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool {name} not found")
        return tool.function
    
    def list_tools(self) -> Dict[str, str]:
        """List all registered tools"""
        return {
            name: tool.description
            for name, tool in self.tools.items()
        }
    
    def execute(self, name: str, *args, **kwargs) -> Any:
        """Execute a tool (synchronous)"""
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool {name} not found")
        return tool.function(*args, **kwargs)

