Feature: Timeline
    As a 安心したい菊池さん
    I want to 自分の言葉がリアルタイムに流れ、やがて冷めて煙となり、空に溶けていく様子を見たい
    So that 「ライブ感」と「ログが残らない安心感」の両方を感じたい

    Background: System Configuration
        Given システムの "Decay time" は "1分" に設定されている
        And システムの "冷却閾値" は "Decay time" に対して "30%" の割合である
        And システムの "中火(Kindling)昇格UU" は "3名" に設定されている
        And システムの "中火(Kindling)延長時間" は "3時間" に設定されている
        # Note: 焚き火昇格UUは過去のDAUに基づいて動的に計算される。ここでは振る舞いのテストができればよいので、固定値を用いる。
        And システムの "焚き火(Bonfire)昇格UU" は "10名" に設定されている
        And システムの "焚き火(Bonfire)初期寿命" は "24時間" に設定されている
        And システムの "焚き火(Bonfire)昇格スコア" は "0pt" に設定されている
        And システムの "薪(Button)係数" は "1pt" に設定されている


    # 表示
    Rule: Timelineは「常に最新」を表示することをデフォルトとする
        Background:
            Given ユーザーは"メイン画面"を開いている
            And 複数の "Spark" が存在し、"Timeline" が画面高さを超えている

        Example: 初期表示時の挙動 (Default Sticky)
            Then "Timeline" は最初から「最下部」にスクロールされた状態で表示される
            And ユーザーが操作しなくても、新しい "Spark" が来れば自動で表示される

        Example: ユーザーが過去ログを見ている場合 (Scroll Up)
            When ユーザーが意図的に上へスクロールする
            Then 自動スクロールは解除され、その場に留まる（新しいSparkが来ても勝手に動かない）

    Rule: Sparkは熱量を持ち、時間とともに冷めて消える
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

        # Decay & kindling
    Rule: Sparkは放置するとDecayする
        Example: 寿命超過によるDecay
            Given "Timeline" 上に "Spark A" が表示されている
            When "Spark A" の経過時間が "Decay time" を超える
            Then "Spark A" はリストから削除され、Timelineが詰まる

    Rule: 複数のユーザーが反応すると寿命が延びる (Kindling)
        Example: 3人のユーザーが反応して中火になる
            Given 投稿直後の種火が存在する
            When "中火(Kindling)昇格UU" と同数のユニークユーザーが、それぞれ薪(ボタン)をくべた
            Then その種火の有効期限(decayAt)は "最終アクション時刻 + 中火(Kindling)延長時間" に延長される
            And その種火は強いGlowを持つ
            And その種火の表示エリアは "種火エリア(Timeline)" のままである

    Rule: 多くのユーザーが反応すると焚き火に昇格する (Bonfire)
        Example: 多くの人が反応して焚き火になる
            Given 種火が存在する
            When "焚き火(Bonfire)昇格UU" と同数のユニークユーザーが、それぞれ "薪" をくべた
            And その種火の熱量スコアは "焚き火(Bonfire)昇格スコア" 以上になった
            Then その種火は "焚き火(Bonfire)" に昇格する
            And その種火の有効期限(decayAt)は "現在時刻 + 焚き火(Bonfire)初期寿命" に設定される
            And その種火は"種火エリア(Timeline)"から削除される


        # EdgeCase
    Rule: Sparkが一つもない場合は「静寂」を表現する
        Background:
            Given "Timeline" に表示できる有効な "Spark" が0件である

        Example: Empty Stateの表示 (The Silent Sky)
            Then 画面中央にアイコン等は表示せず、テキストのみを表示する
            And テキストの内容は「静かな夜空です。」とする

