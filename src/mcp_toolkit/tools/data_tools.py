"""
Generic data access tools following MCP standards
"""
import json
from typing import Dict, List, Any

class DataToolsCollection:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        
    def get_tool_manifest(self) -> Dict[str, Any]:
        """Return MCP-compliant tool manifest"""
        return {
            "tools": [
                {
                    "name": "get_all_items",
                    "description": "Retrieve all available data items",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "get_item_by_id",
                    "description": "Get specific item by ID",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "item_id": {
                                "type": "string",
                                "description": "Unique identifier for the item"
                            }
                        },
                        "required": ["item_id"]
                    }
                },
                {
                    "name": "search_items",
                    "description": "Search items by query",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query string"
                            }
                        },
                        "required": ["query"]
                    }
                }
            ]
        }
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with MCP-compliant response"""
        try:
            if tool_name == "get_all_items":
                data = self.data_manager.get_all_items()
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({"items": data, "count": len(data)}, indent=2)
                        }
                    ]
                }
            elif tool_name == "get_item_by_id":
                item_id = arguments.get("item_id")
                item = self.data_manager.get_item_by_id(item_id)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({"item": item}, indent=2)
                        }
                    ]
                }
            elif tool_name == "search_items":
                query = arguments.get("query", "")
                results = self.data_manager.search_items(query)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "query": query,
                                "results": results,
                                "count": len(results)
                            }, indent=2)
                        }
                    ]
                }
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({"error": f"Unknown tool: {tool_name}"}, indent=2)
                        }
                    ],
                    "isError": True
                }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({"error": str(e)}, indent=2)
                    }
                ],
                "isError": True
            }