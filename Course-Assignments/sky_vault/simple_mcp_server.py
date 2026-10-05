import inspect
from typing import Any, Dict

from tools_registry import ToolRegistry

DEBUG = False


class SimpleMCPServer:
    def __init__(
        self,
        registry: ToolRegistry,
        name: str = 'demo-mcp-server',
        version: str = '1.0.0',
    ):
        self.registry = registry
        self.name = name
        self.version = version
        if DEBUG:
            print(f'[SERVER initialized] name={self.name}, version={self.version}')

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        request_id = request.get('id') if isinstance(request, dict) else None
        if DEBUG:
            print(f'[SERVER received] {request}')

        if not isinstance(request, dict) or any(
            field not in request for field in ('jsonrpc', 'method', 'params', 'id')
        ) or request['jsonrpc'] != '2.0':
            return self._send_response(self._error(request_id, -32600, 'Invalid Request'))

        if not isinstance(request['method'], str) or not isinstance(request['params'], dict):
            return self._send_response(self._error(request_id, -32600, 'Invalid Request'))

        try:
            result = self._dispatch(request['method'], request['params'])
        except KeyError as error:
            return self._send_response(self._error(request_id, -32602, f'Missing required argument: {error.args[0]}'))
        except ValueError as error:
            code = -32601 if str(error).startswith('Unknown method:') else -32001
            return self._send_response(self._error(request_id, code, str(error)))
        except TypeError as error:
            return self._send_response(self._error(request_id, -32602, str(error)))

        return self._send_response({'jsonrpc': '2.0', 'id': request_id, 'result': result})

    @staticmethod
    def _send_response(response: Dict[str, Any]) -> Dict[str, Any]:
        if DEBUG:
            print(f'[SERVER -> HOST] {response}')
        return response

    def _dispatch(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if method == 'initialize':
            client = params.get('client', {})
            return {
                'protocolVersion': params.get('protocolVersion', '2.0'),
                'serverInfo': {'name': self.name, 'version': self.version},
                'clientInfo': client,
            }

        if method == 'tools/list':
            return {'tools': self.registry.list_tools()}

        if method == 'tools/call':
            tool_name = params['name']
            arguments = params.get('arguments', {})
            if not isinstance(arguments, dict):
                raise TypeError('arguments must be an object')
            if DEBUG:
                print(f'[SERVER -> HOST] Calling tool: {tool_name} with arguments: {arguments}')
            tool = self.registry._tools.get(tool_name)
            if tool is None:
                raise ValueError(f'Unknown tool: {tool_name}')
            #inspect.signature(tool.handler).bind(**arguments)
            return self.registry.call_tool(tool_name, arguments)

        raise ValueError(f'Unknown method: {method}')

    @staticmethod
    def _error(request_id: Any, code: int, message: str) -> Dict[str, Any]:
        return {
            'jsonrpc': '2.0',
            'id': request_id,
            'error': {'code': code, 'message': message},
        }