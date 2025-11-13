"""
Tests for template renderer
"""

import pytest
from app.utils.renderer import TemplateRenderer


def test_render_simple_template():
    """Test rendering a simple template"""
    renderer = TemplateRenderer()
    template = "Hello {{name}}!"
    data = {"name": "John"}
    
    result = renderer.render(template, data)
    
    assert result == "Hello John!"


def test_render_multiple_variables():
    """Test rendering template with multiple variables"""
    renderer = TemplateRenderer()
    template = "Hi {{name}}, welcome to {{company}}!"
    data = {"name": "Jane", "company": "Acme Corp"}
    
    result = renderer.render(template, data)
    
    assert result == "Hi Jane, welcome to Acme Corp!"


def test_render_multiline_template():
    """Test rendering multiline template"""
    renderer = TemplateRenderer()
    template = """Hi {{name}},

Welcome to {{company}}!

Best regards,
The Team"""
    data = {"name": "Bob", "company": "Tech Inc"}
    
    result = renderer.render(template, data)
    
    assert "Bob" in result
    assert "Tech Inc" in result
    assert "Welcome to" in result


def test_extract_variables():
    """Test extracting variables from template"""
    renderer = TemplateRenderer()
    template = "Hello {{name}}, your email is {{email}}"
    
    variables = renderer.extract_variables(template)
    
    assert set(variables) == {"name", "email"}


def test_extract_variables_with_duplicates():
    """Test extracting variables removes duplicates"""
    renderer = TemplateRenderer()
    template = "Hi {{name}}, {{name}} is great!"
    
    variables = renderer.extract_variables(template)
    
    assert variables == ["name"]


def test_extract_variables_complex():
    """Test extracting variables from complex template"""
    renderer = TemplateRenderer()
    template = """
    Dear {{first_name}} {{last_name}},
    
    Your order #{{order_id}} totaling ${{amount}} has been confirmed.
    
    Email: {{email}}
    Phone: {{phone}}
    """
    
    variables = renderer.extract_variables(template)
    
    assert set(variables) == {"first_name", "last_name", "order_id", "amount", "email", "phone"}


def test_validate_variables_success():
    """Test variable validation with all variables provided"""
    renderer = TemplateRenderer()
    template = "Hello {{name}}!"
    data = {"name": "John"}
    
    is_valid, missing = renderer.validate_variables(template, data)
    
    assert is_valid is True
    assert missing == []


def test_validate_variables_missing():
    """Test variable validation with missing variables"""
    renderer = TemplateRenderer()
    template = "Hello {{name}}, email: {{email}}!"
    data = {"name": "John"}
    
    is_valid, missing = renderer.validate_variables(template, data)
    
    assert is_valid is False
    assert "email" in missing


def test_validate_variables_multiple_missing():
    """Test validation with multiple missing variables"""
    renderer = TemplateRenderer()
    template = "{{greeting}} {{name}}, your code is {{code}}"
    data = {"name": "Alice"}
    
    is_valid, missing = renderer.validate_variables(template, data)
    
    assert is_valid is False
    assert set(missing) == {"greeting", "code"}


def test_render_with_missing_variable():
    """Test rendering fails with missing variable"""
    renderer = TemplateRenderer()
    template = "Hello {{name}}!"
    data = {}
    
    with pytest.raises(ValueError):
        renderer.render(template, data)


def test_render_with_extra_variables():
    """Test rendering succeeds with extra variables"""
    renderer = TemplateRenderer()
    template = "Hello {{name}}!"
    data = {"name": "John", "extra": "data", "more": "stuff"}
    
    result = renderer.render(template, data)
    
    assert result == "Hello John!"


def test_render_complex_template():
    """Test rendering complex multi-line template"""
    renderer = TemplateRenderer()
    template = """
    Hi {{name}},
    
    Your order #{{order_id}} has been confirmed.
    Total: ${{total}}
    
    Items:
    {{items}}
    
    Thanks!
    """
    data = {
        "name": "Alice",
        "order_id": "12345",
        "total": "99.99",
        "items": "- Item 1\n- Item 2"
    }
    
    result = renderer.render(template, data)
    
    assert "Alice" in result
    assert "12345" in result
    assert "99.99" in result
    assert "Item 1" in result


def test_render_with_special_characters():
    """Test rendering with special characters in data"""
    renderer = TemplateRenderer()
    template = "Hello {{name}}!"
    data = {"name": "José García"}
    
    result = renderer.render(template, data)
    
    assert result == "Hello José García!"


def test_render_with_numbers():
    """Test rendering with numeric values"""
    renderer = TemplateRenderer()
    template = "Your balance is ${{balance}}"
    data = {"balance": 1234.56}
    
    result = renderer.render(template, data)
    
    assert "1234.56" in result


def test_render_with_boolean():
    """Test rendering with boolean values"""
    renderer = TemplateRenderer()
    template = "Active: {{is_active}}"
    data = {"is_active": True}
    
    result = renderer.render(template, data)
    
    assert "True" in result


def test_preview_render_success():
    """Test preview render with valid data"""
    renderer = TemplateRenderer()
    template = "Hello {{name}}!"
    data = {"name": "John"}
    
    result = renderer.preview_render(template, data)
    
    assert result["success"] is True
    assert result["rendered"] == "Hello John!"
    assert "name" in result["variables_used"]


def test_preview_render_missing_variables():
    """Test preview render with missing variables"""
    renderer = TemplateRenderer()
    template = "Hello {{name}} {{surname}}!"
    data = {"name": "John"}
    
    result = renderer.preview_render(template, data)
    
    assert result["success"] is False
    assert "surname" in result["missing_variables"]


def test_render_empty_template():
    """Test rendering empty template"""
    renderer = TemplateRenderer()
    template = ""
    data = {}
    
    result = renderer.render(template, data)
    
    assert result == ""


def test_render_template_without_variables():
    """Test rendering template without any variables"""
    renderer = TemplateRenderer()
    template = "This is a static message."
    data = {}
    
    result = renderer.render(template, data)
    
    assert result == "This is a static message."


def test_extract_variables_from_empty_template():
    """Test extracting variables from empty template"""
    renderer = TemplateRenderer()
    template = ""
    
    variables = renderer.extract_variables(template)
    
    assert variables == []


def test_variable_with_underscores():
    """Test variables with underscores"""
    renderer = TemplateRenderer()
    template = "Hello {{first_name}} {{last_name}}!"
    data = {"first_name": "John", "last_name": "Doe"}
    
    result = renderer.render(template, data)
    
    assert result == "Hello John Doe!"


def test_variable_with_numbers():
    """Test variables with numbers"""
    renderer = TemplateRenderer()
    template = "Code: {{code123}}"
    data = {"code123": "ABC"}
    
    result = renderer.render(template, data)
    
    assert result == "Code: ABC"