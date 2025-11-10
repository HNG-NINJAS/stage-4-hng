"""
Tests for template service business logic
"""

import pytest
from app.services.template_service import TemplateService
from app.schemas import TemplateCreate, TemplateUpdate


def test_create_template(db_session):
    """Test creating a template"""
    service = TemplateService(db_session)
    template_data = TemplateCreate(
        template_id="test_email",
        name="Test Email",
        type="email",
        subject="Hello {{name}}",
        body="Welcome {{name}}!",
        language_code="en"
    )
    
    template = service.create_template(template_data)
    
    assert template.template_id == "test_email"
    assert template.name == "Test Email"
    assert len(template.versions) == 1
    assert len(template.translations) == 1


def test_create_duplicate_template(db_session):
    """Test creating template with duplicate ID fails"""
    service = TemplateService(db_session)
    template_data = TemplateCreate(
        template_id="duplicate",
        name="Test",
        type="email",
        body="Test",
        language_code="en"
    )
    
    service.create_template(template_data)
    
    with pytest.raises(ValueError, match="already exists"):
        service.create_template(template_data)


def test_get_template(db_session):
    """Test getting a template by ID"""
    service = TemplateService(db_session)
    template_data = TemplateCreate(
        template_id="get_test",
        name="Get Test",
        type="email",
        body="Test",
        language_code="en"
    )
    
    created = service.create_template(template_data)
    retrieved = service.get_template("get_test")
    
    assert retrieved is not None
    assert retrieved.id == created.id


def test_list_templates(db_session):
    """Test listing templates with pagination"""
    service = TemplateService(db_session)
    
    # Create multiple templates
    for i in range(5):
        template_data = TemplateCreate(
            template_id=f"test_{i}",
            name=f"Test {i}",
            type="email",
            body="Test",
            language_code="en"
        )
        service.create_template(template_data)
    
    templates, total = service.list_templates(skip=0, limit=10)
    
    assert len(templates) == 5
    assert total == 5


def test_list_templates_with_filter(db_session):
    """Test listing templates with type filter"""
    service = TemplateService(db_session)
    
    # Create email and push templates
    service.create_template(TemplateCreate(
        template_id="email1",
        name="Email",
        type="email",
        body="Test",
        language_code="en"
    ))
    service.create_template(TemplateCreate(
        template_id="push1",
        name="Push",
        type="push",
        body="Test",
        language_code="en"
    ))
    
    templates, total = service.list_templates(type="email")
    
    assert len(templates) == 1
    assert templates[0].type == "email"


def test_update_template(db_session):
    """Test updating template basic fields"""
    service = TemplateService(db_session)
    template_data = TemplateCreate(
        template_id="update_test",
        name="Original",
        type="email",
        body="Original body",
        language_code="en"
    )
    
    service.create_template(template_data)
    
    update_data = TemplateUpdate(name="Updated Name")
    updated = service.update_template("update_test", update_data)
    
    assert updated.name == "Updated Name"


def test_update_template_creates_new_version(db_session):
    """Test updating template body creates new version"""
    service = TemplateService(db_session)
    template_data = TemplateCreate(
        template_id="version_test",
        name="Test",
        type="email",
        body="Version 1.0.0",
        language_code="en"
    )
    
    created = service.create_template(template_data)
    assert len(created.versions) == 1
    
    update_data = TemplateUpdate(body="Version 1.0.1")
    updated = service.update_template("version_test", update_data)
    
    # Refresh to get versions
    db_session.refresh(updated)
    assert len(updated.versions) == 2


def test_delete_template(db_session):
    """Test soft deleting a template"""
    service = TemplateService(db_session)
    template_data = TemplateCreate(
        template_id="delete_test",
        name="Delete Test",
        type="email",
        body="Test",
        language_code="en"
    )
    
    service.create_template(template_data)
    success = service.delete_template("delete_test")
    
    assert success is True
    
    # Should not be retrievable after deletion
    deleted = service.get_template("delete_test")
    assert deleted is None


def test_render_template(db_session):
    """Test rendering a template"""
    service = TemplateService(db_session)
    template_data = TemplateCreate(
        template_id="render_test",
        name="Render Test",
        type="email",
        subject="Hello {{name}}",
        body="Welcome {{name}} to {{company}}!",
        language_code="en"
    )
    
    service.create_template(template_data)
    
    result = service.render_template(
        "render_test",
        {"name": "John", "company": "Acme"},
        "en"
    )
    
    assert result is not None
    assert result["subject"] == "Hello John"
    assert "John" in result["body"]
    assert "Acme" in result["body"]


def test_render_template_missing_variables(db_session):
    """Test rendering fails with missing variables"""
    service = TemplateService(db_session)
    template_data = TemplateCreate(
        template_id="missing_vars",
        name="Test",
        type="email",
        body="Hello {{name}} and {{friend}}!",
        language_code="en"
    )
    
    service.create_template(template_data)
    
    with pytest.raises(ValueError, match="Missing required variables"):
        service.render_template("missing_vars", {"name": "John"}, "en")


def test_add_translation(db_session):
    """Test adding a translation"""
    service = TemplateService(db_session)
    template_data = TemplateCreate(
        template_id="translation_test",
        name="Test",
        type="email",
        body="Hello {{name}}!",
        language_code="en"
    )
    
    service.create_template(template_data)
    
    translation = service.add_translation(
        "translation_test",
        "es",
        "¡Hola {{name}}!",
        "¡Bienvenido {{name}}!"
    )
    
    assert translation is not None
    assert translation.language_code == "es"


def test_render_template_with_translation(db_session):
    """Test rendering template with different language"""
    service = TemplateService(db_session)
    template_data = TemplateCreate(
        template_id="multi_lang",
        name="Test",
        type="email",
        body="Hello {{name}}!",
        language_code="en"
    )
    
    service.create_template(template_data)
    service.add_translation("multi_lang", "es", None, "¡Hola {{name}}!")
    
    result = service.render_template("multi_lang", {"name": "Juan"}, "es")
    
    assert result is not None
    assert "¡Hola Juan!" in result["body"]