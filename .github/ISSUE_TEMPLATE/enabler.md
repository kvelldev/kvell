---
name: Enabler
about: Template for preparation for development
title: "[Enabler] - "
assignees: ""
---

## Overview

本タスクで実現したい技術的な目的を1~2文で簡潔に説明する。

(記入例)
SSH接続の手間をなくし、かつデプロイミスを防ぐため、GitHub ActionsによるEC2への自動デプロイパイプラインを構築する。

## Technical User Story

本タスクを実施するモチベーションを下記の形式で記載する。

- **As a** <developer or system>
- **I want to** <達成したいゴール>
- **so that** <技術的な理由・メリット>できるようになるためだ。

(記入例)
- **As a** developer (管理人)
- **I want to** mainブランチにマージされたら自動でEC2上のアプリが更新されるようにしたい
- **so that** 手動でのSSH作業によるコマンドミス（事故）をなくし、開発に集中できる時間を増やすためだ。

## Background & Context

本タスクが起票された背景を記載する。現状認識、本タスクを実施しない場合のリスク・機会損失等を記載する。

(記入例)
現在はローカルから `git pull` するために毎回SSMでサーバーに入っているが、手順が煩雑であり、環境変数の設定漏れなどが起きやすい。
また、今後ユーザーが増えた際にダウンタイムを最小限にするためにも、Blue/Greenデプロイ等の布石として自動化が必要である。

## Acceptance Criteria

このタスクの完了基準を記載する。「何をするか」ではなく、「何ができるようになったか」にフォーカスする。

(記入例)
- [ ] `.github/workflows/deploy.yml` が作成されている。
- [ ] mainブランチへのPRマージをトリガーにActionsが起動し、成功すること。
- [ ] EC2上のFastAPIおよびReactのビルドファイルが最新に置き換わり、サービスが再起動していること。
- [ ] デプロイ完了がSlack（またはDiscord）に通知されること。

## Hints & Notes

実装上のヒント、コード例、気をつけるべきポイント等を記載する。

(記入例)
- AWSへの認証はAccess Keyではなく、OIDC (OpenID Connect) を使用すること。
- デプロイ中はNginxでメンテナンス画面を出すかどうか検討が必要（今回は瞬断許容でOK）。

## Related Issues & Docs

- Issue: #
- Docs: [link](link_to_docs)
