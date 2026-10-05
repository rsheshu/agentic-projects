import json
from typing import Any, Dict,List
from simple_mcp_server import SimpleMCPServer

DEBUG = False


class SimpleMCPClient:
    def __init__(self, server: SimpleMCPServer):
        self.server = server
        self._next_id = 1

    def _request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        request = {
            'jsonrpc': '2.0',
            'id': self._next_id,
            'method': method,
            'params': params,
        }
        if DEBUG:
            print(f'[CLIENT -> SERVER] {json.dumps(request)}')
        self._next_id += 1
        return self.send_request(request)

    def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        if DEBUG:
            print(f'[CLIENT -> SERVER] {json.dumps(request)}')
        response = self.server.handle_request(request)
        if DEBUG:
            print(f'[CLIENT <- SERVER] {json.dumps(response)}')
        return response

    def initialize(self, name: str = 'demo-client', version: str = '1.0.0'):
        return self._request(
            'initialize',
            {
                'protocolVersion': '2.0',
                'client': {'name': name, 'version': version},
            },
        )

    def list_tools(self):
        return self._request('tools/list', {})

    def call_tool(self, name: str, arguments: Dict[str, Any]):
        return self._request('tools/call', {'name': name, 'arguments': arguments})

    def tool_schemas_for_provider(self) -> List[Dict[str, Any]]:
        response = self.list_tools()
        if "error" in response:
            raise RuntimeError(response["error"].get("message", "Could not list MCP tools"))

        return [
            {
                "type": "function",
                "function": {
                    "name": declaration["name"],
                    "description": declaration["description"],
                    "parameters": declaration["parameters"],
                },
            }
            for declaration in response.get("result", {}).get("tools", [])
        ]
    