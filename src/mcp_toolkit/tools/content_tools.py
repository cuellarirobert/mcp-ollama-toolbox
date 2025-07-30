"""
Generic content management tools following MCP standards
"""
import json
from typing import Dict, List, Any

class ContentToolsCollection:
    def __init__(self, content_manager):
        self.content_manager = content_manager
        
    def get_tool_manifest(self) -> Dict[str, Any]:
        """Return MCP-compliant tool manifest"""
        return {
            "tools": [
                {
                    "name": "get_content_items",
                    "description": "Retrieve all content items",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            ]
        }
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a content tool with MCP-compliant response"""
        try:
            if tool_name == "get_content_items":
                content = self.content_manager.get_content_items()
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({"content": content, "count": len(content)}, indent=2)
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