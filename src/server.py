#!/usr/bin/env python3
"""
MCP Server with HTTP transport support for containerized deployment.

This server provides simple tools and prompts that can be used by MCP clients
via HTTP transport. It includes basic tools like weather, sum, and a context-aware
tool that demonstrates MCP capabilities.
"""

import argparse
import logging
import os
from typing import Any, Dict, List

from mcp.server.fastmcp import Context, FastMCP
from mcp.types import CallToolResult, TextContent
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create MCP server with stateless HTTP for container deployment
mcp = FastMCP(
    name="ContainerMCPServer",
    stateless_http=True,  # Required for container deployment
    json_response=False   # Use SSE streams by default
)


class WeatherData(BaseModel):
    """Weather data model."""
    temperature: float
    condition: str
    humidity: int
    city: str


@mcp.tool()
def get_weather(city: str = "San Francisco") -> WeatherData:
    """
    Get mock weather information for a city.
    
    Args:
        city: The city name to get weather for
    
    Returns:
        WeatherData: Weather information including temperature, condition, humidity
    """
    # Mock weather data - in production, this would call a real weather API
    mock_weather = {
        "San Francisco": {"temp": 18.5, "condition": "foggy", "humidity": 85},
        "New York": {"temp": 22.0, "condition": "sunny", "humidity": 60},
        "London": {"temp": 12.0, "condition": "rainy", "humidity": 90},
        "Tokyo": {"temp": 25.0, "condition": "partly cloudy", "humidity": 70},
    }
    
    weather_info = mock_weather.get(city, {"temp": 20.0, "condition": "unknown", "humidity": 50})
    
    return WeatherData(
        temperature=weather_info["temp"],
        condition=weather_info["condition"],
        humidity=weather_info["humidity"],
        city=city
    )


@mcp.tool()
def sum_numbers(a: float, b: float) -> float:
    """
    Add two numbers together.
    
    Args:
        a: First number
        b: Second number
    
    Returns:
        float: The sum of the two numbers
    """
    return a + b


@mcp.tool()
async def context_info(message: str, ctx: Context) -> CallToolResult:
    """
    Demonstrate context capabilities with logging, progress reporting, and metadata access.
    
    Args:
        message: A message to process
        ctx: MCP Context object providing access to logging, progress, etc.
    
    Returns:
        CallToolResult: Information about the context and processing
    """
    # Log some information
    await ctx.info(f"Processing context info request: {message}")
    await ctx.debug("This is a debug message from the context tool")
    
    # Report progress
    await ctx.report_progress(
        progress=0.5,
        total=1.0,
        message="Processing message..."
    )
    
    # Access request metadata (if available)
    request_id = getattr(ctx.request_context, 'request_id', 'unknown')
    
    # Complete progress
    await ctx.report_progress(
        progress=1.0,
        total=1.0,
        message="Complete"
    )
    
    response_text = f"""Context Information:
- Message: {message}
- Request ID: {request_id}
- Context logging available: Yes
- Progress reporting available: Yes
- User interaction capabilities: Available through context
"""
    
    return CallToolResult(
        content=[TextContent(type="text", text=response_text)],
        isError=False
    )


# Add prompts for reusable templates
@mcp.prompt("weather_report")
def weather_report_prompt(city: str = "San Francisco", format: str = "brief") -> str:
    """
    Generate a weather report prompt for the specified city.
    
    Args:
        city: City name for the weather report
        format: Report format (brief, detailed, or forecast)
    """
    if format == "detailed":
        return f"""Please provide a detailed weather report for {city}. Include:
- Current temperature and conditions
- Humidity levels
- Wind speed and direction
- UV index
- Air quality
- Extended forecast for the next 3 days"""
    elif format == "forecast":
        return f"""Please provide a 5-day weather forecast for {city} including:
- Daily high and low temperatures
- Precipitation probability
- Weather conditions
- Any weather alerts or advisories"""
    else:  # brief
        return f"What's the current weather in {city}? Please provide temperature, conditions, and humidity."


@mcp.prompt("calculation_helper")
def calculation_helper_prompt(operation: str = "addition", context: str = "") -> str:
    """
    Generate a prompt for mathematical calculations.
    
    Args:
        operation: Type of mathematical operation
        context: Additional context for the calculation
    """
    base_prompt = f"Please help me with a {operation} calculation."
    if context:
        base_prompt += f" Context: {context}"
    
    if operation == "addition":
        base_prompt += " Please add the numbers and show your work."
    elif operation == "subtraction":
        base_prompt += " Please subtract the numbers and explain the process."
    elif operation == "multiplication":
        base_prompt += " Please multiply the numbers and show intermediate steps."
    elif operation == "division":
        base_prompt += " Please divide the numbers and handle any remainders appropriately."
    else:
        base_prompt += " Please perform the calculation and explain your approach."
    
    return base_prompt


# Add custom routes using FastMCP's custom_route decorator
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """Health check endpoint for container orchestration."""
    from starlette.responses import JSONResponse
    
    # Get tool and prompt count using FastMCP's built-in methods
    try:
        tools = await mcp.list_tools()
        tools_count = len(tools)
    except Exception:
        tools_count = 0
        
    try:
        prompts = getattr(mcp, '_prompts', {})
        prompts_count = len(prompts)
    except Exception:
        prompts_count = 0
    
    return JSONResponse({
        "status": "healthy",
        "server": "ContainerMCPServer",
        "transport": "streamable-http",
        "tools_count": tools_count,
        "prompts_count": prompts_count
    })


@mcp.custom_route("/", methods=["GET"])
async def root_info(request):
    """Root endpoint with server information."""
    from starlette.responses import JSONResponse
    
    # Get tool and prompt names using FastMCP's built-in methods
    try:
        tool_list = await mcp.list_tools()
        tools = [tool.name for tool in tool_list]
    except Exception:
        tools = []
        
    try:
        prompts = list(getattr(mcp, '_prompts', {}).keys())
    except Exception:
        prompts = []
    
    return JSONResponse({
        "name": "Container MCP Server",
        "version": "1.0.0",
        "transport": "streamable-http",
        "mcp_endpoint": "/mcp",
        "health_endpoint": "/health",
        "tools": tools,
        "prompts": prompts
    })


def create_app():
    """Create and return the FastMCP streamable HTTP app."""
    return mcp.streamable_http_app()


def run_server(port: int = 8000, log_level: str = "INFO", json_response: bool = False):
    """
    Run the MCP server using FastMCP's built-in server.
    
    Args:
        port: Port to run the server on
        log_level: Logging level
        json_response: Whether to use JSON responses instead of SSE
    """
    # Update server configuration
    if json_response:
        mcp.json_response = True
        logger.info("Using JSON response mode")
    
    logger.info(f"Starting MCP server on port {port}")
    logger.info(f"Server name: {mcp.name}")
    
    # Use FastMCP's built-in server runner with streamable-http transport
    # Configure host and port through environment variables
    import os
    os.environ['HOST'] = '0.0.0.0'
    os.environ['PORT'] = str(port)
    
    # This properly initializes the task group and handles all the ASGI setup
    mcp.run(transport='streamable-http')


def main():
    """Main entry point for direct execution."""
    parser = argparse.ArgumentParser(description="MCP Server for Container Deployment")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    parser.add_argument("--json-response", action="store_true", help="Use JSON responses instead of SSE")
    
    args = parser.parse_args()
    
    # Set logging level from args
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))
    
    try:
        run_server(args.port, args.log_level, args.json_response)
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()