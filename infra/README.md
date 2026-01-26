# Kvell Infrastructure

本番環境のCloudFormationテンプレートおよび運用手順。

## アーキテクチャ

```
User → CloudFront → S3 (SPA)
                 → EC2 (Docker: API + MongoDB + Redis)
```

**特徴:**
- APIサーバーはEC2上で直接Docker Composeを実行（ECR不使用）。
- セットアップスクリプト (`setup-prod.sh`) はS3からダウンロードして実行。
- GitHub PAT等の機密情報は SSM Parameter Store で管理。
- Elastic IP (EIP) を使用し、インスタンス再作成時もIPを固定（CDN設定変更不要）。
- データベースのバックアップは日次でS3へ保存。

## ファイル構成

```
infra/
├── README.md          # このファイル
├── network.yml        # VPC, Subnet, IGW
├── instance.yml       # EC2, Security Group, IAM, Data EBS
├── cdn.yml            # S3, CloudFront
└── scripts/
    ├── setup-prod.sh  # EC2初期構築 & アプリデプロイ
    └── backup.sh      # MongoDBバックアップ (S3連携)
```

## デプロイ手順

### 0. 変数設定 (初回のみ)

```bash
export AWS_PROFILE=kvell
export AWS_REGION=ap-northeast-1
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
```

### 1. Storage Stack デプロイ
S3バケット (Setup Scripts, Backups, CloudFront Logs) を作成します。

```bash
# バケット名はパラメータで上書き可能ですが、デフォルトは kvell-prod-{scripts,backups,logs} となります。
# 既に同名のバケットが他にある場合は作成に失敗するので注意してください。

aws cloudformation deploy \
  --template-file storage.yml \
  --stack-name kvell-storage \
  --region $AWS_REGION

# 作成されたバケット名・ドメインを変数に格納 (後続のステップで使用)
export SCRIPTS_BUCKET=$(aws cloudformation describe-stacks --stack-name kvell-storage --query "Stacks[0].Outputs[?OutputKey=='ScriptsBucketName'].OutputValue" --output text)
export BACKUP_BUCKET=$(aws cloudformation describe-stacks --stack-name kvell-storage --query "Stacks[0].Outputs[?OutputKey=='BackupBucketName'].OutputValue" --output text)
export LOGS_BUCKET_DOMAIN=$(aws cloudformation describe-stacks --stack-name kvell-storage --query "Stacks[0].Outputs[?OutputKey=='LogsBucketDomainName'].OutputValue" --output text)
```

### 2. SSMパラメータ設定 & スクリプトアップロード

GitHubのReadOnlyトークン (Contents: Read) を取得し、SSMに保存します。

```bash
aws ssm put-parameter \
  --name /kvell/prod/github_pat \
  --value "github_pat_xxxxxxxxxxxx" \
  --type SecureString \
  --region $AWS_REGION
```

インスタンス構築時に実行されるスクリプトをS3バケットに配置します。

```bash
aws s3 cp infra/scripts/setup-prod.sh s3://$SCRIPTS_BUCKET/setup-prod.sh
aws s3 cp infra/scripts/backup.sh s3://$SCRIPTS_BUCKET/backup.sh
```

### 2.5 Network Stack デプロイ
```bash
aws cloudformation deploy \
  --template-file network.yml \
  --stack-name kvell-network \
  --region $AWS_REGION
```

### 3. Instance Stack デプロイ

```bash
aws cloudformation deploy \
  --template-file instance.yml \
  --stack-name kvell-instance \
  --parameter-overrides \
    ScriptsBucketName=$SCRIPTS_BUCKET \
    BackupS3Bucket=$BACKUP_BUCKET \
    CorsOrigins=https://kvellapp.com \
    KeyPairName=kvellkey \
    NotificationEmail="your-email@example.com" \
  --capabilities CAPABILITY_NAMED_IAM \
  --region $AWS_REGION
```

> [!IMPORTANT]
> `NotificationEmail` に指定したメールアドレスにAWSSNSから確認メールが届きます。**リンクを必ずクリックして承認**してください。

