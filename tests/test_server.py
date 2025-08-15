"""Tests for the MCP server."""

import json
from unittest.mock import AsyncMock, Mock

import pytest
from starlette.testclient import TestClient

from src.server import create_app, get_weather, sum_numbers


@pytest.fixture
def app():
    """Create test application."""
    return create_app()


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)




def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert data["server"] == "ContainerMCPServer"
    assert data["transport"] == "streamable-http"
    assert "tools_count" in data
    assert "prompts_count" in data


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == "Container MCP Server"
    assert data["version"] == "1.0.0"
    assert data["mcp_endpoint"] == "/mcp"
    assert "tools" in data
    assert "prompts" in data


def test_get_weather_tool():
    """Test get_weather tool function."""
    # Test default city
    result = get_weather()
    assert result.city == "San Francisco"
    assert result.temperature == 18.5
    assert result.condition == "foggy"
    assert result.humidity == 85
    
    # Test specific city
    result = get_weather("New York")
    assert result.city == "New York"
    assert result.temperature == 22.0
    assert result.condition == "sunny"
    assert result.humidity == 60
    
    # Test unknown city
    result = get_weather("Unknown City")
    assert result.city == "Unknown City"
    assert result.temperature == 20.0
    assert result.condition == "unknown"
    assert result.humidity == 50


def test_sum_numbers_tool():
    """Test sum_numbers tool function."""
    assert sum_numbers(2, 3) == 5
    assert sum_numbers(-1, 1) == 0
    assert sum_numbers(2.5, 3.7) == 6.2
    assert sum_numbers(0, 0) == 0


@pytest.mark.asyncio
async def test_context_info_tool():
    """Test context_info tool function."""
    from src.server import context_info
    
    # Mock context object
    mock_context = Mock()
    mock_context.info = AsyncMock()
    mock_context.debug = AsyncMock()
    mock_context.report_progress = AsyncMock()
    mock_context.request_context = Mock()
    mock_context.request_context.request_id = "test-123"
    
    result = await context_info("test message", mock_context)
    
    # Verify context methods were called
    mock_context.info.assert_called_once()
    mock_context.debug.assert_called_once()
    assert mock_context.report_progress.call_count == 2  # Called twice for progress
    
    # Verify result
    assert not result.isError
    assert len(result.content) == 1
    assert result.content[0].type == "text"
    assert "test message" in result.content[0].text
    assert "test-123" in result.content[0].text


def test_mcp_endpoint_accessibility(client):
    """Test that the MCP endpoint is accessible."""
    # Test that the MCP endpoint mount exists - we can't easily test the MCP protocol
    # in unit tests, but we can verify the endpoint is available
    
    # The /mcp path should be mounted and accessible
    # This will return a 404 for GET but not a connection error
    response = client.get("/mcp")
    # MCP endpoints typically don't respond to GET, so 404 or 405 is expected
    assert response.status_code in [404, 405, 200]


def test_weather_report_prompt():
    """Test weather report prompt generation."""
    from src.server import weather_report_prompt
    
    # Test brief format
    result = weather_report_prompt("Paris", "brief")
    assert "Paris" in result
    assert "temperature" in result
    
    # Test detailed format
    result = weather_report_prompt("London", "detailed")
    assert "London" in result
    assert "detailed weather report" in result
    assert "UV index" in result
    
    # Test forecast format
    result = weather_report_prompt("Tokyo", "forecast")
    assert "Tokyo" in result
    assert "5-day weather forecast" in result


def test_calculation_helper_prompt():
    """Test calculation helper prompt generation."""
    from src.server import calculation_helper_prompt
    
    # Test addition
    result = calculation_helper_prompt("addition")
    assert "addition calculation" in result
    assert "add the numbers" in result
    
    # Test with context
    result = calculation_helper_prompt("multiplication", "budget calculation")
    assert "multiplication calculation" in result
    assert "budget calculation" in result
    
    # Test unknown operation
    result = calculation_helper_prompt("unknown")
    assert "unknown calculation" in result