Feature: 焚き火詳細ビューとレス機能 (Bonfire Detail & Response)
    As a 祭りを楽しみたいファン (B-Layer User)
    I want to 気になる焚き火の中に入り、会話の流れを読んだり、感想を投げ込んだりしたい
    So that メインTLのノイズから離れ、好きな話題で盛り上がることができる

    Background: System Configuration
        Given システムの "文字数制限" は "500文字" に設定されている
        And 焚き火:"bonbonfire-001"が存在している

    Rule: 遷移と表示 (Navigation & Display)
        Example: 焚き火詳細への遷移
            Given ユーザーはメインタイムラインを表示している
            When ユーザーが "bonfire-001" のカードをタップする
            Then 画面が "焚き火詳細ビュー" に遷移する
            And ヘッダー背景に "bonfire-001" の画像がHero Animationにて拡大表示される
            And "bonfire-001" に紐づくレス一覧が "古い順 (Oldest First)" で表示される
        # wsのRoom参加は裏側の挙動なのでGherkinには書かないが、実装時には必須

    Rule: シェア機能 (Sharing)
        Example: 外部SNSへの拡散
            When ユーザーが "シェアボタン" をタップする
            Then "X (Twitter)" や "LINE" を含む共有メニューが表示される
            And 共有リンクには "現在の焚き火ページのURL" がセットされている

    Rule: 既読管理 (Read State via LocalStorage)
        Background:
            Given ユーザーは以前に "bonfire-001" を閲覧し、途中のレスまでスクロールしていた

        Example: 既読ラインの復元
            When ユーザーがブラウザを再起動し、再度 "bonfire-001" を開く
            Then 前回最後に表示されたレスの下に "ここまで読んだ" というボーダーが表示される
            And タイムラインは自動的にそのボーダー位置までスクロールされる

    Rule: レスの投稿
        Background:
            Given ユーザーは "bonfire-001" の詳細ビューを表示している

        Example: 焚き火へのレス
            When ユーザーがFABをタップし、"文字数制限" 以内のテキストを入力して投稿する
            Then 入力画面が閉じられる
            And 詳細ビューの最下部に自分の投稿が追加される
            And 追加された投稿には "薪くべボタン" は表示されない

    Rule: 鎮火時の挙動
        Background:
            Given ユーザーは "bonfire-001" の詳細ビューを表示している

        Example: 鎮火した場合
            When "bonfire-001" がDecayした
            Then 投稿用FAB・シェアボタンが非表示、または無効化される
            But 過去のレスや、他のユーザーが滑り込みで投稿したレスは画面遷移しない限り引き続き閲覧できる

    Rule: スクロール制御 (Smart Auto-Scroll)
        Example: 追尾モード (Live)
            Given ユーザーがタイムラインの最下部付近にいる
            When 他のユーザーが新しいレスを投稿する
            Then 画面が自動的に新しいレスまでスクロールする

        Example: 閲覧モード (Reading)
            Given ユーザーが過去ログを読むために上にスクロールしている
            When 他のユーザーが新しいレスを投稿する
            Then 画面はスクロールせず、現在の位置を維持する
            And "新着あり" を通知するインジケーターが表示される
