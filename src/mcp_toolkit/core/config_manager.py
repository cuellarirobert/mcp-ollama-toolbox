"""
Simple configuration management for MCP Toolkit
Config file stored in project root for easy access
"""
import os
import json
from typing import Dict, Any, Optional
from pathlib import Path

class ConfigManager:
    def __init__(self, config_file: str = None):
        # Default to project root directory
        if config_file:
            self.config_file = config_file
        else:
            # Find project root (where this is likely being run from)
            current_dir = os.getcwd()
            self.config_file = os.path.join(current_dir, "mcp_config.json")
        
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                print(f"📋 Loaded config from: {self.config_file}")
            except Exception as e:
                print(f"⚠️  Could not load config file {self.config_file}: {e}")
                self.config = self._get_default_config()
        else:
            print(f"📝 No config file found at {self.config_file}")
            print(f"   Use 'create config file' to set up OAuth credentials.")
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration structure"""
        return {
            "_instructions": {
                "description": "MCP Toolkit Configuration",
                "how_to_use": [
                    "1. Add your OAuth credentials below",
                    "2. Change 'current_environment' to switch between dev/staging/prod",
                    "3. Update URLs to match your API endpoints",
                    "4. Save this file and restart the application"
                ],
                "example": {
                    "client_id": "your_actual_client_id_here",
                    "client_secret": "your_actual_secret_here"
                }
            },
            "current_environment": "production",
            "environments": {
                "development": {
                    "name": "Development Environment",
                    "description": "For local development and testing",
                    "oauth": {
                        "client_id": "PUT_YOUR_DEV_CLIENT_ID_HERE",
                        "client_secret": "PUT_YOUR_DEV_CLIENT_SECRET_HERE",
                        "token_url": "https://dev-api.example.com/oauth/token",
                        "auth_url": "https://dev-api.example.com/oauth/authorize",
                        "redirect_uri": "http://localhost:8080/callback",
                        "default_scope": "read write"
                    }
                },
                "staging": {
                    "name": "Staging Environment",
                    "description": "For testing before production",
                    "oauth": {
                        "client_id": "PUT_YOUR_STAGING_CLIENT_ID_HERE",
                        "client_secret": "PUT_YOUR_STAGING_CLIENT_SECRET_HERE",
                        "token_url": "https://staging-api.example.com/oauth/token",
                        "auth_url": "https://staging-api.example.com/oauth/authorize",
                        "redirect_uri": "http://localhost:8080/callback",
                        "default_scope": "read write"
                    }
                },
                "production": {
                    "name": "Production Environment",
                    "description": "Live production system",
                    "oauth": {
                        "client_id": "PUT_YOUR_PROD_CLIENT_ID_HERE",
                        "client_secret": "PUT_YOUR_PROD_CLIENT_SECRET_HERE",
                        "token_url": "https://api.example.com/oauth/token",
                        "auth_url": "https://api.example.com/oauth/authorize",
                        "redirect_uri": "http://localhost:8080/callback",
                        "default_scope": "read write"
                    }
                }
            }
        }
    
    def get_current_environment(self) -> str:
        """Get the currently selected environment"""
        return self.config.get("current_environment", "production")
    
    def set_current_environment(self, environment: str):
        """Set the current environment"""
        if environment not in self.config.get("environments", {}):
            raise ValueError(f"Environment '{environment}' not found in config")
        
        self.config["current_environment"] = environment
        self.save_config()
        print(f"🔄 Switched to {environment} environment")
    
    def get_oauth_config(self, environment: str = None) -> Dict[str, Any]:
        """Get OAuth configuration for specified environment"""
        env = environment or self.get_current_environment()
        
        env_config = self.config.get("environments", {}).get(env, {})
        oauth_config = env_config.get("oauth", {})
        
        # Check for placeholder values
        placeholder_indicators = [
            "PUT_YOUR_", "your_actual_", "REPLACE_", "ADD_YOUR_", 
            "example.com", "localhost", ""
        ]
        
        issues = []
        for field in ["client_id", "client_secret", "token_url"]:
            value = oauth_config.get(field, "")
            if not value or any(indicator in str(value) for indicator in placeholder_indicators):
                issues.append(field)
        
        if issues:
            raise ValueError(
                f"Please update the config file: {self.config_file}\n"
                f"Environment '{env}' needs these fields configured: {issues}\n"
                f"Replace the placeholder values with your actual OAuth credentials."
            )
        
        return oauth_config
    
    def get_available_environments(self) -> Dict[str, str]:
        """Get list of available environments with their display names"""
        environments = {}
        for env_key, env_config in self.config.get("environments", {}).items():
            environments[env_key] = env_config.get("name", env_key.title())
        return environments
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"💾 Config saved to: {self.config_file}")
        except Exception as e:
            print(f"⚠️  Could not save config file: {e}")
    
    def create_config_file(self):
        """Create a configuration file with helpful instructions"""
        config = self._get_default_config()
        
        # Create the config file
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Config file created: {self.config_file}")
        print(f"")
        print(f"📝 NEXT STEPS:")
        print(f"   1. Open the file: {self.config_file}")
        print(f"   2. Replace placeholder values with your actual OAuth credentials")
        print(f"   3. Update URLs to match your API endpoints")
        print(f"   4. Save the file")
        print(f"   5. Use 'show config status' to verify everything is set up")
        print(f"")
        print(f"💡 TIP: Look for values like 'PUT_YOUR_CLIENT_ID_HERE' and replace them")
        
        return config
    
    def show_config_status(self) -> Dict[str, Any]:
        """Show current configuration status"""
        current_env = self.get_current_environment()
        environments = self.get_available_environments()
        
        status = {
            "config_file": os.path.abspath(self.config_file),
            "config_exists": os.path.exists(self.config_file),
            "current_environment": current_env,
            "available_environments": environments,
            "environments_status": {}
        }
        
        for env_key in environments.keys():
            try:
                oauth_config = self.get_oauth_config(env_key)
                status["environments_status"][env_key] = {
                    "configured": True,
                    "ready": True,
                    "client_id": oauth_config.get("client_id", "")[:10] + "..." if oauth_config.get("client_id") else "Missing",
                    "token_url": oauth_config.get("token_url", "Missing")
                }
            except ValueError as e:
                status["environments_status"][env_key] = {
                    "configured": False,
                    "ready": False,
                    "error": str(e),
                    "needs_setup": True
                }
        
        return status