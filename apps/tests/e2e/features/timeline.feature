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
