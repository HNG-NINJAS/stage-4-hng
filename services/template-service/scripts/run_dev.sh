#!/bin/bash

# Development server startup script

set -e

echo "🚀 Starting Template Service in Development Mode..."
echo ""

# Check for virtual environment (supports both venv and .venv)
VENV_DIR=""
if [ -d "venv" ]; then
    VENV_DIR="venv"
elif [ -d ".venv" ]; then
    VENV_DIR=".venv"
fi

# Create virtual environment if it doesn't exist
if [ -z "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    VENV_DIR=".venv"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment ($VENV_DIR)..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements-dev.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "⚠️  Please update .env with your configuration"
    else
        echo "❌ .env.example not found. Creating default .env..."
        cat > .env << 'EOF'
DATABASE_URL=postgresql://admin:admin123@localhost:5433/template_service
REDIS_URL=redis://localhost:6379/0
SERVICE_NAME=template-service
SERVICE_VERSION=1.0.0
PORT=3004
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO
EOF
        echo "✅ Created default .env file"
    fi
fi

# Check if database is accessible
echo "🗄️  Checking database connection..."
if command -v psql &> /dev/null; then
    if psql -h localhost -p 5433 -U admin -d template_service -c "SELECT 1" > /dev/null 2>&1; then
        echo "✅ Database connection successful"
    else
        echo "⚠️  Warning: Cannot connect to database"
        echo "   Make sure PostgreSQL is running:"
        echo "   docker-compose up -d postgres_template"
    fi
else
    echo "⚠️  psql not found, skipping database check"
fi

# Run database migrations
echo "🗄️  Running database migrations..."
if command -v alembic &> /dev/null; then
    if alembic upgrade head; then
        echo "✅ Migrations applied successfully"
    else
        echo "❌ Migration failed. Check database connection."
        echo "   You can skip this step and run manually later:"
        echo "   alembic upgrade head"
    fi
else
    echo "⚠️  Alembic not found, skipping migrations"
fi

# Start the service
echo ""
echo "=================================================="
echo "✅ Starting Template Service"
echo "=================================================="
echo "🌐 Service URL:    http://localhost:3004"
echo "📚 API Docs:       http://localhost:3004/docs"
echo "❤️  Health Check:  http://localhost:3004/health"
echo "📊 Metrics:        http://localhost:3004/metrics"
echo "=================================================="
echo ""
echo "Press Ctrl+C to stop"
echo ""

uvicorn app.main:app --reload --port 3004 --log-level info