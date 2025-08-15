# Container MCP Server

A Model Context Protocol (MCP) server designed for containerized deployment with HTTP transport. This server provides simple, dependency-free tools and prompts that can be used by MCP clients via streamable HTTP transport.

## Features

- **HTTP Transport**: Uses streamable HTTP transport for remote MCP server deployment
- **Container Ready**: Optimized for Docker/Kubernetes deployment with health checks
- **Simple Tools**: Weather data, mathematical calculations, and context-aware operations
- **Prompts**: Reusable templates for weather reports and calculations
- **No External Dependencies**: Mock data for easy testing and demonstration

## Tools

### 1. get_weather
Get mock weather information for a city.

**Parameters:**
- `city` (string, optional): City name (default: "San Francisco")

**Returns:** Weather data including temperature, condition, and humidity

### 2. sum_numbers  
Add two numbers together.

**Parameters:**
- `a` (float): First number
- `b` (float): Second number

**Returns:** The sum of the two numbers

### 3. context_info
Demonstrate MCP context capabilities including logging, progress reporting, and metadata access.

**Parameters:**
- `message` (string): A message to process
- `ctx` (Context): MCP Context object (automatically injected)

**Returns:** Information about the context and processing

## Prompts

### 1. weather_report
Generate weather report prompts for specified cities.

**Arguments:**
- `city` (string): City name for the weather report
- `format` (string): Report format ("brief", "detailed", or "forecast")

### 2. calculation_helper
Generate prompts for mathematical calculations.

**Arguments:**
- `operation` (string): Type of mathematical operation
- `context` (string): Additional context for the calculation

## Installation & Development

### Using Virtual Environment (Recommended)

1. **Create and activate virtual environment:**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Unix/macOS:
   source venv/bin/activate
   # On Windows:
   # venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run in development mode:**
   ```bash
   python -m src.server --port 8000 --log-level DEBUG
   ```

4. **Run tests:**
   ```bash
   pytest
   ```

5. **Deactivate virtual environment when done:**
   ```bash
   deactivate
   ```

### Without Virtual Environment (Not Recommended)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run in development mode:**
   ```bash
   python -m src.server --port 8000 --log-level DEBUG
   ```

3. **Run tests:**
   ```bash
   pytest
   ```

### Direct Execution

The server supports direct execution for development and testing:

```bash
# Basic execution
python src/server.py

# With custom options
python src/server.py --port 3000 --log-level DEBUG --json-response
```

**Command-line options:**
- `--port`: Port to run the server on (default: 8000)
- `--log-level`: Logging level (default: INFO)
- `--json-response`: Use JSON responses instead of SSE streams

## Container Deployment

### Docker

1. **Build the container:**
   ```bash
   docker build -t mcp-server .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8000:8000 mcp-server
   ```

3. **With custom environment:**
   ```bash
   docker run -p 8000:8000 -e LOG_LEVEL=DEBUG mcp-server
   ```

### Docker Compose

1. **Basic deployment:**
   ```bash
   docker-compose up
   ```

2. **With production nginx proxy:**
   ```bash
   docker-compose --profile production up
   ```

### Kubernetes

Example deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-server
  template:
    metadata:
      labels:
        app: mcp-server
    spec:
      containers:
      - name: mcp-server
        image: mcp-server:latest
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: mcp-service
spec:
  selector:
    app: mcp-server
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## API Endpoints

### Health Check
- **URL:** `GET /health`
- **Response:** Server health status and metadata
- **Use:** Container orchestration health checks

### Server Info
- **URL:** `GET /`
- **Response:** Server information, available tools, and prompts
- **Use:** Discovery and documentation

### MCP Endpoint
- **URL:** `POST /mcp`
- **Protocol:** MCP over HTTP (JSON-RPC 2.0)
- **Transport:** Streamable HTTP with SSE support
- **Use:** MCP client connections

## Connection Details

### For MCP Clients

**Server URL:** `http://localhost:8000/mcp`

**Transport:** Streamable HTTP

**Authentication:** None (can be extended)

### Example Client Connection (Python)

```python
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    async with streamablehttp_client("http://localhost:8000/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools.tools]}")
            
            # Call a tool
            result = await session.call_tool("get_weather", {"city": "New York"})
            print(f"Weather result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Testing

### Unit Tests
```bash
pytest tests/
```

### Integration Tests
```bash
# Start the server
python -m src.server --port 8001 &
SERVER_PID=$!

# Test health endpoint
curl http://localhost:8001/health

# Test server info
curl http://localhost:8001/

# Test MCP connection with a client
# (see example above)

# Cleanup
kill $SERVER_PID
```

### Container Tests
```bash
# Test container build
docker build -t mcp-server-test .

# Test container run
docker run -d -p 8002:8000 --name mcp-test mcp-server-test

# Test health check
curl http://localhost:8002/health

# Cleanup
docker stop mcp-test && docker rm mcp-test
```

## Monitoring

### Health Checks
The server provides a `/health` endpoint that returns:
- Server status
- Tool and prompt counts
- Transport information

### Logging
Structured logging with configurable levels:
```bash
# Set log level via environment
export LOG_LEVEL=DEBUG
python -m src.server

# Or via command line
python -m src.server --log-level DEBUG
```

### Metrics
For production deployments, consider adding:
- Prometheus metrics endpoint
- OpenTelemetry tracing
- Request/response logging

## Architecture

```
┌─────────────────┐    HTTP/SSE     ┌─────────────────┐
│   MCP Client    │ ◄──────────────► │   MCP Server    │
│                 │                 │                 │
│ - Claude Code   │                 │ - Tools         │
│ - Custom Client │                 │ - Prompts       │
│ - Web App       │                 │ - Health Check  │
└─────────────────┘                 └─────────────────┘
                                           │
                                           ▼
                                    ┌─────────────────┐
                                    │   Container     │
                                    │                 │
                                    │ - Docker        │
                                    │ - Kubernetes    │
                                    │ - Cloud Run     │
                                    └─────────────────┘
```

## Security Considerations

- The server runs as a non-root user in containers
- No secrets or API keys are required for basic functionality
- Consider adding authentication for production deployments
- Network policies should restrict access to necessary ports only

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run the test suite
5. Submit a pull request

## License

This project is available under the MIT License.