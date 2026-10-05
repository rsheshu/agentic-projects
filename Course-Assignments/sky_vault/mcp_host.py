
import json
from typing import Any, Dict
from simple_mcp_client import SimpleMCPClient

DEBUG = False


class MCPHost:
    def __init__(self, client: SimpleMCPClient):
        self.client = client

    def discover_tools(self):
        if DEBUG:
            print('[HOST -> CLIENT] list_tools()')
        response = self.client.list_tools()
        self._validate_response(response)
        if DEBUG:
            print(f'[HOST <- CLIENT] {json.dumps(response)}')
        return response['result']['tools']

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]):
        if DEBUG:
            print(f'[HOST -> CLIENT] call_tool({tool_name}, {arguments})')
        response = self.client.call_tool(tool_name, arguments)
        self._validate_response(response)
        if DEBUG:
            print(f'[HOST <- CLIENT] {json.dumps(response)}')
        return response

    def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        self._validate_request(request)
        if DEBUG:
            print(f'[HOST -> CLIENT] {json.dumps(request)}')
        response = self.client.send_request(request)
        self._validate_response(response, request['id'])
        if DEBUG:
            print(f'[HOST <- CLIENT] {json.dumps(response)}')
        return response

    @staticmethod
    def _validate_request(request: Dict[str, Any]) -> None:
        if not isinstance(request, dict) or any(
            field not in request for field in ('jsonrpc', 'id', 'method', 'params')
        ):
            raise ValueError('Invalid JSON-RPC request')
        if request['jsonrpc'] != '2.0' or not isinstance(request['method'], str):
            raise ValueError('Invalid JSON-RPC request')
        if not isinstance(request['params'], dict):
            raise ValueError('Invalid JSON-RPC request')

    @staticmethod
    def _validate_response(response: Dict[str, Any], request_id: Any = None) -> None:
        if not isinstance(response, dict):
            raise ValueError('Invalid JSON-RPC response')
        if response.get('jsonrpc') != '2.0' or 'id' not in response:
            raise ValueError('Invalid JSON-RPC response')
        if request_id is not None and response['id'] != request_id:
            raise ValueError('JSON-RPC response id does not match request id')

        has_result = 'result' in response
        has_error = 'error' in response
        if has_result == has_error:
            raise ValueError('JSON-RPC response must contain exactly one of result or error')

        if has_error:
            error = response['error']
            if not isinstance(error, dict) or not isinstance(error.get('code'), int):
                raise ValueError('Invalid JSON-RPC error response')
            if not isinstance(error.get('message'), str):
                raise ValueError('Invalid JSON-RPC error response')


def main() -> None:
    from simple_mcp_server import SimpleMCPServer
    from tools_inventory import tool_registry

    host = MCPHost(SimpleMCPClient(SimpleMCPServer(tool_registry)))
    requests = [
        {
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'tools/call',
            'params': {
                'name': 'find_available_gate',
                'arguments': {'terminal': 'Terminal 2'},
            },
        },
        {
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'tools/call',
            'params': {
                'name': 'find_gate',
                'arguments': {'terminal': 'Terminal 2'},
            },
        },
        {
            'jsonrpc': '2.0',
            'id': 4,
            'method': 'tools/call',
            'params': {
                'name': 'find_available_gate',
                'arguments': {},
            },
        },
    ]

    for request in requests:
        print(json.dumps(host.send_request(request), indent=2))


if __name__ == '__main__':
    main()

