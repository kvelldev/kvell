# Kvell Infrastructure

本番環境のCloudFormationテンプレート。

## アーキテクチャ

```
User → CloudFront → S3 (SPA)
                 → EC2 (Docker: API + MongoDB + Redis)
```

## ファイル構成

```
infra/
├── README.md          # このファイル
├── network.yml        # VPC, Subnet, IGW
├── instance.yml       # EC2, Security Group, IAM, Data EBS
├── cdn.yml            # S3, CloudFront
└── scripts/
    ├── setup-prod.sh  # EC2起動時に実行
    └── backup.sh      # Cronで毎時実行
```

## デプロイ順序

### 0. 変数設定

```bash
# 最初に1回だけ実行
export AWS_PROFILE=kvell
export AWS_REGION=ap-northeast-1
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export ECR_REPO="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/kvell-api"

```

### 1. 事前準備

```bash
# ACM証明書の作成 (us-east-1, AWSコンソールで)

# ECRリポジトリの作成
aws ecr create-repository --repository-name kvell-api --region $AWS_REGION

# GitHubトークンをSSM Parameter Storeに保存
# (GitHub Settings → Developer settings → Fine-grained tokens)
# Repository: kvell のみ, Permissions: Contents (read-only)
aws ssm put-parameter \
  --name /kvell/github-token \
  --value "github_pat_xxxxxxxxxxxx" \
  --type SecureString \
  --region $AWS_REGION

# APIイメージをビルド・プッシュ
cd apps/api
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO
docker build -t kvell-api .
docker tag kvell-api:latest $ECR_REPO:latest
docker push $ECR_REPO:latest
```

### 2. ネットワーク

```bash
aws cloudformation deploy \
  --template-file network.yml \
  --stack-name kvell-network \
  --region $AWS_REGION
```

### 3. S3/CloudFront

```shell
export ACM_CERT_ARN=ARN
export DOMAIN_NAME=domain
# Basic認証: user:password をbase64エンコード
export BASIC_AUTH=$(echo -n 'user:password' | base64)
```
してから実行

```bash
aws cloudformation deploy \
  --template-file cdn.yml \
  --stack-name kvell-cdn \
  --parameter-overrides \
    DomainName=$DOMAIN_NAME \
    AcmCertificateArn=$ACM_CERT_ARN \
    ApiOriginDomain=dummy.local \
    BasicAuthCredentials=$BASIC_AUTH \
  --capabilities CAPABILITY_IAM \
  --region $AWS_REGION
```

### 4. EC2インスタンス

```bash
aws cloudformation deploy \
  --template-file instance.yml \
  --stack-name kvell-instance \
  --parameter-overrides \
    GitHubRepo=kvelldev/kvell \
    EcrRepository=$ECR_REPO \
    CorsOrigins=$DOMAIN_NAME \
    BackupS3Bucket=kvell-prod-backups \
  --capabilities CAPABILITY_NAMED_IAM \
  --region $AWS_REGION
```

### 5. CloudFront Origin更新

EC2のPublic DNSを取得してcdn.ymlを再デプロイ（IPアドレスはCloudFrontで使用不可）：

```bash
# EC2のPublic DNSを取得
INSTANCE_ID=$(aws cloudformation describe-stacks \
  --stack-name kvell-instance \
  --query 'Stacks[0].Outputs[?OutputKey==`InstanceId`].OutputValue' \
  --output text)

PUBLIC_DNS=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].PublicDnsName' \
  --output text)

echo "Public DNS: $PUBLIC_DNS"

# cdn.ymlを再デプロイ
aws cloudformation deploy \
  --template-file cdn.yml \
  --stack-name kvell-cdn \
  --parameter-overrides \
    DomainName=$DOMAIN_NAME \
    AcmCertificateArn=$ACM_CERT_ARN \
    ApiOriginDomain=$PUBLIC_DNS \
    BasicAuthCredentials=$BASIC_AUTH \
  --capabilities CAPABILITY_IAM \
  --region $AWS_REGION
```

### 6. SPA デプロイ

```bash
# CloudFront Distribution IDを取得
DISTRIBUTION_ID=$(aws cloudformation describe-stacks \
  --stack-name kvell-cdn \
  --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionId`].OutputValue' \
  --output text)

cd apps/web && npm run build
aws s3 sync dist/ s3://kvell-prod-spa/ --delete
aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths "/*"
```

## 運用

### 新バージョンデプロイ

```bash
# イメージをビルド・プッシュ
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO
docker build -t kvell-api apps/api
docker tag kvell-api:latest $ECR_REPO:v1.2.3
docker push $ECR_REPO:v1.2.3

# EC2でイメージ更新
aws ssm start-session --target i-xxxx
cd /opt/kvell
git pull
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

### バックアップ復旧

```bash
aws s3 cp s3://kvell-prod-backups/bonfires-YYYYMMDD-HHMM.bson /tmp/
docker cp /tmp/bonfires.bson kvell-mongo-1:/tmp/
docker exec kvell-mongo-1 mongorestore \
  --uri="mongodb://localhost:27017/kvell" \
  --collection=bonfires /tmp/bonfires.bson
```
