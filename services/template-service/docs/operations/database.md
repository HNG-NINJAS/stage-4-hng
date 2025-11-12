# Database Operations

Guide for managing Template Service database.

## Schema Overview

### Tables

#### templates
Main template records with metadata.

```sql
CREATE TABLE templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_templates_template_id ON templates(template_id);
CREATE INDEX idx_templates_type ON templates(type);
CREATE INDEX idx_templates_category ON templates(category);
CREATE INDEX idx_templates_is_active ON templates(is_active);
```

#### template_versions
Version history for templates.

```sql
CREATE TABLE template_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID REFERENCES templates(id) ON DELETE CASCADE,
    version VARCHAR(50) NOT NULL,
    subject TEXT,
    body TEXT NOT NULL,
    variables JSONB DEFAULT '[]',
    is_current BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_template_versions_template_id ON template_versions(template_id);
CREATE INDEX idx_template_versions_is_current ON template_versions(is_current);
```

#### template_translations
Multi-language support.

```sql
CREATE TABLE template_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_version_id UUID REFERENCES template_versions(id) ON DELETE CASCADE,
    language_code VARCHAR(10) NOT NULL,
    subject TEXT,
    body TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(template_version_id, language_code)
);

CREATE INDEX idx_template_translations_version_id ON template_translations(template_version_id);
CREATE INDEX idx_template_translations_language ON template_translations(language_code);
```

## Migrations

### Alembic Setup

Alembic is used for database migrations.

#### Configuration

```ini
# alembic.ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql://admin:admin123@localhost:5432/template_service

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

### Common Commands

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply all migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# View current version
alembic current

# Rollback to specific version
alembic downgrade <revision>
```

### Example Migration

```python
"""Add category column to templates

Revision ID: abc123
Revises: def456
Create Date: 2025-11-12 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'abc123'
down_revision = 'def456'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('templates', 
        sa.Column('category', sa.String(100), nullable=True)
    )
    op.create_index('idx_templates_category', 'templates', ['category'])

def downgrade():
    op.drop_index('idx_templates_category', 'templates')
    op.drop_column('templates', 'category')
```

## Backup & Restore

### Manual Backup

```bash
# Full database backup
pg_dump -h localhost -U admin -d template_service > backup.sql

# Compressed backup
pg_dump -h localhost -U admin -d template_service | gzip > backup.sql.gz

# Schema only
pg_dump -h localhost -U admin -d template_service --schema-only > schema.sql

# Data only
pg_dump -h localhost -U admin -d template_service --data-only > data.sql

# Specific table
pg_dump -h localhost -U admin -d template_service -t templates > templates.sql
```

### Restore

```bash
# Restore from backup
psql -h localhost -U admin -d template_service < backup.sql

# Restore compressed backup
gunzip -c backup.sql.gz | psql -h localhost -U admin -d template_service

# Restore specific table
psql -h localhost -U admin -d template_service < templates.sql
```

### Automated Backups

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/template_service_$TIMESTAMP.sql.gz"

# Create backup
pg_dump -h localhost -U admin -d template_service | gzip > $BACKUP_FILE

# Keep only last 7 days
find $BACKUP_DIR -name "template_service_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE"
```

### Cron Job

```bash
# Add to crontab
0 2 * * * /path/to/backup.sh >> /var/log/template_backup.log 2>&1
```

## Performance Optimization

### Indexes

```sql
-- Check missing indexes
SELECT
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE schemaname = 'public'
    AND tablename IN ('templates', 'template_versions', 'template_translations')
ORDER BY abs(correlation) DESC;

-- Create composite index for common queries
CREATE INDEX idx_templates_type_active ON templates(type, is_active);
CREATE INDEX idx_template_versions_template_current ON template_versions(template_id, is_current);
```

### Query Optimization

```sql
-- Analyze query performance
EXPLAIN ANALYZE
SELECT t.*, tv.*
FROM templates t
JOIN template_versions tv ON t.id = tv.template_id
WHERE t.template_id = 'welcome_email'
    AND tv.is_current = TRUE;

-- Update statistics
ANALYZE templates;
ANALYZE template_versions;
ANALYZE template_translations;

-- Vacuum tables
VACUUM ANALYZE templates;
VACUUM ANALYZE template_versions;
VACUUM ANALYZE template_translations;
```

### Connection Pooling

```python
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,          # Number of connections to maintain
    max_overflow=10,       # Additional connections when pool is full
    pool_timeout=30,       # Timeout for getting connection
    pool_recycle=3600,     # Recycle connections after 1 hour
    pool_pre_ping=True     # Verify connections before using
)
```

## Monitoring

### Database Metrics

```sql
-- Active connections
SELECT count(*) FROM pg_stat_activity WHERE datname = 'template_service';

-- Long running queries
SELECT
    pid,
    now() - query_start AS duration,
    query,
    state
FROM pg_stat_activity
WHERE state != 'idle'
    AND now() - query_start > interval '5 seconds'
