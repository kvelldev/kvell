#!/bin/bash
# TODO: netstat対応
set -euo pipefail

# This script is downloaded and executed by EC2 UserData
# Environment variables like BACKUP_BUCKET, REPO_URL should be exported by the caller if needed.

export AWS_DEFAULT_REGION="ap-northeast-1"
readonly TARGET_USER="ubuntu"
readonly TARGET_HOME="/home/${TARGET_USER}"

# logging settings
LOG_FILE="/var/log/user-data-script.log"
exec > >(tee -a "$LOG_FILE")
exec 2>&1

# utility functions
mkdir -p /opt/scripts
cat <<"EOF" > /opt/scripts/common-functions.sh
error_exit() {
    echo "$(date): ERROR: $1" >&2
    exit 1
}

log_info() {
    echo "$(date): INFO: $1"
}

log_success() {
    echo "$(date): SUCCESS: $1"
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}
EOF
source /opt/scripts/common-functions.sh

# --------------------------------------------------------------------
# system settings
# --------------------------------------------------------------------

setup_system() {
    log_info "Setting up system configuration..."

    # timezone
    timedatectl set-timezone Asia/Tokyo || error_exit "Failed to set timezone"
    log_success "Timezone set to Asia/Tokyo"

    # apt
    apt update -y && apt upgrade -y || error_exit "Failed to update packages"
    log_success "Packages updated"
}

install_essential_packages() {
    log_info "Installing essential packages..."

    local packages=(
        git curl wget unzip build-essential sqlite3 gnupg
        # Python build deps (optional if using pre-built python via uv, but good to have)
        libbz2-dev libssl-dev libreadline-dev libffi-dev zlib1g-dev
        libncurses5-dev libncursesw5-dev libsqlite3-dev libgdbm-dev
        liblzma-dev tk-dev uuid-dev
    )

    apt install -y "${packages[@]}" || error_exit "Failed to install essential packages"
    log_success "Essential packages installed"
}

# --------------------------------------------------------------------
# Performance Tuning (Swap & File Descriptors)
# --------------------------------------------------------------------

tune_system_performance() {
    log_info "Tuning system performance (Swap & Limits)..."

    # 1. Swap Setup (2GB) for t3.medium
    if [ ! -f /swapfile ]; then
        log_info "Creating 2GB swapfile..."
        fallocate -l 2G /swapfile
        chmod 600 /swapfile
        mkswap /swapfile
        swapon /swapfile
        echo '/swapfile none swap sw 0 0' >> /etc/fstab
        log_success "Swap created"
    else
        log_info "Swapfile already exists. Skipping."
    fi

    # 2. Tune File Descriptors (OS Level)
    log_info "Tuning file descriptors for WebSockets..."

    # System-wide limit
    if ! grep -q "fs.file-max = 100000" /etc/sysctl.conf; then
        echo "fs.file-max = 100000" >> /etc/sysctl.conf
        sysctl -p
    fi

    # User limits (hard & soft)
    if ! grep -q "* soft nofile 100000" /etc/security/limits.conf; then
        cat <<EOF >> /etc/security/limits.conf
* soft nofile 100000
* hard nofile 100000
root soft nofile 100000
root hard nofile 100000
EOF
    fi

    log_success "System performance tuning completed"
}

# --------------------------------------------------------------------
# AWS
# --------------------------------------------------------------------

install_aws_cli() {
    log_info "Installing AWS CLI (v2)..."
    if command_exists aws; then
        log_info "AWS CLI found, skipping install."
        return 0
    fi

    local temp_dir="/tmp/aws-cli-install"
    mkdir -p "$temp_dir" && cd "$temp_dir"

    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip -o awscliv2.zip
    ./aws/install --update

    rm -rf "$temp_dir"
    log_success "AWS CLI installed"
}

install_ssm_agent() {
    log_info "Installing SSM Agent..."
    if snap list 2>/dev/null | grep -q amazon-ssm-agent; then
        return 0
    fi
    snap install amazon-ssm-agent --classic
    snap start amazon-ssm-agent
    log_success "SSM Agent installed"
}

# --------------------------------------------------------------------
# Application Setup (uv, git, venv)
# --------------------------------------------------------------------

install_uv() {
    log_info "Installing uv for user ${TARGET_USER}..."

    # Run installer as ubuntu user
    # uv installs to ~/.local/bin or ~/.cargo/bin depending on version,
    # forcing standard install script
    sudo -u "${TARGET_USER}" curl -LsSf https://astral.sh/uv/install.sh | sudo -u "${TARGET_USER}" sh

    log_success "uv installed"
}

