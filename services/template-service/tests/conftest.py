"""
Pytest configuration and fixtures
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models import Template, TemplateVersion, TemplateTranslation

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database session override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_template_data():
    """Sample template data for testing"""
    return {
        "template_id": "test_welcome",
        "name": "Test Welcome Email",
        "description": "Test template for welcome emails",
        "type": "email",
        "category": "onboarding",
        "subject": "Welcome {{name}}!",
        "body": "Hi {{name}}, welcome to {{company_name}}!",
        "language_code": "en"
    }


@pytest.fixture
def created_template(client, sample_template_data):
    """Create a template and return the response"""
    response = client.post("/api/v1/templates", json=sample_template_data)
    assert response.status_code == 201
    return response.json()["data"]