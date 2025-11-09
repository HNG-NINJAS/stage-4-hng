"""
SQLAlchemy database models
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class Template(Base):
    """Main template table"""
    
    __tablename__ = "templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String(50), nullable=False, index=True)  # email, push, sms
    category = Column(String(100), nullable=True, index=True)  # welcome, alert, marketing
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    versions = relationship(
        "TemplateVersion",
        back_populates="template",
        cascade="all, delete-orphan",
        lazy="select"
    )
    translations = relationship(
        "TemplateTranslation",
        back_populates="template",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self):
        return f"<Template(id={self.template_id}, name={self.name}, type={self.type})>"


class TemplateVersion(Base):
    """Template version history"""
    
    __tablename__ = "template_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("templates.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(String(20), nullable=False)  # 1.0.0, 1.0.1, etc.
    subject = Column(String(500), nullable=True)  # For email templates
    body = Column(Text, nullable=False)
    variables = Column(JSON, nullable=False, default=list)  # ["name", "email"]
    metadata = Column(JSON, nullable=True, default=dict)
    is_current = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(100), nullable=True)
    
    # Relationship
    template = relationship("Template", back_populates="versions")

    def __repr__(self):
        return f"<TemplateVersion(version={self.version}, current={self.is_current})>"


class TemplateTranslation(Base):
    """Multi-language template support"""
    
    __tablename__ = "template_translations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("templates.id", ondelete="CASCADE"), nullable=False, index=True)
    language_code = Column(String(10), nullable=False, index=True)  # en, es, fr, etc.
    subject = Column(String(500), nullable=True)
    body = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship
    template = relationship("Template", back_populates="translations")

    def __repr__(self):
        return f"<TemplateTranslation(language={self.language_code})>"