setup_kvell_app() {
    log_info "Setting up Kvell application..."

    # Default Repo URL (Can be overridden by env var)
    local REPO_URL="${REPO_URL:-https://github.com/kvelldev/kvell.git}"
    local WS_DIR="${TARGET_HOME}/ws"
    local APP_DIR="${WS_DIR}/kvell/apps/api"
    local PARAM_NAME="/kvell/prod/github_pat"


    # 1. Clone Repository (as ubuntu user)
    # 1-a. Get PAT from SSM
    log_info "Fetching GitHub PAT from SSM..."
    local GITHUB_TOKEN
    GITHUB_TOKEN=$(aws ssm get-parameter --region ap-northeast-1 --name "${PARAM_NAME}" --with-decryption --query "Parameter.Value" --output text) || error_exit "Failed to get PAT from SSM"

    # 1-b. Git auth configuration (setup for ubuntu user)
    log_info "Configuring Git authentication..."
    sudo -u "${TARGET_USER}" git config --global url."https://${GITHUB_TOKEN}:@github.com/".insteadOf "https://github.com/"

    # 1-c. clone.
    sudo -u "${TARGET_USER}" mkdir -p "${WS_DIR}"

    if [ ! -d "${WS_DIR}/kvell" ]; then
        log_info "Cloning ${REPO_URL}..."
        sudo -u "${TARGET_USER}" git clone "${REPO_URL}" "${WS_DIR}/kvell"
    else
        log_info "Repository exists, pulling latest..."
        cd "${WS_DIR}/kvell"
        sudo -u "${TARGET_USER}" git pull
    fi

    # 1.5 Create .env file based on example
    log_info "Creating .env file from example..."
    if [ -f "${APP_DIR}/.env.example" ]; then
        cp "${APP_DIR}/.env.example" "${APP_DIR}/.env"
    elif [ -f "${WS_DIR}/kvell/.env.example" ]; then
         cp "${WS_DIR}/kvell/.env.example" "${APP_DIR}/.env"
    else
        log_info "No .env.example found, creating empty .env"
        touch "${APP_DIR}/.env"
    fi

    # Append production settings
    cat <<EOF >> "${APP_DIR}/.env"

# Production Settings (Appended by setup script)
ENV=production
MONGO_URI=mongodb://localhost:27017
MONGO_DB=kvell
REDIS_URI=redis://localhost:6379
CORS_ORIGINS="${CORS_ORIGINS:-https://kvellapp.com}"
# Add other env vars here as needed (OR rely on systemd Environment)
EOF
    chown "${TARGET_USER}:${TARGET_USER}" "${APP_DIR}/.env"

    # 1.6 Start DB Containers
    log_info "Starting Database containers..."
    if [ -f "${WS_DIR}/kvell/docker-compose.yml" ]; then
        cd "${WS_DIR}/kvell"
        # Start mongo and redis only
        sudo -u "${TARGET_USER}" docker compose up -d mongo redis || log_info "Failed to start DB containers (maybe compose file differs?)"
        log_info "Waiting for DB to initialize..."
        sleep 15
    else
        log_info "No docker-compose.yml found, skipping DB start."
    fi



    # 2. Setup Python Environment with uv (as ubuntu user)
    if [ -d "${APP_DIR}" ]; then
        log_info "Setting up virtualenv in ${APP_DIR}..."
        cd "${APP_DIR}"

        # Path to uv executable (check both .local/bin and .cargo/bin)
        local UV_BIN="${TARGET_HOME}/.local/bin/uv"
        if [ ! -f "${UV_BIN}" ]; then
            UV_BIN="${TARGET_HOME}/.cargo/bin/uv"
        fi

        # Verify uv exists
        if [ ! -f "${UV_BIN}" ]; then
             error_exit "uv executable not found at ${UV_BIN} or .local/bin"
        fi

        # Initialize venv
        sudo -u "${TARGET_USER}" "${UV_BIN}" venv

        # Install dependencies
        # Assuming requirements.txt exists. If pyproject.toml is used, use 'uv sync'
        if [ -f "requirements.txt" ]; then
             sudo -u "${TARGET_USER}" "${UV_BIN}" pip install -r requirements.txt
        elif [ -f "pyproject.toml" ]; then
             sudo -u "${TARGET_USER}" "${UV_BIN}" sync
        else
             log_info "No requirements found, installing minimal deps..."
             sudo -u "${TARGET_USER}" "${UV_BIN}" pip install uvicorn fastapi
        fi

        log_success "Python environment created"
    else
        error_exit "App directory not found: ${APP_DIR}"
    fi
}

