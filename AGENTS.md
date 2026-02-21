# fast-aiogentic - Agent Guidelines

## Project Overview
Python 3.13 project: fast-aiogentic

## Core Values - The Zen of Python
```python
import this
```
- Beautiful is better than ugly
- Explicit is better than implicit
- Simple is better than complex
- Complex is better than complicated
- Flat is better than nested
- Sparse is better than dense
- Readability counts
- Special cases aren't special enough to break the rules
- Although practicality beats purity
- Errors should never pass silently
- Unless explicitly silenced
- In the face of ambiguity, refuse the temptation to guess
- There should be one-- and preferably only one --obvious way to do it
- Although that way may not be obvious at first unless you're Dutch
- Now is better than never
- Although never is often better than *right* now
- If the implementation is hard to explain, it's a bad idea
- If the implementation is easy to explain, it may be a good idea

## Technical Stack
- **Python**: 3.13
- **Package Manager**: uv (for venv and dependencies)
- **Build System**: uv-build
- **Domain Modeling**: Pydantic 2.0+
- **Linting**: ruff (strict import sorting), ty (fast type checking)
- **Testing**: pytest, pytest-asyncio, pytest-cov
- **API Framework**: FastAPI


## Architectural Principles

### Domain-Driven Design (DDD)
- Ubiquitous language throughout the codebase
- Clear bounded contexts and aggregates
- Rich domain models using Pydantic
- Domain logic separated from infrastructure

### Test-Driven Development (TDD)
- Write tests first, then implementation
- Red → Green → Refactor cycle
- Minimum 80% code coverage target
- Test behavior, not implementation

### SOLID Principles
- **S**ingle Responsibility: Each class/function has one reason to change
- **O**pen/Closed: Open for extension, closed for modification
- **L**iskov Substitution: Derived classes substitutable for base classes
- **I**nterface Segregation: Depend only on interfaces you use
- **D**ependency Inversion: Depend on abstractions, not concretions

### GRASP Principles
- **Creator**: Assign class B responsibility to create A if B contains/aggregates A
- **Information Expert**: Assign responsibility to class with necessary information
- **Low Coupling**: Minimize dependencies between classes
- **High Cohesion**: Keep related responsibilities together
- **Controller**: Delegate system events to appropriate handlers
- **Polymorphism**: Use polymorphism for type-based variations
- **Pure Fabrication**: Create artificial classes for low coupling/high cohesion
- **Indirection**: Introduce intermediate objects to reduce coupling
- **Protected Variations**: Protect against variations with stable interfaces

### Clean Code Guidelines
- **Functions**: Short (<20 lines), single purpose, meaningful names
- **Variables**: Descriptive names, no single letters (except i, j in loops)
- **Comments**: Why, not what; code should be self-documenting
- **Error Handling**: Explicit, never silent failures
- **Formatting**: Consistent, follow PEP 8 via ruff

## Pydantic Best Practices

### Model Design
```python
from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict

class DomainModel(BaseModel):
    """Always use docstrings for models."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        arbitrary_types_allowed=False,
        extra="forbid",  # Strict validation
    )

    # Use Annotated with Field for rich metadata
    name: Annotated[str, Field(min_length=1, max_length=100)]
    age: Annotated[int, Field(ge=0, le=150)]
```

### Type Safety Rules
- **NO dict[str, Any]**: Always create proper Pydantic models
- **NO raw dicts**: Use Pydantic models for all data structures
- **Reuse models**: Check existing models before creating new ones
- **Inherit wisely**: Extend existing models when appropriate
- **Validation**: Use validators for business rules
- **Immutability**: Consider frozen=True for value objects

### Model Organization
```
src/fast_aiogentic/
├── domain/
│   ├── models/      # Core domain models
│   ├── value_objects/ # Immutable value objects
│   └── aggregates/   # Aggregate roots
├── application/
│   └── dto/         # Data Transfer Objects
└── infrastructure/
    └── schemas/     # External API schemas
```

## Development Workflow

### Before Implementation
1. Run `pydantic-manager` to list existing models
2. Identify reusable models and types
3. Inherit from existing types where appropriate
4. Only create new types when absolutely necessary
5. Get user approval for any `Any` type usage

### During Implementation
1. Follow TDD: Write test → Implement → Refactor
2. Keep functions short and focused
3. Use meaningful variable and function names
4. Handle errors explicitly
5. Document complex logic with docstrings

### Code Quality Checks
```bash
# Format and lint
uv run ruff format src/ tests/
uv run ruff check src/ tests/

# Type checking
uv run ty check src/

# Run tests with coverage
uv run pytest --cov

# Full validation
uv run python scripts/validate.py
```

## Project Structure
```
fast-aiogentic/
├── src/
│   └── fast_aiogentic/
│       ├── __init__.py
│       ├── domain/          # Core business logic
│       ├── application/     # Use cases and services
│       ├── infrastructure/  # External interfaces
│       ├── api/             # API endpoints (if enabled)
│       └── cli/             # CLI commands (if enabled)
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── scripts/
│   └── validate.py
├── docker/
│   └── Dockerfile
├── .github/
│   └── workflows/
├── pyproject.toml
├── README.md
├── AGENTS.md
└── .gitignore
```

## Deliverables
- **Docker Compose Backend**: Port 8000


## Core Dependencies


## Validation Checklist
- [ ] All functions < 20 lines
- [ ] No dict[str, Any] in public signatures
- [ ] All models inherit from appropriate base classes
- [ ] 80%+ test coverage
- [ ] Zero ty errors (strict mode)
- [ ] Zero ruff violations
- [ ] All errors handled explicitly
- [ ] Documentation complete
- [ ] CI/CD pipeline passing

## Getting Started
```bash
# Initialize project
git init
uv venv
uv sync --all-extras

# Verify installation
uv run python -V

# List existing Pydantic models
uv run python -m pydantic_manager list

# Run tests
uv run pytest

# Start development
uv run python -m fast_aiogentic
```

## Contact
For questions about these guidelines, consult the team lead or refer to the official documentation.
