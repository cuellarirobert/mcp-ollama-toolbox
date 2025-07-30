"""
MCP Ollama Chat Interface
Provides a professional terminal chat experience with function calling
"""
import ollama
import json
import os
import time
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

class MCPOllamaChat:
    def __init__(self, model="llama3.1"):
        self.model = model
        self.client = ollama.Client()
        self.conversation_history = []
        self._cached_data = {}
        
        # Terminal colors for professional UX
        self.colors = {
            'blue': '\033[94m', 'green': '\033[92m', 'yellow': '\033[93m',
            'red': '\033[91m', 'purple': '\033[95m', 'cyan': '\033[96m',
            'white': '\033[97m', 'bold': '\033[1m', 'underline': '\033[4m',
            'end': '\033[0m', 'dim': '\033[2m'
        }
        
        # Will be populated by tool collections
        self.available_functions = {}
        self.function_descriptions = {}
        self.tool_schemas = []
        
    def register_tool_collection(self, collection_name: str, tool_collection):
        """Register a tool collection with the chat interface"""
        manifest = tool_collection.get_tool_manifest()
        
        for tool in manifest.get("tools", []):
            tool_name = tool["name"]
            self.available_functions[tool_name] = lambda tc=tool_collection, tn=tool_name, **kwargs: tc.execute_tool(tn, kwargs)
            self.function_descriptions[tool_name] = tool["description"]
            
            # Convert to Ollama function schema
            schema = {
                'type': 'function',
                'function': {
                    'name': tool_name,
                    'description': tool["description"],
                    'parameters': tool.get("inputSchema", {"type": "object", "properties": {}, "required": []})
                }
            }
            self.tool_schemas.append(schema)
    
    # UI Helper Methods
    def _colorize(self, text: str, color: str) -> str:
        return f"{self.colors.get(color, '')}{text}{self.colors['end']}"
    
    def _print_timestamp(self):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{self.colors['dim']}[{timestamp}]{self.colors['end']}", end=" ")
    
    def _animate_thinking(self, duration=1.5):
        frames = ["🤔", "💭", "🧠", "💡"]
        end_time = time.time() + duration
        i = 0
        while time.time() < end_time:
            print(f"\r{frames[i % len(frames)]} Analyzing your request...", end="", flush=True)
            time.sleep(0.3)
            i += 1
        print("\r" + " " * 30 + "\r", end="", flush=True)
    
    def _log_function_call(self, function_name: str, arguments: dict, step_num: int, total_steps: int):
        print(f"\n{self.colors['cyan']}┌─ Function Call #{step_num}/{total_steps}{self.colors['end']}")
        print(f"{self.colors['cyan']}│{self.colors['end']}")
        print(f"{self.colors['cyan']}├─ Function:{self.colors['end']} {self.colors['bold']}{function_name}{self.colors['end']}")
        print(f"{self.colors['cyan']}├─ Description:{self.colors['end']} {self.function_descriptions.get(function_name, 'No description')}")
        
        if arguments:
            print(f"{self.colors['cyan']}├─ Parameters:{self.colors['end']}")
            for key, value in arguments.items():
                print(f"{self.colors['cyan']}│  • {key}:{self.colors['end']} {self.colors['yellow']}{value}{self.colors['end']}")
        else:
            print(f"{self.colors['cyan']}├─ Parameters:{self.colors['end']} {self.colors['dim']}None{self.colors['end']}")
        
        print(f"{self.colors['cyan']}│{self.colors['end']}")
        print(f"{self.colors['cyan']}├─ MCP Payload Structure:{self.colors['end']}")
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": function_name,
                "arguments": arguments if arguments else {}
            }
        }
        payload_json = json.dumps(payload, indent=2)
        for line in payload_json.split('\n'):
            print(f"{self.colors['cyan']}│  {self.colors['dim']}{line}{self.colors['end']}")
        
        print(f"{self.colors['cyan']}│{self.colors['end']}")
        print(f"{self.colors['cyan']}└─ Executing...{self.colors['end']}", end="", flush=True)
    
    def _log_function_result(self, success: bool, message: str, data_summary: str = None):
        if success:
            print(f" {self.colors['green']}✅ Success{self.colors['end']}")
            if data_summary:
                print(f"   {self.colors['green']}└─{self.colors['end']} {data_summary}")
        else:
            print(f" {self.colors['red']}❌ Failed{self.colors['end']}")
            print(f"   {self.colors['red']}└─{self.colors['end']} {message}")
    
    def _get_data_summary(self, function_result: dict) -> str:
        """Generate summary from MCP response"""
        try:
            if function_result.get("isError"):
                return f"Error occurred"
            
            content = function_result.get("content", [])
            if content and len(content) > 0:
                text_content = content[0].get("text", "")
                try:
                    data = json.loads(text_content)
                    if isinstance(data, list):
                        return f"Retrieved {len(data)} items"
                    elif isinstance(data, dict):
                        if 'count' in data:
                            return f"Found {data['count']} items"
                        elif 'total_items' in data:
                            return f"Retrieved {data['total_items']} items"
                        else:
                            return "Retrieved data successfully"
                except:
                    return "Retrieved data successfully"
            return "Operation completed"
        except:
            return "Operation completed"
    
    def chat(self, message: str, system_prompt: str = None) -> str:
        """Main chat interface with MCP function calling"""
        
        # Handle special commands
        if message.lower() in ['help', '/help', '?']:
            self._show_help()
            return ""
        elif message.lower() in ['tools', '/tools', 'list tools']:
            self._list_available_tools()
            return ""
        
        self.conversation_history.append({"role": "user", "content": message})
        
        default_prompt = "You are a helpful assistant with access to various tools and functions. Use the available tools to help users with their requests."
        
        try:
            self._print_timestamp()
            self._animate_thinking()
            
            response = self.client.chat(
                model=self.model,
                messages=[{
                    'role': 'system',
                    'content': system_prompt or default_prompt
                }, {
                    'role': 'user', 
                    'content': message
                }],
                tools=self.tool_schemas,
            )

            if response.get('message', {}).get('tool_calls'):
                tool_calls = response['message']['tool_calls']
                
                print(f"{self.colors['bold']}🔧 Function Calling Required{self.colors['end']}")
                print(f"Ollama determined {self.colors['yellow']}{len(tool_calls)}{self.colors['end']} function call{'s' if len(tool_calls) > 1 else ''} needed:")
                
                messages = [
                    {'role': 'system', 'content': system_prompt or default_prompt},
                    {'role': 'user', 'content': message},
                    response['message']
                ]
                
                for i, tool_call in enumerate(tool_calls):
                    try:
                        function_name = tool_call['function']['name']
                        function_args = tool_call['function'].get('arguments', {})
                        
                        if isinstance(function_args, str):
                            function_args = json.loads(function_args) if function_args else {}
                        
                        self._log_function_call(function_name, function_args, i+1, len(tool_calls))
                        
                        if function_name in self.available_functions:
                            start_time = time.time()
                            function_result = self.available_functions[function_name](**function_args)
                            execution_time = time.time() - start_time
                            
                            # Handle MCP response format
                            if isinstance(function_result, dict) and 'content' in function_result:
                                success = not function_result.get('isError', False)
                                data_summary = self._get_data_summary(function_result)
                                self._log_function_result(success, "", f"{data_summary} (took {execution_time:.2f}s)")
                                
                                # Extract text content for Ollama
                                content_text = ""
                                for content_item in function_result.get('content', []):
                                    if content_item.get('type') == 'text':
                                        content_text += content_item.get('text', '')
                                
                                messages.append({
                                    'role': 'tool',
                                    'content': content_text,
                                    'tool_call_id': tool_call.get('id', 'unknown')
                                })
                            else:
                                # Fallback for non-MCP responses
                                self._log_function_result(True, "", f"Operation completed (took {execution_time:.2f}s)")
                                messages.append({
                                    'role': 'tool',
                                    'content': str(function_result),
                                    'tool_call_id': tool_call.get('id', 'unknown')
                                })
                        else:
                            self._log_function_result(False, f"Unknown function: {function_name}")
                            messages.append({
                                'role': 'tool',
                                'content': f"Error: Unknown function {function_name}",
                                'tool_call_id': tool_call.get('id', 'unknown')
                            })
                    except Exception as e:
                        self._log_function_result(False, str(e))
                        messages.append({
                            'role': 'tool',
                            'content': f"Error: {str(e)}",
                            'tool_call_id': tool_call.get('id', 'unknown')
                        })
                
                print(f"\n{self.colors['purple']}🧠 Processing Results & Generating Response...{self.colors['end']}")
                
                final_response = self.client.chat(model=self.model, messages=messages)
                self.conversation_history.append({"role": "assistant", "content": final_response['message']['content']})
                
                print(f"\n{self.colors['green']}✨ Response Ready!{self.colors['end']}\n")
                return final_response['message']['content']
            
            print(f"{self.colors['blue']}💭 Responding from knowledge...{self.colors['end']}\n")
            self.conversation_history.append({"role": "assistant", "content": response['message']['content']})
            return response['message']['content']
            
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            print(f"\n{self.colors['red']}❌ Error: {str(e)}{self.colors['end']}\n")
            return error_msg
    
    def _show_help(self):
        print(f"\n{self.colors['bold']}🔧 MCP Ollama Toolkit Help{self.colors['end']}")
        print(f"Available commands:")
        print(f"  {self.colors['cyan']}help{self.colors['end']} - Show this help")
        print(f"  {self.colors['cyan']}tools{self.colors['end']} - List available tools")
        print(f"  Ask any question to interact with the tools!")
    
    def _list_available_tools(self):
        print(f"\n{self.colors['bold']}🛠️ Available Tools{self.colors['end']}")
        if not self.available_functions:
            print("No tools registered yet.")
            return
            
        for tool_name, description in self.function_descriptions.items():
            print(f"  {self.colors['cyan']}{tool_name}{self.colors['end']}: {description}")