setup_systemd_service() {
    log_info "Configuring Systemd service..."

    # Write the service file
    cat <<EOF > /etc/systemd/system/kvell-api.service
[Unit]
Description=Kvell API
After=network.target

[Service]
User=${TARGET_USER}
Group=${TARGET_USER}
WorkingDirectory=${TARGET_HOME}/ws/kvell/apps/api
Environment="PATH=${TARGET_HOME}/ws/kvell/apps/api/.venv/bin:/usr/local/bin:/usr/bin"
Environment="PYTHONPATH=${TARGET_HOME}/ws/kvell/apps/api/src"
ExecStart=${TARGET_HOME}/ws/kvell/apps/api/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    # Enable and start
    systemctl daemon-reload
    systemctl enable kvell-api
    systemctl start kvell-api

    log_success "Kvell API service started"
}

# --------------------------------------------------------------------
# Docker & Backup (Existing)
# --------------------------------------------------------------------

install_docker() {
    log_info "Installing Docker..."


    if ! command_exists docker; then
        install -m 0755 -d /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

        apt update -y
        apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
        usermod -aG docker "${TARGET_USER}"
    fi

    # Docker Daemon Configuration
    # WebSocket用にulimitを緩和し、ログ肥大化を防ぐ設定を入れる
    if [ ! -f /etc/docker/daemon.json ]; then
        log_info "Configuring Docker daemon (ulimits & logs)..."
        mkdir -p /etc/docker
        cat <<EOF > /etc/docker/daemon.json
{
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 65535,
      "Soft": 65535
    }
  },
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF
        # 設定反映のため再起動
        systemctl restart docker
        log_success "Docker configured and restarted"
    fi


    log_success "Docker installed/verified"
}

setup_backup() {
    log_info "Setting up backup script..."
    if [ -z "${SCRIPT_BUCKET:-}" ]; then
        log_info "SCRIPT_BUCKET not set, skipping backup script download."
        return 0
    fi

    aws s3 cp "s3://${SCRIPT_BUCKET}/backup.sh" /opt/scripts/backup.sh
    chmod +x /opt/scripts/backup.sh
    ln -sf /opt/scripts/backup.sh /etc/cron.daily/kvell-backup
    log_success "Backup configured"
}

setup_data_volume() {
    log_info "Mounting Data Volume..."

    # 1. デバイス名の特定
    # Nitro系(t3など)は /dev/nvme1n1、旧世代は /dev/xvdf
    local DEVICE=""

    if [ -b "/dev/nvme1n1" ]; then
        DEVICE="/dev/nvme1n1"
    elif [ -b "/dev/xvdf" ]; then
        DEVICE="/dev/xvdf"
    else
        # 【変更点】 デバイスが見つからない場合はここで処理を強制終了(Panic)させる
        # これにより Cloud-init が失敗ステータスとなり、異常に気づけます
        error_exit "CRITICAL: Data Volume device not found! Expected /dev/nvme1n1 or /dev/xvdf."
    fi

    log_info "Target device found: $DEVICE"

    # 2. フォーマット（冪等性あり）
    # blkid が失敗する(=未フォーマット)時だけ実行
    if ! blkid "$DEVICE" > /dev/null 2>&1; then
        log_info "Formatting $DEVICE..."
        mkfs -t xfs "$DEVICE" || error_exit "Failed to format $DEVICE"
    fi

    # マウントポイント作成
    mkdir -p /data

    # 3. マウント（冪等性あり）
    # すでにマウントされていない場合のみ mount コマンドを実行
    if ! mountpoint -q /data; then
        mount "$DEVICE" /data || error_exit "Failed to mount $DEVICE"
        log_success "Mounted $DEVICE to /data"
    else
        log_info "/data is already mounted. Skipping."
    fi

    # 4. fstabへの追記（冪等性あり）
    # UUIDではなくデバイス名で書く簡易方式（再起動後も同じデバイス名である前提）
    if ! grep -q "$DEVICE /data xfs" /etc/fstab; then
        echo "$DEVICE /data xfs defaults,nofail 0 2" >> /etc/fstab
        log_success "Added entry to /etc/fstab"
    fi

    # Docker用のディレクトリ作成
    mkdir -p /data/mongo /data/redis
}

main() {
    log_info "Starting Setup..."

    setup_system
    setup_data_volume
    tune_system_performance
    install_essential_packages
    install_aws_cli
    install_ssm_agent
    install_docker

    # New App Setup Steps
    install_uv
    setup_kvell_app
    setup_systemd_service

    setup_backup

    log_info "Setup Completed"
    echo "Setup finished at $(date)" | tee /etc/motd
}

main "$@"
