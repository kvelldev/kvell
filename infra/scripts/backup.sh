#!/bin/bash
# Kvell MongoDB Backup Script
# Called by cron hourly
set -euo pipefail

BACKUP_BUCKET="${BACKUP_BUCKET:-kvell-prod-backups}"
TIMESTAMP=$(date +%Y%m%d-%H%M)

# Dump bonfires collection only
docker exec kvell-mongo-1 mongodump \
    --uri="mongodb://localhost:27017/kvell" \
    --collection=bonfires \
    --out=/tmp/backup

# Upload to S3
docker cp kvell-mongo-1:/tmp/backup/kvell/bonfires.bson /tmp/
aws s3 cp /tmp/bonfires.bson "s3://${BACKUP_BUCKET}/bonfires-${TIMESTAMP}.bson"

# Cleanup
docker exec kvell-mongo-1 rm -rf /tmp/backup
rm -f /tmp/bonfires.bson

echo "$(date): Backup completed - bonfires-${TIMESTAMP}.bson"
