# fast-aiogentic

Python 3.13 project: fast-aiogentic

## Features

- Built with Python 3.13 and modern best practices
- Domain-driven design with Pydantic models
- Type-safe with strict ty checking
- Comprehensive test coverage
- RESTful API with FastAPI

- Docker containerization

## Quick Start

### Prerequisites

- Python 3.13+
- uv package manager
- Docker and Docker Compose

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd fast-aiogentic

# Set up virtual environment
uv venv
uv sync --all-extras

# Verify installation
uv run python -V
```

### Development

```bash
# Run tests
uv run pytest

# Run linting and type checking
uv run ruff check src/ tests/
uv run ty check src/

# Format code
uv run ruff format src/ tests/
```

### Running with Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access the API at http://localhost:8000
```



## Project Structure

```
fast-aiogentic/
├── src/
│   └── fast_aiogentic/      # Main package
│       ├── __init__.py          # Package version
│       └── api/                # API endpoints
├── tests/                        # Test suite
├── .github/workflows/            # CI/CD configuration
├── Dockerfile                   # Container build
├── docker-compose.yml           # Local development
├── Makefile                      # Common commands
├── pyproject.toml                # Project configuration
└── README.md
```

## Testing

Run tests with coverage:
```bash
make test
# or
uv run pytest --cov
```

## Contributing

1. Create a feature branch
2. Write tests first (TDD)
3. Implement the feature
4. Ensure all tests pass
5. Run linting and type checking
6. Submit a pull request

## License

MIT License - see LICENSE file for details.
