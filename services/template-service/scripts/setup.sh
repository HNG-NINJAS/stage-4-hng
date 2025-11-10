#!/bin/bash

# Quick setup script to create folder structure

echo "🏗️  Creating Template Service folder structure..."

# Create directories
mkdir -p app/{api,services,utils}
mkdir -p tests
mkdir -p alembic/versions
mkdir -p scripts

# Create Python files
touch app/__init__.py
touch app/main.py
touch app/config.py
touch app/database.py
touch app/models.py
touch app/schemas.py

touch app/api/__init__.py
touch app/api/templates.py
touch app/api/health.py
touch app/api/metrics.py

touch app/services/__init__.py
touch app/services/template_service.py

touch app/utils/__init__.py
touch app/utils/response.py
touch app/utils/renderer.py

# Create test files
touch tests/__init__.py
touch tests/conftest.py
touch tests/test_template_service.py
touch tests/test_renderer.py
touch tests/test_api.py

# Create alembic files
touch alembic/env.py
touch alembic/script.py.mako

# Create script files
touch scripts/seed_templates.py
touch scripts/test_api.sh
touch scripts/run_dev.sh

# Create config files
touch requirements.txt
touch requirements-dev.txt
touch Dockerfile
touch .dockerignore
touch .env.example
touch .gitignore
touch alembic.ini
touch pytest.ini
touch README.md
touch INTEGRATION.md

# Make scripts executable
chmod +x scripts/*.sh
chmod +x scripts/seed_templates.py

echo "✅ Folder structure created successfully!"
echo ""
echo "Next steps:"
echo "1. Copy the code into each file"
echo "2. Run: python3 -m venv venv"
echo "3. Run: source venv/bin/activate"
echo "4. Run: pip install -r requirements-dev.txt"
echo "5. Run: cp .env.example .env"
echo "6. Run: alembic upgrade head"
echo "7. Run: ./scripts/run_dev.sh"