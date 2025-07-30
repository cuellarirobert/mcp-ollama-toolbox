#!/usr/bin/env python3
"""
Basic usage example for MCP Ollama Toolkit
This demonstrates how to set up and use the chat interface with tools
"""
import os
import sys
import signal

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mcp_toolkit.core.chat_interface import MCPOllamaChat
from mcp_toolkit.tools.data_tools import DataToolsCollection
from mcp_toolkit.tools.content_tools import ContentToolsCollection

# Sample data managers (you'd replace these with your real implementations)
class SampleDataManager:
    def __init__(self):
        self.data = [
            {"id": 1, "name": "Sample Item 1", "type": "example"},
            {"id": 2, "name": "Sample Item 2", "type": "demo"},
            {"id": 3, "name": "Another Item", "type": "example"}
        ]
    
    def get_all_items(self):
        return self.data
    
    def get_item_by_id(self, item_id):
        return next((item for item in self.data if item["id"] == int(item_id)), None)
    
    def search_items(self, query):
        return [item for item in self.data if query.lower() in item["name"].lower()]

class SampleContentManager:
    def __init__(self):
        self.content = [
            {"id": "c1", "title": "Content 1", "status": "published"},
            {"id": "c2", "title": "Content 2", "status": "draft"}
        ]
    
    def get_content_items(self):
        return self.content

def signal_handler(sig, frame):
    print('\n\n👋 Thanks for using MCP Ollama Toolkit! Goodbye!')
    sys.exit(0)

def print_banner():
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                🚀  MCP Ollama Toolkit Demo                   ║
║                   Professional Function Calling             ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    os.system('clear' if os.name == 'posix' else 'cls')
    print_banner()
    
    print("⚡ Initializing MCP Chat System...")
    
    try:
        # Initialize the chat interface
        chat = MCPOllamaChat()

        # Create auth manager (example configuration)
        auth_manager = OAuth2Manager(
            client_id="your_client_id",
            client_secret="your_client_secret", 
            token_url="https://api.example.com/oauth/token",
            auth_url="https://api.example.com/oauth/authorize",
            redirect_uri="http://localhost:8080/callback"
        )
        
        # Create and register auth tools
        auth_tools = AuthToolsCollection(auth_manager)
        chat.register_tool_collection("auth_tools", auth_tools)
        
        # Create your data/content managers
        data_manager = SampleDataManager()
        content_manager = SampleContentManager()
        
        # Create tool collections
        data_tools = DataToolsCollection(data_manager)
        content_tools = ContentToolsCollection(content_manager)
        
        # Register tool collections with chat interface
        chat.register_tool_collection("data_tools", data_tools)
        chat.register_tool_collection("content_tools", content_tools)
        
        print("✅ Chat system ready!")
        print("\n🚀 Quick Start:")
        print("  • Type 'tools' to see available functions")
        print("  • Ask: 'What data do you have?'")
        print("  • Try: 'Search for Sample'")
        print("  • Type 'help' for more options")
        print("  • 'quit' to exit")
        print()
        
        # Main chat loop
        while True:
            try:
                user_input = input("💬 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    print("\n👋 Thanks for using MCP Ollama Toolkit! Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                print(f"\n🤖 Assistant:")
                response = chat.chat(user_input)
                
                if response.strip():
                    print(response)
                
            except KeyboardInterrupt:
                signal_handler(None, None)
            except EOFError:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("Please try again.\n")
                
    except Exception as e:
        print(f"❌ Failed to initialize: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()