ORDER BY duration DESC;

-- Table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Cache hit ratio
SELECT
    sum(heap_blks_read) as heap_read,
    sum(heap_blks_hit) as heap_hit,
    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as ratio
FROM pg_statio_user_tables;
```

### Slow Query Log

```sql
-- Enable slow query logging
ALTER DATABASE template_service SET log_min_duration_statement = 1000;

-- View slow queries
SELECT
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat_statements%'
ORDER BY mean_time DESC
LIMIT 10;
```

## Maintenance

### Regular Maintenance Tasks

```sql
-- Vacuum and analyze (weekly)
VACUUM ANALYZE templates;
VACUUM ANALYZE template_versions;
VACUUM ANALYZE template_translations;

-- Reindex (monthly)
REINDEX TABLE templates;
REINDEX TABLE template_versions;
REINDEX TABLE template_translations;

-- Update statistics (daily)
ANALYZE templates;
ANALYZE template_versions;
ANALYZE template_translations;
```

### Automated Maintenance

```sql
-- Enable autovacuum (should be on by default)
ALTER TABLE templates SET (autovacuum_enabled = true);
ALTER TABLE template_versions SET (autovacuum_enabled = true);
ALTER TABLE template_translations SET (autovacuum_enabled = true);

-- Adjust autovacuum settings
ALTER TABLE templates SET (
    autovacuum_vacuum_scale_factor = 0.1,
    autovacuum_analyze_scale_factor = 0.05
);
```

## Data Cleanup

### Soft Delete Cleanup

```sql
-- Find soft-deleted templates older than 30 days
SELECT id, template_id, deleted_at
FROM templates
WHERE deleted_at IS NOT NULL
    AND deleted_at < NOW() - INTERVAL '30 days';

-- Permanently delete old soft-deleted templates
DELETE FROM templates
WHERE deleted_at IS NOT NULL
    AND deleted_at < NOW() - INTERVAL '30 days';
```

### Old Version Cleanup

```sql
-- Keep only last 10 versions per template
WITH ranked_versions AS (
    SELECT
        id,
        template_id,
        ROW_NUMBER() OVER (PARTITION BY template_id ORDER BY created_at DESC) as rn
    FROM template_versions
)
DELETE FROM template_versions
WHERE id IN (
    SELECT id FROM ranked_versions WHERE rn > 10
);
```

## Disaster Recovery

### Point-in-Time Recovery

```bash
# Enable WAL archiving in postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /archive/%f'

# Create base backup
pg_basebackup -h localhost -U admin -D /backup/base -Fp -Xs -P

# Restore to specific point in time
# 1. Stop PostgreSQL
# 2. Replace data directory with base backup
# 3. Create recovery.conf
cat > recovery.conf << EOF
restore_command = 'cp /archive/%f %p'
recovery_target_time = '2025-11-12 10:00:00'
EOF
# 4. Start PostgreSQL
```

### Replication Setup

```sql
-- On primary server
CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'password';

-- In postgresql.conf
wal_level = replica
max_wal_senders = 3
wal_keep_segments = 64

-- In pg_hba.conf
host replication replicator replica_ip/32 md5

-- On replica server
pg_basebackup -h primary_ip -D /var/lib/postgresql/data -U replicator -P -v

-- Create recovery.conf on replica
cat > recovery.conf << EOF
standby_mode = 'on'
primary_conninfo = 'host=primary_ip port=5432 user=replicator password=password'
trigger_file = '/tmp/postgresql.trigger'
EOF
```

## Troubleshooting

### Connection Issues

```sql
-- Check max connections
SHOW max_connections;

-- Check current connections
SELECT count(*) FROM pg_stat_activity;

-- Kill idle connections
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
    AND state_change < NOW() - INTERVAL '1 hour';
```

### Lock Issues

```sql
-- Check for locks
SELECT
    l.pid,
    l.mode,
    l.granted,
    a.query
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid
WHERE NOT l.granted;

-- Kill blocking query
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE pid = <blocking_pid>;
```

### Disk Space

```sql
-- Check database size
SELECT pg_size_pretty(pg_database_size('template_service'));

-- Check table sizes
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Clean up bloat
VACUUM FULL templates;
```

## Security

### User Management

```sql
-- Create read-only user
CREATE USER readonly WITH PASSWORD 'password';
GRANT CONNECT ON DATABASE template_service TO readonly;
GRANT USAGE ON SCHEMA public TO readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;

-- Create application user
CREATE USER app_user WITH PASSWORD 'password';
GRANT CONNECT ON DATABASE template_service TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;
```

### Encryption

```sql
-- Enable SSL
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_cert_file = '/path/to/server.crt';
ALTER SYSTEM SET ssl_key_file = '/path/to/server.key';

-- Require SSL for connections
ALTER DATABASE template_service SET ssl = on;
```

## Next Steps

- Configure [Monitoring](./monitoring.md)
- Review [Deployment](./deployment.md)
- Set up [Integration](../integration/overview.md)
