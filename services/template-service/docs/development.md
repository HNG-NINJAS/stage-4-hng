# Development Guide

> **Setup and guidelines for developing Template Service**

## Development Setup

### 1. Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+ (optional)
- RabbitMQ 3.12+ (optional)
- Git

### 2. Clone Repository

```bash
git clone <repository>
cd services/template-service
```

### 3. Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 4. Install Dependencies

```bash
# Development dependencies
pip install -r requirements-dev.txt

# Production dependencies only
pip install -r requirements.txt
```

### 5. Environment Configuration

```bash
cp .env.example .env
```

Edit `.env`:
```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/template_db
REDIS_URL=redis://localhost:6379/0
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
LOG_LEVEL=DEBUG
```

### 6. Start Infrastructure

```bash
# From repo root
docker-compose up -d postgres_template redis rabbitmq
```

### 7. Database Setup

```bash
# Run migrations
alembic upgrade head

# Seed sample data
python scripts/seed_templates.py
```

### 8. Start Development Server

```bash
uvicorn app.main:app --reload --port 3004
```

Visit http://localhost:3004/docs for API documentation.

## Project Structure

```
template-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configuration
│   ├── database.py          # Database setup
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── api/
│   │   ├── __init__.py
│   │   ├── templates.py     # Template endpoints
│   │   ├── health.py        # Health checks
│   │   └── metrics.py       # Metrics tracking
│   ├── services/
│   │   ├── __init__.py
│   │   └── template_service.py  # Business logic
│   └── utils/
│       ├── __init__.py
│       ├── renderer.py      # Jinja2 rendering
│       ├── cache.py         # Redis caching
│       ├── rabbitmq.py      # Event publishing
│       └── response.py      # Response formatting
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   ├── test_api.py          # API tests
│   ├── test_template_service.py
│   └── test_renderer.py
├── alembic/
│   ├── versions/            # Migration files
│   └── env.py
├── scripts/
│   ├── seed_templates.py
│   ├── test_api.sh
│   └── run_dev.sh
├── docs/
│   ├── api/
│   ├── integration/
│   ├── examples/
│   ├── deployment.md
│   └── development.md
├── requirements.txt
├── requirements-dev.txt
├── alembic.ini
├── Dockerfile
└── README.md
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Follow coding standards (see below).

### 3. Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/test_api.py

# Specific test
pytest tests/test_api.py::test_create_template
```

### 4. Check Code Quality

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Lint
flake8 app/ tests/

# Type check
mypy app/
```

### 5. Create Migration (if needed)

```bash
# Auto-generate migration
alembic revision --autogenerate -m "Add new column"

# Review generated migration in alembic/versions/

# Apply migration
alembic upgrade head
```

### 6. Commit Changes

```bash
git add .
git commit -m "feat: add new feature"
```

Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `refactor:` - Code refactoring
- `test:` - Tests
- `chore:` - Maintenance

### 7. Push and Create PR

```bash
git push origin feature/your-feature-name
```

## Coding Standards

### Python Style

Follow [PEP 8](https://pep8.org/) and use:
- **Black** for formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

### Type Hints

Always use type hints:

```python
def render_template(template_id: str, data: dict) -> dict:
    """Render template with data"""
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def create_template(template_data: dict) -> Template:
    """Create a new template.
    
    Args:
        template_data: Dictionary containing template information
        
    Returns:
        Created template object
        
    Raises:
        ValueError: If template_id already exists
    """
    pass
```

### Error Handling

```python
try:
    result = operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    raise
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Template created", extra={
    "template_id": template_id,
    "user_id": user_id
})
```

## Testing Guidelines

### Test Structure

```python
def test_feature_name():
    """Test description"""
    # Arrange
    data = {"key": "value"}
    
    # Act
    result = function(data)
    
    # Assert
    assert result == expected
```

### Fixtures

Use pytest fixtures for common setup:

```python
@pytest.fixture
def sample_template():
    return {
        "template_id": "test_template",
        "name": "Test Template",
        "type": "email"
    }

def test_create_template(client, sample_template):
    response = client.post("/api/v1/templates", json=sample_template)
    assert response.status_code == 201
```

### Mocking

```python
from unittest.mock import patch, MagicMock

@patch('app.utils.rabbitmq.publish_event')
def test_event_publishing(mock_publish):
    service.create_template(data)
    mock_publish.assert_called_once()
```

### Test Coverage

Aim for >80% coverage:

```bash
pytest --cov=app --cov-report=term-missing
```

## Database Migrations

### Create Migration

```bash
# Auto-generate
alembic revision --autogenerate -m "Description"

# Manual
alembic revision -m "Description"
```

### Review Migration

Always review auto-generated migrations:

```python
# alembic/versions/xxx_description.py
def upgrade():
    op.add_column('templates', sa.Column('new_field', sa.String()))

def downgrade():
    op.drop_column('templates', 'new_field')
```

### Apply Migration

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Downgrade one version
alembic downgrade -1

# Show current version
alembic current
```

## Debugging

### VS Code Launch Configuration

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--port",
        "3004"
      ],
      "jinja": true,
      "justMyCode": false
    }
  ]
}
```

### Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Interactive Debugging

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use breakpoint() in Python 3.7+
breakpoint()
```

## Performance Profiling

### Profile Endpoint

```python
from fastapi import Request
import time

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### Memory Profiling

```bash
pip install memory-profiler

python -m memory_profiler script.py
```

## Common Tasks

### Add New Endpoint

1. Define schema in `app/schemas.py`
2. Add endpoint in `app/api/templates.py`
3. Add business logic in `app/services/template_service.py`
4. Write tests in `tests/test_api.py`

### Add New Model Field

1. Update model in `app/models.py`
2. Update schema in `app/schemas.py`
3. Create migration: `alembic revision --autogenerate -m "Add field"`
4. Apply migration: `alembic upgrade head`
5. Update tests

### Add New Dependency

```bash
# Add to requirements.txt
echo "package-name==1.0.0" >> requirements.txt

# Install
pip install -r requirements.txt

# Freeze exact versions
pip freeze > requirements.txt
```

## Troubleshooting

### Database Connection Error

```bash
# Check PostgreSQL is running
docker-compose ps postgres_template

# Test connection
psql $DATABASE_URL
```

### Migration Conflicts

```bash
# Show migration history
alembic history

# Downgrade to specific version
alembic downgrade <revision>

# Resolve conflicts and upgrade
alembic upgrade head
```

### Import Errors

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements-dev.txt
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Pytest Documentation](https://docs.pytest.org/)

## Getting Help

- Check [API Documentation](api/README.md)
- Review [Integration Guide](integration/README.md)
- Search [GitHub Issues](https://github.com/your-org/template-service/issues)
- Ask in team chat
