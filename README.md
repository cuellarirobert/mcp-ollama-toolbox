# MCP Ollama Toolbox 🛠️

A professional toolkit for integrating Python functions with Ollama using Model Context Protocol (MCP) standards. Features OAuth2 authentication, function calling transparency, and a beautiful terminal interface.

![Demo](https://img.shields.io/badge/Status-Beta-yellow)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Ollama](https://img.shields.io/badge/Ollama-Compatible-green)
![License](https://img.shields.io/badge/License-MIT-blue)

## ✨ Features

- 🔧 **MCP-Compliant Tools**: Properly structured tool collections following MCP standards
- 🎨 **Professional UI**: Colored terminal output with progress indicators and animations
- 📊 **Function Call Transparency**: See exactly what tools are being called with MCP payload structure
- 🔐 **OAuth2 Support**: Built-in OAuth2 authentication with multi-environment support
- 🔌 **Easy Integration**: Simple way to connect your existing Python modules
- 🚀 **Extensible**: Add new tool collections with minimal code
- 📋 **Configuration Management**: Simple JSON config file for OAuth credentials

## 🎬 Demo

```bash
You: "Get me an OAuth token for staging"

🔧 Function Calling Required
Ollama determined 1 function call needed:

┌─ Function Call #1/1
│
├─ Function: get_oauth_token
├─ Description: Get OAuth2 bearer token using client credentials flow
├─ Parameters:
│  • environment: staging
│
├─ MCP Payload Structure:
│  {
│    "jsonrpc": "2.0",
│    "method": "tools/call",
│    "params": {
│      "name": "get_oauth_token",
│      "arguments": {"environment": "staging"}
│    }
│  }
│
└─ Executing... ✅ Success
   └─ Retrieved bearer token (took 0.45s)

🧠 Processing Results & Generating Response...
✨ Response Ready!

I've successfully retrieved an OAuth2 bearer token for your staging environment. The token is valid for 3600 seconds and includes 'read write' scope permissions.
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Ollama installed and running
- Ollama model pulled (e.g., `ollama pull llama3.1`)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/cuellarirobert/mcp-ollama-toolbox.git
   cd mcp-ollama-toolbox
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up configuration:
   ```bash
   python examples/basic_usage.py
   # Ask: "create config file"
   ```

4. Edit `mcp_config.json` with your OAuth credentials:
   ```json
   {
     "current_environment": "production",
     "environments": {
       "production": {
         "oauth": {
           "client_id": "your_actual_client_id",
           "client_secret": "your_actual_secret",
           "token_url": "https://your-api.com/oauth/token"
         }
       }
     }
   }
   ```

5. Run the demo:
   ```bash
   python examples/basic_usage.py
   ```

### Try These Commands

- "What tools do you have available?"
- "Get an OAuth token"
- "Switch to staging environment"
- "Show me all the data"
- "Search for Sample"

## 🏗️ Architecture

```
mcp-ollama-toolbox/
├── src/mcp_toolkit/
│   ├── core/                    # Core chat interface and configuration
│   │   ├── chat_interface.py    # Main MCP chat interface
│   │   └── config_manager.py    # Configuration management
│   ├── tools/                   # MCP-compliant tool collections
│   │   ├── auth_tools.py        # OAuth2 authentication
│   │   ├── data_tools.py        # Data access and management
│   │   ├── content_tools.py     # Content operations
│   │   └── oauth_manager.py     # OAuth2 implementation
│   ├── resources/               # Schemas and templates
│   └── prompts/                 # System prompts and examples
├── examples/                    # Usage examples
└── tests/                       # Test suite
```

## 🔧 Usage

### Basic Usage

```python
from mcp_toolkit.core.chat_interface import MCPOllamaChat
from mcp_toolkit.tools.data_tools import DataToolsCollection

# Create chat interface
chat = MCPOllamaChat()

# Create your data manager (implement your logic here)
data_manager = YourDataManager()

# Create and register tools
tools = DataToolsCollection(data_manager) 
chat.register_tool_collection("data", tools)

# Start chatting!
response = chat.chat("What data do you have?")
```

### Adding Custom Tools

```python
class MyCustomToolsCollection:
    def __init__(self, my_manager):
        self.my_manager = my_manager
        
    def get_tool_manifest(self):
        return {
            "tools": [
                {
                    "name": "my_custom_function",
                    "description": "Does something amazing",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "param": {"type": "string", "description": "A parameter"}
                        },
                        "required": ["param"]
                    }
                }
            ]
        }
    
    def execute_tool(self, tool_name, arguments):
        if tool_name == "my_custom_function":
            result = self.my_manager.do_something(arguments["param"])
            return {
                "content": [{"type": "text", "text": json.dumps(result)}]
            }

# Register with chat interface
chat.register_tool_collection("custom", MyCustomToolsCollection(my_manager))
```

## 🔐 OAuth2 Configuration

The toolkit supports multiple environments with separate OAuth credentials:

### Environment Structure

```json
{
  "current_environment": "production",
  "environments": {
    "development": {
      "name": "Development Environment",
      "oauth": {
        "client_id": "dev_client_id",
        "client_secret": "dev_secret",
        "token_url": "https://dev-api.example.com/oauth/token",
        "default_scope": "read write admin"
      }
    },
    "staging": {
      "name": "Staging Environment", 
      "oauth": {
        "client_id": "staging_client_id",
        "client_secret": "staging_secret",
        "token_url": "https://staging-api.example.com/oauth/token",
        "default_scope": "read write"
      }
    },
    "production": {
      "name": "Production Environment",
      "oauth": {
        "client_id": "prod_client_id",
        "client_secret": "prod_secret",
        "token_url": "https://api.example.com/oauth/token",
        "default_scope": "read write"
      }
    }
  }
}
```

### OAuth2 Commands

- "Get OAuth token" - Get token from current environment
- "Get token for staging" - Get token from specific environment
- "Switch to development" - Change current environment
- "Show config status" - Check configuration status  
- "Refresh token using xyz..." - Refresh an existing token

## 🛠️ Available Tools

### Authentication Tools

- `get_oauth_token`: Get OAuth2 bearer tokens with client credentials flow
- `refresh_oauth_token`: Refresh expired tokens
- `switch_environment`: Change between dev/staging/production
- `show_config_status`: Display current configuration

### Data Tools

- `get_all_items`: Retrieve all data items
- `get_item_by_id`: Get specific item by identifier
- `search_items`: Search through data with queries

### Content Tools

- `get_content_items`: Retrieve content library
- `update_content_item`: Modify content properties
- `create_content_item`: Add new content

## 🧪 Testing

```bash
# Run tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_tools.py -v

# Test with coverage
python -m pytest --cov=src/mcp_toolkit tests/
```

## 📚 Examples

Check out the `examples/` directory for:

- `basic_usage.py`: Getting started with the toolkit
- `advanced_workflows.py`: Complex multi-step operations
- `custom_integration.py`: Adding your own tools

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/mcp-ollama-toolbox.git
cd mcp-ollama-toolbox

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install in development mode
pip install -e .
pip install -r requirements-dev.txt

# Run tests
python -m pytest
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai) for the amazing local LLM platform
- [Model Context Protocol](https://modelcontextprotocol.io) for the standards
- The open-source community for inspiration and tools

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/cuellarirobert/mcp-ollama-toolbox/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/cuellarirobert/mcp-ollama-toolbox/discussions)
- 📖 **Documentation**: Check the `docs/` directory
- 💬 **Questions**: Open a discussion or issue