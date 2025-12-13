#!/bin/bash
# Kvell Production Setup Script
# FastAPI runs natively via systemd, MongoDB/Redis in Docker
set -euo pipefail

readonly KVELL_HOME="/opt/kvell"
readonly LOG_FILE="/var/log/kvell-setup.log"

exec > >(tee -a "$LOG_FILE")
exec 2>&1

log_info() { echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] $1"; }
log_error() { echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $1" >&2; }
log_success() { echo "$(date '+%Y-%m-%d %H:%M:%S') [SUCCESS] $1"; }

# --------------------------------------------------------------------
# System Setup
# --------------------------------------------------------------------
setup_system() {
    log_info "Setting up system..."

    timedatectl set-timezone Asia/Tokyo

    apt update -y && apt upgrade -y
    apt install -y curl wget unzip jq git python3 python3-pip python3-venv

    # Install AWS CLI v2
    if ! command -v aws &> /dev/null; then
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "/tmp/awscliv2.zip"
        unzip -q /tmp/awscliv2.zip -d /tmp
        /tmp/aws/install
        rm -rf /tmp/aws /tmp/awscliv2.zip
    fi

    log_success "System setup completed"
}

# --------------------------------------------------------------------
# Docker Installation (for MongoDB/Redis only)
# --------------------------------------------------------------------
install_docker() {
    log_info "Installing Docker..."

    if command -v docker &> /dev/null; then
        log_info "Docker already installed"
        return 0
    fi

    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
      https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
      | tee /etc/apt/sources.list.d/docker.list > /dev/null

    apt update -y
    apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

    systemctl enable --now docker

    log_success "Docker installed"
}

# --------------------------------------------------------------------
# Setup Python Environment
# --------------------------------------------------------------------
setup_python_env() {
    log_info "Setting up Python environment..."

    cd "$KVELL_HOME/apps/api"

    # Create venv as root (will be used by ubuntu user via systemd)
    python3 -m venv .venv

    # Install uv and dependencies
    .venv/bin/pip install --upgrade pip
    .venv/bin/pip install uv
    .venv/bin/uv sync --frozen

    # Fix ownership for ubuntu user
    chown -R ubuntu:ubuntu .venv

    log_success "Python environment setup completed"
}

# --------------------------------------------------------------------
# Setup systemd Service for API
# --------------------------------------------------------------------
setup_api_service() {
    log_info "Setting up Kvell API systemd service..."

    cat > /etc/systemd/system/kvell-api.service << EOF
[Unit]
Description=Kvell FastAPI Application
After=network.target docker.service
Wants=docker.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/kvell/apps/api
Environment="PATH=/opt/kvell/apps/api/.venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=/opt/kvell/apps/api/src"
Environment="MONGODB_URI=mongodb://localhost:27017/kvell?replicaSet=rs0"
Environment="REDIS_URL=redis://localhost:6379"
Environment="CORS_ORIGINS=${CORS_ORIGINS:-https://kvellapp.com}"
Environment="LOG_LEVEL=info"
ExecStart=/opt/kvell/apps/api/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable kvell-api

    log_success "Kvell API systemd service configured"
}

# --------------------------------------------------------------------
# Start Database Services (Docker)
# --------------------------------------------------------------------
start_database_services() {
    log_info "Starting database services (MongoDB/Redis)..."

    mkdir -p /data/mongo
    chown -R 999:999 /data/mongo  # MongoDB container user

    cd "$KVELL_HOME"

    # Use database-only compose file
    docker compose -f docker-compose.db.yml up -d

    # Wait for MongoDB to be ready
    log_info "Waiting for MongoDB to be ready..."
    sleep 10

    log_success "Database services started"
}

# --------------------------------------------------------------------
# Start API Service
# --------------------------------------------------------------------
start_api_service() {
    log_info "Starting Kvell API service..."

    systemctl start kvell-api

    # Wait and check status
    sleep 3
    if systemctl is-active --quiet kvell-api; then
        log_success "Kvell API service started successfully"
    else
        log_error "Kvell API service failed to start"
        journalctl -u kvell-api.service -n 20
        exit 1
    fi
}

# --------------------------------------------------------------------
# Backup Script Setup
# --------------------------------------------------------------------
setup_backup() {
    log_info "Setting up backup cron job..."

    echo "0 * * * * root BACKUP_BUCKET=${BACKUP_BUCKET:-} $KVELL_HOME/infra/scripts/backup.sh >> /var/log/kvell-backup.log 2>&1" > /etc/cron.d/kvell-backup

    log_success "Backup cron job configured"
}

# --------------------------------------------------------------------
# Main
# --------------------------------------------------------------------
main() {
    log_info "Starting Kvell production setup (non-containerized API)..."

    setup_system
    install_docker
    setup_python_env
    setup_api_service
    start_database_services
    start_api_service
    setup_backup

    # Update MOTD
    cat > /etc/motd << 'MOTD'

╔══════════════════════════════════════════════════════════════╗
║                    🔥 KVELL SERVER 🔥                        ║
╠══════════════════════════════════════════════════════════════╣
║  API:       systemctl status kvell-api                       ║
║  Logs:      journalctl -u kvell-api -f                       ║
║  Health:    curl http://localhost:8000/api/health            ║
║  MongoDB:   docker logs kvell-mongo-1                        ║
║  Redis:     docker logs kvell-redis-1                        ║
╚══════════════════════════════════════════════════════════════╝

MOTD

    log_success "Kvell production setup completed!"
}

main "$@"
