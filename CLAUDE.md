# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Preferences

### Development Workflow & Standards
- Follow TDD with unit and integration tests
- Use language-standard project layouts (Go standard layout, Python src/ layout)
- Include Makefiles/task runners for common operations (test, build, run, lint)

### Code Quality & Architecture
- Use descriptive variable/function names for self-documenting code
- Abstract external services behind interfaces for testability
- Implement repository pattern and dependency injection where appropriate

### Concurrency & Error Handling
- Use async/await patterns or consider concurrency/thread-safety for I/O operations
- Implement explicit error handling with context (Go wrapped errors, Python custom exception hierarchies with meaningful messages)

### Documentation & Logging
- Maintain running project summary with current architecture and simple changelog
- Include class/file/function level documentation with commenting on tricky logic
- Use structured, configurable logging (LOG_LEVEL support) with appropriate levels

### Language-Specific Patterns
**Python:**
- Follow dataclass patterns for type safety and validation
- Use FastAPI/Flask patterns
- Use type hints and Pydantic for data validation
- Use async/await for I/O operations
- Use pytest for testing with fixtures and parameterized tests
- Use pip-tools for dependency management

**Go:**
- Follow idiomatic Go patterns with proper error handling

**Both:**
- Include configuration validation
- Health check endpoints for services
- Graceful degradation

### Project Management
- Manage dependencies in virtual environments/workspaces with requirements files
- Separate configuration from code using environment variables
- Include README with usage examples and basic deployment guidance

## Project Overview
An MCP server that will work as a remote server with a small set of tools that have fewer, if any, dependencies.