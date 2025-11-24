# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python learning project for building AI agent systems with OpenAI API integration. The project follows a 4-day curriculum structure:

- **Day 1**: Design patterns (chain pattern implementation)
- **Day 2**: Agent state management framework
- **Day 3**: ReAct loop and tools implementation
- **Day 4-5**: Personal assistant CLI application

## Development Commands

### Environment Setup
```bash
# Install dependencies with uv
uv sync

# Create .env file with OPENAI_API_KEY
echo "OPENAI_API_KEY=your_key_here" > .env
```

### Running the Application
```bash
# Run main entry point
python main.py

# Run with uv
uv run main.py
```

## Architecture

### Planned Structure
```
src/
├── day1_patterns/     # Chain pattern design implementation
├── day2_framework/    # Agent state management
├── day3_core/         # ReAct engine and tools
└── day4_cli/         # Final CLI assistant
```

### Dependencies
- **openai**: OpenAI API client for LLM interactions
- **pydantic**: Data validation and configuration
- **python-dotenv**: Environment variable management (.env file)
- **rich**: Rich text and formatting for CLI output
- **typer**: CLI framework for building command-line interfaces

## Key Concepts

This project focuses on teaching fundamental AI agent patterns:
1. **Chain Pattern**: Sequential processing of agent operations
2. **State Management**: Maintaining conversation and task state
3. **ReAct Loop**: Reasoning and Acting pattern for problem-solving
4. **Tool Integration**: Extending agent capabilities with external tools

## Environment Configuration

The project requires a `.env` file in the project root with:
```
OPENAI_API_KEY=your_openai_api_key_here
```

The project is configured to work with Python 3.12+ and uses `uv` for dependency management.