#!/bin/bash
# Kvell Production Setup Script
# This script is embedded in UserData and clones the repo from GitHub
set -euo pipefail

readonly KVELL_HOME="/opt/kvell"
readonly GITHUB_REPO="${GITHUB_REPO:-https://github.com/your-org/kvell.git}"
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
    apt install -y curl wget unzip jq git

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
# Docker Installation
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
# Clone Repository
# --------------------------------------------------------------------
clone_repo() {
    log_info "Cloning Kvell repository..."

    mkdir -p /data/mongo

    if [ -d "$KVELL_HOME" ]; then
        cd "$KVELL_HOME"
        git pull
    else
        git clone "$GITHUB_REPO" "$KVELL_HOME"
    fi

    cd "$KVELL_HOME"

    # Create .env file
    cat > .env << EOF
ECR_REPO=${ECR_REPO}
IMAGE_TAG=${IMAGE_TAG:-latest}
CORS_ORIGINS=${CORS_ORIGINS}
LOG_LEVEL=info
EOF

    log_success "Repository cloned"
}

# --------------------------------------------------------------------
# Backup Script Setup
# --------------------------------------------------------------------
setup_backup() {
    log_info "Setting up backup cron job..."

    # Add cron job (hourly backup)
    echo "0 * * * * root BACKUP_BUCKET=${BACKUP_BUCKET} $KVELL_HOME/infra/scripts/backup.sh >> /var/log/kvell-backup.log 2>&1" > /etc/cron.d/kvell-backup

    log_success "Backup cron job configured"
}

# --------------------------------------------------------------------
# Start Application
# --------------------------------------------------------------------
start_application() {
    log_info "Starting Kvell application..."

    cd "$KVELL_HOME"

    # Login to ECR
    aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPO%%/*}

    # Use production compose file
    docker compose -f docker-compose.prod.yml pull
    docker compose -f docker-compose.prod.yml up -d

    log_success "Kvell application started"
}

# --------------------------------------------------------------------
# Main
# --------------------------------------------------------------------
main() {
    log_info "Starting Kvell production setup..."

    setup_system
    install_docker
    clone_repo
    setup_backup
    start_application

    log_success "Kvell production setup completed!"
    echo "Kvell setup completed at $(date)" | tee /etc/motd
}

main "$@"
