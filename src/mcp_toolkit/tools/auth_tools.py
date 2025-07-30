"""
OAuth2 authentication tools with simple config file management
"""
import json
from typing import Dict, List, Any
from ..core.config_manager import ConfigManager

class AuthToolsCollection:
    def __init__(self, config_manager: ConfigManager = None):
        self.config_manager = config_manager or ConfigManager()
        self._auth_managers = {}  # Cache auth managers by environment
        
    def get_tool_manifest(self) -> Dict[str, Any]:
        """Return MCP-compliant tool manifest"""
        return {
            "tools": [
                {
                    "name": "get_oauth_token",
                    "description": "Get OAuth2 bearer token (uses current environment from config file)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "scope": {
                                "type": "string",
                                "description": "OAuth2 scopes (optional, uses default from config)",
                                "default": ""
                            },
                            "environment": {
                                "type": "string",
                                "description": "Override environment (optional, uses current from config)"
                            }
                        },
                        "required": []
                    }
                },
                {
                    "name": "switch_environment",
                    "description": "Switch to a different environment (development, staging, production)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "environment": {
                                "type": "string",
                                "description": "Environment to switch to",
                                "enum": ["development", "staging", "production"]
                            }
                        },
                        "required": ["environment"]
                    }
                },
                {
                    "name": "show_config_status",
                    "description": "Show current configuration status and available environments",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "create_config_file",
                    "description": "Create a configuration file template for OAuth settings",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "refresh_oauth_token",
                    "description": "Refresh an OAuth2 token using refresh token",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "refresh_token": {
                                "type": "string",
                                "description": "Refresh token"
                            }
                        },
                        "required": ["refresh_token"]
                    }
                }
            ]
        }
    
    def _get_auth_manager(self, environment: str = None):
        """Get OAuth manager for specified environment"""
        env = environment or self.config_manager.get_current_environment()
        
        if env not in self._auth_managers:
            config = self.config_manager.get_oauth_config(env)
            
            # Import here to avoid circular imports
            from .oauth_manager import OAuth2Manager
            self._auth_managers[env] = OAuth2Manager(
                client_id=config["client_id"],
                client_secret=config["client_secret"],
                token_url=config["token_url"],
                auth_url=config.get("auth_url"),
                redirect_uri=config.get("redirect_uri")
            )
        
        return self._auth_managers[env]
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an auth tool with MCP-compliant response"""
        try:
            if tool_name == "get_oauth_token":
                environment = arguments.get("environment")
                scope = arguments.get("scope") or self.config_manager.get_oauth_config(environment).get("default_scope", "")
                
                auth_manager = self._get_auth_manager(environment)
                result = auth_manager.get_oauth_token("client_credentials", scope)
                
                # Add environment info to response
                result["environment"] = environment or self.config_manager.get_current_environment()
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            
            elif tool_name == "switch_environment":
                environment = arguments.get("environment")
                self.config_manager.set_current_environment(environment)
                
                # Clear cached auth manager for clean switch
                if environment in self._auth_managers:
                    del self._auth_managers[environment]
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "status": "success",
                                "message": f"Switched to {environment} environment",
                                "current_environment": environment
                            }, indent=2)
                        }
                    ]
                }
            
            elif tool_name == "show_config_status":
                status = self.config_manager.show_config_status()
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(status, indent=2)
                        }
                    ]
                }
            
            elif tool_name == "create_config_file":
                self.config_manager.create_config_file()
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "status": "success",
                                "message": "Configuration file created",
                                "config_file": self.config_manager.config_file,
                                "instructions": [
                                    "1. Open the config file in your text editor",
                                    "2. Add your client_id and client_secret for each environment",
                                    "3. Update URLs if needed",
                                    "4. Save the file",
                                    "5. Use 'show config status' to verify"
                                ]
                            }, indent=2)
                        }
                    ]
                }
            
            elif tool_name == "refresh_oauth_token":
                refresh_token = arguments.get("refresh_token")
                auth_manager = self._get_auth_manager()
                result = auth_manager.refresh_oauth_token(refresh_token)
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
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
                        "text": json.dumps({
                            "error": str(e),
                            "suggestion": "Try 'create config file' if you haven't set up OAuth credentials yet"
                        }, indent=2)
                    }
                ],
                "isError": True
            }