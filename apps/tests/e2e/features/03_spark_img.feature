Feature: 画像の表示
    ユーザーが投稿した画像URL（パラメータ付き含む）を適切に検出し、
    表示不能な場合でもUIの整合性を保つための「読み込み失敗画像」を表示する。

    Background: システム設定
        Given システムの "許可ドメインリスト" は "Official, Twitter(Img), Insta(CDN)" を含む
        And システムには "読み込み失敗時の代替画像 (placeholder_error.png)" がアセットとして用意されている
        And 画像表示の "最大高さ" は "300px" (object-fit: contain) である

    # サムネ
    Rule: 柔軟な画像URL検出 (Smart Regex)
        単純な拡張子判定だけでなく、クエリパラメータやCDN特有の形式を含むURLも画像として認識する。

        Example: クエリパラメータ付きの画像URL (Twitter等)
            Given ユーザーは "https://pbs.twimg.com/media/E4jX...?format=jpg&name=large" という種火を入力した
            When その種火が表示される
            Then URLは画像として認識され、サムネイルが展開される
            And URLテキスト自体も表示される
            And imgタグのsrcは入力されたURLそのものである
        # NOTE: "referrerPolicy='no-referrer'"を使用する

        Example: 標準的な拡張子の画像URL
            Given ユーザーは "http://sakurazaka46.com/blog/photo.JPG" という種火を入力した
            When その種火が表示される
            Then URLは画像として認識され、サムネイルが展開される
            And URLテキスト自体も表示される
        # 大文字小文字 (JPG/jpg) は区別しない

    Rule: エラー時の代替画像表示 (Visual Fallback)
        画像のリンク切れやアクセス拒否 (403/404) が発生した場合、テキストリンクに戻すのではなく、
        視覚的にわかりやすい「失敗画像」を表示する。ただし、元URLへの導線は維持する。

        Example: 画像ロードエラー発生時
            Given タイムラインに "https://broken-link.com/image.png" のサムネイル枠が表示された
            When ブラウザが画像の読み込みに失敗する (onErrorイベント発生)
            Then 表示されている画像が "読み込み失敗時の代替画像" に差し替わる
            And URLテキスト自体も表示される

    Rule: ライトボックスと表示崩れ防止
        成功・失敗に関わらず、レイアウト（高さ制限）と拡大機能は維持される。

        Example: 代替画像の表示レイアウト
            Given 画像の読み込みに失敗し、代替画像が表示されている
            Then 代替画像も "最大高さ (300px)" の制約を守って表示される
            And トリミングは行われず、object-fit: contain で表示される
        # IMPORTANT: 同一性保持権を侵害しないため、画像のトリミングは行わない


        # 拡大
    Rule: 正常画像のアプリ内拡大 (Lightbox)
        正常にロードされた画像は、タップすることでアプリ内モーダルとして最大化表示される。
        この際、外部サイトへの遷移は発生しない。

        Example: タイムライン上の画像をタップして拡大する
            Given タイムラインに "https://pbs.twimg.com/media/example.jpg" のサムネイルが表示されている
            And 画像のロードは "成功" している
            When ユーザーがそのサムネイルをタップする
            Then "Lightboxモーダル" が起動し、画像が画面中央に表示される
            And 背景のタイムラインは "暗いオーバーレイ" で覆われ、スクロール不可となる
            And 画像はトリミングされず、アスペクト比を維持して画面内に最大化される
            And モーダル内には "元画像へのリンクアイコン"が表示される

        Example: Lightboxを閉じる
            Given Lightboxモーダルが開いている
            When ユーザーが "画像以外の背景エリア（オーバーレイ）" をタップする
            Then Lightboxモーダルが閉じ、元のタイムライン画面に戻る
            And スクロール位置は画像を開く前と同じ位置に維持されている