### 4. CDN Stack デプロイ

Instance StackのOutputにあるIPアドレス (またはEIP) を `ApiOriginDomain` に指定します。

```bash
# ドメイン名の設定
export DOMAIN_NAME="kvellapp.com"

# ACM証明書ARNの取得 (us-east-1から取得する必要あり)
export ACM_CERT_ARN=$(aws acm list-certificates --region us-east-1 --query "CertificateSummaryList[?DomainName=='$DOMAIN_NAME'].CertificateArn" --output text)

API_ORIGIN_DOMAIN=$(aws cloudformation describe-stacks --stack-name kvell-instance --query "Stacks[0].Outputs[?OutputKey=='PublicDnsName'].OutputValue" --output text)
```

```bash
aws cloudformation deploy \
  --template-file cdn.yml \
  --stack-name kvell-cdn \
  --parameter-overrides \
    ApiOriginDomain=$API_ORIGIN_DOMAIN \
    LogsBucketDomainName=$LOGS_BUCKET_DOMAIN \
    DomainName=$DOMAIN_NAME \
    AcmCertificateArn=$ACM_CERT_ARN \
  --capabilities CAPABILITY_IAM \
  --region $AWS_REGION
```

> [!NOTE]
> Route 53のレコード作成（エイリアス設定）はCloudFormationには含まれていません。
> CloudFrontのデプロイ完了後、マネジメントコンソールの「関数の関連付け」設定や「代替ドメイン名」設定画面から「Route 53 レコードを作成」ボタン等を使用して自動設定を行ってください。

> [!IMPORTANT]
> `AcmCertificateArn` は必ず **us-east-1 (バージニア北部)** リージョンで作成された証明書のARNを指定してください（CloudFrontの制約）。

### 5. SPA デプロイ

Webアプリケーション (React) をビルドし、S3バケットに同期します。

```bash
# 変数設定 (CDN StackのOutputから取得)
export SPA_BUCKET=$(aws cloudformation describe-stacks --stack-name kvell-cdn --query "Stacks[0].Outputs[?OutputKey=='SpaBucketName'].OutputValue" --output text)
export CLOUDFRONT_ID=$(aws cloudformation describe-stacks --stack-name kvell-cdn --query "Stacks[0].Outputs[?OutputKey=='CloudFrontDistributionId'].OutputValue" --output text)

# ビルド
cd apps/web
npm ci
npm run build

# S3へ同期 (distフォルダの内容をアップロード)
aws s3 sync dist s3://$SPA_BUCKET --delete

# キャッシュ削除 (古いコンテンツが残らないように)
aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_ID --paths "/*"

cd ../..
```


## 運用

### アプリケーション更新

ECRを使用せず、EC2上で直接 `git pull` してビルドします。

1. **SSM Session Manager** でインスタンスに接続。
2. 以下のコマンドを実行:

```bash
# SSH接続後
cd /home/ubuntu/ws/kvell

# コード更新
git pull

# 依存関係更新 (もしあれば)
cd apps/api
../../.local/bin/uv sync  # または pip install -r requirements.txt

# DB更新 (もしdocker-compose.ymlが変わっていたら)
cd ../..
docker compose up -d mongo redis

# API再起動
sudo systemctl restart kvell-api
```

### ログ確認

- **初期セットアップログ**: `/var/log/user-data-bootstrap.log`
- **アプリケーションログ**: `docker compose logs -f`

### バックアップ復旧

`backup.sh` により日次でS3 (`kvell-prod-backups`) にMongoDBダンプが保存されています。

```bash
# S3から取得
aws s3 cp s3://kvell-prod-backups/bonfires-YYYYMMDD-HHMM.bson /tmp/

# MongoDBへリストア
docker cp /tmp/bonfires.bson kvell-mongo-1:/tmp/
docker exec kvell-mongo-1 mongorestore \
  --uri="mongodb://localhost:27017/kvell" \
  --collection=bonfires /tmp/bonfires.bson
```
