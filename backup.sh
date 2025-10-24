#!/bin/bash
# GIVC Platform Backup Script

BACKUP_DIR="/home/pi/GIVC/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

echo "🔄 Starting backup at $(date)"

# Backup PostgreSQL
echo "  📦 Backing up PostgreSQL..."
docker exec givc-postgres pg_dump -U givc givc_prod | gzip > "$BACKUP_DIR/postgres_${TIMESTAMP}.sql.gz"

# Backup Redis
echo "  📦 Backing up Redis..."
docker exec givc-redis redis-cli -a redis_pass SAVE 2>/dev/null
docker cp givc-redis:/data/dump.rdb "$BACKUP_DIR/redis_${TIMESTAMP}.rdb"

# Backup configuration files
echo "  📦 Backing up configuration..."
tar -czf "$BACKUP_DIR/config_${TIMESTAMP}.tar.gz" \
    docker-compose.yml \
    nginx/ \
    .env 2>/dev/null || true

# Clean old backups (keep last 7 days)
find "$BACKUP_DIR" -name "*.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.rdb" -mtime +7 -delete

echo "✅ Backup completed: $BACKUP_DIR"
ls -lh "$BACKUP_DIR" | tail -5
