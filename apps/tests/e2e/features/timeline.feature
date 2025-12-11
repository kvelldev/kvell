Feature: Timeline
    As a 安心したい菊池さん（B層）
    I want to 自分の言葉がリアルタイムに流れ、やがて冷めて煙となり、空に溶けていく様子を見たい
    So that 「ライブ感」と「ログが残らない安心感」の両方を感じたい

    Background: System Configuration
        Given システムの "Decay time" は "1分" に設定されている
        Given システムの "冷却閾値" は "Decay time" に対して "30%" の割合である

    Rule: Timelineは「常に最新」を表示することをデフォルトとする
        Background:
            Given 複数の "Spark" が存在し、"Timeline" が画面高さを超えている

        Example: 初期表示時の挙動 (Default Sticky)
            When ユーザーがページを開く（またはリロードする）
            Then "Timeline" は最初から「最下部」にスクロールされた状態で表示される
            And ユーザーが操作しなくても、新しい "Spark" が来れば自動で表示される

        Example: ユーザーが過去ログを見ている場合 (Scroll Up)
            When ユーザーがページを開く
            And ユーザーが意図的に上へスクロールする
            Then 自動スクロールは解除され、その場に留まる（新しいSparkが来ても勝手に動かない）

    Rule: Sparkは「熱量」と「残り時間」を可視化する
        Background:
            Given ユーザーは "Timeline" を閲覧している

        Example: 発生直後のSpark（高温状態）
            When 新しい "Spark" が投稿される（残り寿命 100%〜30%）
            Then その "Spark" はGlowを持つ
            And その "Spark" には「残り時間（例: 09:59）」がカウントダウン表示される

        Example: 冷却されたSpark
            Given 投稿から時間が経過している "Spark" がある
            When その "Spark" の残り寿命が "冷却閾値" を下回る
            Then その "Spark" のGlowは消失する


    Rule: 寿命尽きたSparkはDecayする
        Example: 寿命超過によるDecay
            Given "Timeline" 上に "Spark A" が表示されている
            When "Spark A" の経過時間が "Decay time" を超える
            Then "Spark A" はリストから削除され、Timelineが詰まる

    Rule: Sparkが一つもない場合は「静寂」を表現する
        Background:
            Given "Timeline" に表示できる有効な "Spark" が0件である

        Example: Empty Stateの表示 (The Silent Sky)
            Then 画面中央にアイコン等は表示せず、テキストのみを表示する
            And テキストの内容は「静かな夜空です。」とする

    TODO: モーダル対応に伴う仕様のマージ

    Feature: Post a Spark

        As a サイレントマジョリティ（ファン）
        I want to 自分の感情を「種火」として投稿したい
        So that 誰かの目を気にせず、微熱を吐き出してスッキリできる

        Background: System Configuration
            # 開発設定: ここを変更すると全シナリオの閾値が変わります
            Given システムの "文字数制限" は "500文字" に設定されている
            And システムの "投稿レートリミット" は "1分間に10回" に設定されている
            And システムの "公開期間(表示寿命)" は "10分" に設定されている
            And システムの "法的保存期間(TTL)" は "30日" に設定されている
            And NGワードリストには "forbidden_word" が登録されている

    Rule: 妥当な内容の投稿
        受け入れ可能なテキストであれば、投稿は保存され、適切な公開期間と法的保存期間が設定される。

        Example: 正常な種火の投稿
            Given ユーザーは "文字数制限" 以内の有効なテキストを入力した
            When "種火を投げる"を実行する
            Then 投稿完了のフィードバックが表示される
            And 入力フォームがクリアされる
            And 投稿データはDBに保存される
            And 保存されたデータの "表示期限" は現在時刻から "公開期間" 後に設定されている
            And 保存されたデータの "物理削除予定日" は現在時刻から "法的保存期間" 後に設定されている

    Rule: 入力値の検証
        空文字、文字数超過、NGワードを含む投稿は拒否されなければならない。

        Example: 文字数超過の投稿
            Given ユーザーは "文字数制限 + 1文字" のテキストを入力した
            Then 文字数カウントが超過を示す警告色で表示される
            And "種火を投げる" ボタンが無効化されている

        Example: NGワードを含む投稿
            Given ユーザーは "forbidden_word" を含むテキストを入力した
            When "種火を投げる"を実行する
            Then "不適切な表現が含まれています" というエラーが表示される
            And 投稿データはDBに保存されない

        Example: 空文字または空白のみの投稿
            Given ユーザーは "空白文字のみ" を入力した
            When "種火を投げる"を実行する
            Then エラーが表示される、またはボタンが押せない状態である

    Rule: 連投制限
        荒らし対策のため、短時間の連続投稿を制限する。

        Example: 制限を超えた連投
            Given このユーザーは直前の期間内に "投稿レートリミット" 回数の投稿を完了している
            When ユーザーがさらに "投稿レートリミット + 1回目" の投稿を実行する
            Then "投稿ペースが速すぎます" という旨のエラーが表示される
            And 投稿データはDBに保存されない

    Rule: 匿名IDのローテーション
        ユーザーの識別子は固定されず、特定に結びつかないよう定期的に変更される。

        Example: 日次でのIDハッシュ変更
            Given ユーザーAの現在の "IPアドレスハッシュ" がある値である
            When システムの日次ローテーション時刻（例: 24:00）を過ぎる
            Then ユーザーAが次に投稿する際、保存される識別子は以前とは異なる値になる
