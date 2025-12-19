Feature: 焚き火詳細ビューとレス機能 (Bonfire Detail & Response)
    As a 祭りを楽しみたいファン (B-Layer User)
    I want to 気になる焚き火の中に入り、会話の流れを読んだり、感想を投げ込んだりしたい
    So that メインTLのノイズから離れ、好きな話題で盛り上がることができる

    Background: System Configuration
        Given システムの "画像読み込み許可ドメインリスト" が用意されている
        And 焚き火:"bonbonfire-001"が存在している

    Rule: 遷移と表示
        Example: 焚き火詳細への遷移
            Given ユーザーはメインタイムラインを表示している
            When ユーザーが "bonfire-001" のカードをタップする
            Then 画面が "焚き火詳細ビュー" に遷移する
            And ヘッダー背景に "bonfire-001" の画像がHero Animationにて拡大表示される
            And "bonfire-001" に紐づくレス一覧が "古い順 (Oldest First)" で表示される
            And レスタイムラインは最も古いものの位置にスクロールされている
        # wsのRoom参加は裏側の挙動なのでGherkinには書かないが、実装時には必須

    Rule: ヘッダー画像の表示
        Background:
            Given ユーザーは"bonfire-001" の詳細ビューを表示している

        Example: 正常な画像のレンダリング（演出付き）
            Given "bonfire-001" に画像URLが含まれている
            And URLは"画像読み込み許可ドメインリスト"とマッチする
            And そのURLの画像ロードに "成功" した
            When ヘッダーが表示される
            Then 画像はヘッダー領域の中央に "アスペクト比を維持" して表示される
            And 背景には "メイン画像を加工した演出背景" が表示される
            And 文字要素の可読性のために "オーバーレイ" が表示される
            # Lightboxは共通仕様
            And ヘッダー画像をタップすると、Spark画像と同様の "Lightboxモーダル" が起動する

        Example: 画像なしの場合
            Given "bonfire-001" に画像URLが含まれていない、またはURLは"画像読み込み許可ドメインリスト"とマッチしない
            When ヘッダーが表示される
            Then ヘッダー背景には "デフォルトの焚き火画像" が表示される
            And ブラー処理やLightbox機能は無効化される


        Example: 画像読み込み失敗の場合
            # 世界観を壊さないため、エラーアイコンではなくデフォルト画像を使用する
            Given "bonfire-001" に画像URLが含まれている
            And URLは"画像読み込み許可ドメインリスト"とマッチする
            But そのURLの画像ロードに "失敗" した
            When ヘッダーが表示される
            Then ヘッダー背景には "デフォルトの焚き火画像" が表示される
            And ブラー処理やLightbox機能は無効化される

    Rule: ヘッダーURLの表示
        Example: URLのレンダリング
            Given "bonfire-001" にURLが含まれている
            When ヘッダーが表示される
            Then URLはsparkと同様の仕様で表示される

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

        Example: 固定型マーカー (LINE/Discord風)
            Given ユーザーが "bonfire-001" を開き、既読ラインが表示されている
            When ユーザーが下方向にスクロールして新しいレスを読む
            Then 既読ラインの表示位置は移動しない
        # 内部的にはスクロール位置を追跡しており、離脱時に保存される

        Example: ハイウォーターマーク方式
            Given ユーザーが"レス[10]"までスクロールした後、"レス[5]"まで戻った
            When ユーザーがページを離脱する
            Then 既読位置は"レス[10]"として保存される

        Example: 全既読時のマーカー非表示
            Given ユーザーが最新のレスまで全て読んだ状態で離脱した
            When ユーザーが再度 "bonfire-001" を開く
            Then "ここまで読んだ" ボーダーは表示されない

        Example: 新着レス到着時の既読維持
            Given ユーザーが"レス[8]"まで読んだ状態で "bonfire-001" を開いている
            And 既読ラインが"レス[8]"の下に表示されている
            When 他のユーザーが"レス[9]", "レス[10]"を投稿する
            Then 既読ラインの位置は"レス[8]"の下のまま変わらない
            And ユーザーが"レス[10]"までスクロールすると、次回訪問時の既読位置が更新される

    Rule: レスの投稿
        Background:
            Given ユーザーは "bonfire-001" の詳細ビューを表示している

        Example: 焚き火へのレス
            When ユーザーがFABをタップし、テキストを入力して投稿する
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
