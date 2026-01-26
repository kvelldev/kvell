#!/bin/bash
# Kvell MongoDB Backup Script
# Called by cron daily
set -euo pipefail

BACKUP_BUCKET="${BACKUP_BUCKET:-kvell-prod-backups}"
TIMESTAMP=$(date +%Y%m%d-%H%M)
CONTAINER_NAME="kvell-mongo-1"

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "$(date): Error - Container ${CONTAINER_NAME} is not running. Skipping backup."
    exit 1
fi

# Dump bonfires collection only
docker exec ${CONTAINER_NAME} mongodump \
    --uri="mongodb://localhost:27017/kvell" \
    --collection=bonfires \
    --out=/tmp/backup

# Upload to S3
docker cp ${CONTAINER_NAME}:/tmp/backup/kvell/bonfires.bson /tmp/
aws s3 cp /tmp/bonfires.bson "s3://${BACKUP_BUCKET}/bonfires-${TIMESTAMP}.bson"

# Cleanup
docker exec ${CONTAINER_NAME} rm -rf /tmp/backup
rm -f /tmp/bonfires.bson

echo "$(date): Backup completed - bonfires-${TIMESTAMP}.bson"
