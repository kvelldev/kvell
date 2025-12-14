#!/bin/bash
set -euo pipefail

# --------------------------------------------------------------------
# 設定・定数
# --------------------------------------------------------------------
readonly KVELL_HOME="/opt/kvell"
readonly LOG_FILE="/var/log/setup-prod.log"
# UserDataから渡された環境変数がもしあれば使うが、基本はここで定義またはSSMから取得
readonly REGION=$(curl -s http://169.254.169.254/latest/meta-data/placement/region)

exec > >(tee -a "$LOG_FILE") 2>&1

log_info() { echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] $1"; }
log_error() { echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $1" >&2; }

# --------------------------------------------------------------------
# 1. EBSボリュームのマウント (MongoDB用)
# --------------------------------------------------------------------
setup_volume() {
    log_info "Setting up data volume..."

    # マウントポイント作成
    mkdir -p /data

    # 既にマウント済みか確認
    if mountpoint -q /data; then
        log_info "Volume already mounted at /data"
        return 0
    fi

    # NVMeデバイスを探す (AWSのGP3ボリュームはNVMeとして認識される)
    # 実際には blkid でUUIDを確認してマウントするのが確実ですが、
    # ここではシンプルに「まだフォーマットされていないディスクがあれば使う」ロジック例
    # ※本番では CloudFormation で指定した VolumeID を元に特定するのがベスト

    # 簡易版: /dev/nvme1n1 (通常、ルートの次に来るEBS) を対象とする
    TARGET_DEV="/dev/nvme1n1"

    if [ -b "$TARGET_DEV" ]; then
        # ファイルシステムがなければ作成
        if ! blkid "$TARGET_DEV"; then
            log_info "Formatting $TARGET_DEV..."
            mkfs.ext4 "$TARGET_DEV"
        fi

        mount "$TARGET_DEV" /data
        echo "$TARGET_DEV /data ext4 defaults,nofail 0 2" >> /etc/fstab
        log_info "Mounted $TARGET_DEV to /data"
    else
        log_error "Data volume device not found!"
        # 初回起動でEBSアタッチに時間がかかっている場合の待機ロジックが必要なら追加
    fi
}

# --------------------------------------------------------------------
# 2. Python環境構築 (uv を使用)
# --------------------------------------------------------------------
setup_python() {
    log_info "Setting up Python with uv..."

    # uv のインストール
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"

    cd "$KVELL_HOME/apps/api"

    # システムのPythonではなく、uv管理下のPythonを使って仮想環境作成 (爆速)
    # コンパイル不要。バイナリをダウンロードしてくるだけ。
    uv venv .venv --python 3.11

    # 依存関係のインストール
    uv sync --frozen

    # 権限修正
    chown -R ubuntu:ubuntu "$KVELL_HOME"
    log_info "Python setup completed."
}

# --------------------------------------------------------------------
# 3. ミドルウェア起動 (Docker)
# --------------------------------------------------------------------
setup_docker_services() {
    log_info "Starting MongoDB & Redis..."

    # データディレクトリの準備
    mkdir -p /data/mongo
    chown -R 999:999 /data/mongo # MongoDB container user ID

    cd "$KVELL_HOME"

    # Dockerインストール確認 (UserDataで入れているはずだが念のため)
    if ! command -v docker &> /dev/null; then
        # 必要ならここでインストール
        log_error "Docker not found!"
        exit 1
    fi

    # コンテナ起動
    docker compose -f docker-compose.db.yml up -d

    log_info "Database services started."
}

# --------------------------------------------------------------------
# 4. Systemd サービス登録 (FastAPI)
# --------------------------------------------------------------------
setup_systemd() {
    log_info "Configuring systemd for FastAPI..."

    cat > /etc/systemd/system/kvell-api.service <<EOF
[Unit]
Description=Kvell API
After=network.target docker.service

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=$KVELL_HOME/apps/api
Environment="PATH=$KVELL_HOME/apps/api/.venv/bin:/usr/local/bin:/usr/bin"
Environment="PYTHONUNBUFFERED=1"
# 環境変数はここに追加するか、EnvironmentFile=/opt/kvell/.env を使う
ExecStart=$KVELL_HOME/apps/api/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable --now kvell-api
    log_info "Kvell API service started."
}

# --------------------------------------------------------------------
# メイン処理
# --------------------------------------------------------------------
main() {
    log_info "Starting Kvell Production Setup..."

    # System update (UserDataで済んでいればスキップ可)
    export DEBIAN_FRONTEND=noninteractive

    setup_volume
    setup_python
    setup_docker_services
    setup_systemd

    log_info "Setup Completed Successfully!"
}

main
