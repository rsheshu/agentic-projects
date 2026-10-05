from dataclasses import dataclass
from typing import Callable, Dict, Any, Iterable, List
import json

DEBUG = False


@dataclass
class ToolDescription:
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable[..., Any]


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolDescription] = {}
        if DEBUG:
            print('[REGISTRY initialized]')

    def register(self, tool: ToolDescription):
        self._tools[tool.name] = tool
        if DEBUG:
            print(f'[REGISTRY registered] {tool.name}')

    def register_tools(self, tools: ToolDescription | Iterable[ToolDescription]):
        if isinstance(tools, ToolDescription):
            tools = [tools]

        for tool in tools:
            self.register(tool)

    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': t.name,
                'description': t.description,
                'parameters': t.parameters,
            }
            for t in self._tools.values()
        ]

    def call_tool(self, name: str, arguments: Dict[str, Any]):
        if name not in self._tools:
            raise ValueError(f'Unknown tool: {name}')
        print(f'[REGISTRY calling] {name} with arguments: {json.dumps(arguments)}')
        return self._tools[name].handler(**arguments)

