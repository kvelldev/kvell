---
name: Bug
about: Create a report to help us improve
title: "[Bug] - "
assignees: ""
---

## Overview

発生している不具合の事象を1〜2行で簡潔に記載する。

(記入例)
AndroidのChromeブラウザにおいて、WebSocket接続が切断された際に自動再接続が行われず、エラー画面のままフリーズする。

## Reproduction Steps

不具合を再現させるための手順を記載する。

1. [Go to] '...'
2. [Click on] '....'
3. [See error]

(記入例)
1. Android端末(Pixel 6a)でChromeを開き、トップページにアクセスする。
2. 投稿一覧が表示された状態で、機内モードをONにする（オフラインにする）。
3. 「接続が切れました」というトーストが表示される。
4. 機内モードをOFFにする（オンラインに戻す）。
5. **再接続されず、ローディングスピナーが回り続ける。**

## Expected Behavior vs Actual Behavior

本来あるべき挙動と、実際の挙動（バグ）のギャップを記載する。

- **Expected:** オンライン復帰を検知し、自動的にWebSocket再接続が行われ、投稿一覧が更新されること。
- **Actual:** 再接続処理が走らず（または失敗し）、スピナーが表示されたまま操作不能になる。

## Environment

不具合が発生した環境情報を記載する。

- OS: [e.g. iOS, Android, Windows]
- Browser: [e.g. Chrome, Safari]
- Version: [e.g. 22]
- Device: [e.g. iPhone 12, PC]

(記入例)
- OS: Android 14
- Browser: Chrome Mobile
- Device: Pixel 6a

## Background & Impact

不具合の深刻度や、修正しない場合のリスクを記載する。

(記入例)
ライブ会場などの電波が不安定な環境での利用が想定されるため、再接続不可はUXの致命的な欠陥となる。
ユーザーはブラウザをリロードしなければならず、離脱率の増加につながるため、優先度高（High）で対応が必要。

## Acceptance Criteria

修正完了の基準を記載する。

(記入例)
- [ ] ネットワーク切断後、復帰した際に自動で再接続されること。
- [ ] 再接続試行中は適切なUI（「再接続中...」等）が表示されていること。
- [ ] 3回リトライしてもダメな場合は、手動リロードを促すボタンが表示されること。

## Hints & Notes

ログ情報、スタックトレース、スクリーンショット、参考コード等を記載する。

(記入例)
- `reconnecting-websocket` ライブラリのオプション設定見直しが必要かもしれない。
- コンソールログ: `WebSocket connection to 'wss://...' failed: ...`

## Related Issues & Docs

- Issue: #
- Docs: [link](link_to_docs)
