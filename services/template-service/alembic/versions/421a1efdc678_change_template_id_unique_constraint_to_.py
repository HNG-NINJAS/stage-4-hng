"""change_template_id_unique_constraint_to_partial

Revision ID: 421a1efdc678
Revises: 
Create Date: 2025-11-10 22:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '421a1efdc678'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the old unique index
    op.drop_index('ix_templates_template_id', table_name='templates')
    
    # Create a partial unique index (only for active templates)
    op.execute("""
        CREATE UNIQUE INDEX ix_templates_template_id_active 
        ON templates (template_id) 
        WHERE is_active = true
    """)
    
    # Recreate a non-unique index for all templates (for lookups)
    op.create_index('ix_templates_template_id', 'templates', ['template_id'], unique=False)


def downgrade() -> None:
    # Drop the non-unique index
    op.drop_index('ix_templates_template_id', table_name='templates')
    
    # Drop the partial unique index
    op.drop_index('ix_templates_template_id_active', table_name='templates')
    
    # Recreate the old unique index
    op.create_index('ix_templates_template_id', 'templates', ['template_id'], unique=True)
