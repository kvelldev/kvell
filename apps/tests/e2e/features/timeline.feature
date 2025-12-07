Feature: Timeline
    As a 安心したい菊池さん（B層）
    I want to 自分の言葉がリアルタイムに流れ、やがて冷めて煙となり、空に溶けていく様子を見たい
    So that 「ライブ感」と「ログが残らない安心感」の両方を感じたい

    Background: System Configuration
        Given システムの "種火の寿命" は "10分" に設定されている
        And システムの "冷却閾値（Hot/Ashの境界）" は "残り寿命3分" に設定されている

    Rule: Timelineは「常に最新」を表示することをデフォルトとする
        Background:
            Given 複数の "Spark" が存在し、"Timeline" が画面高さを超えている

        Example: 初期表示時の挙動 (Default Sticky)
            When ユーザーがページを開く（またはリロードする）
            Then "Timeline" は最初から「最下部」にスクロールされた状態で表示される
            And ユーザーが操作しなくても、新しい "Spark" が来れば自動で表示される

        Example: ユーザーが過去ログを見ている場合 (Scroll Up)
            When ユーザーが意図的に上へスクロールする
            Then 自動スクロールは解除され、その場に留まる（新しいSparkが来ても勝手に動かない）

    Rule: Sparkは「熱量」と「残り時間」を可視化する
        Background:
            Given ユーザーは "Timeline" を閲覧している

        Example: 発生直後のSpark（高温状態）
            When 新しい "Spark" が投稿される（残り寿命 100%〜30%）
            Then その "Spark" は「白文字（Smoke White）」で表示される
            And その "Spark" は「オレンジ色の枠線（Ember Border）」と「発光（Glow）」を持つ
            And その "Spark" には「残り時間（例: 09:59）」がカウントダウン表示される

        Example: 冷却されたSpark（灰化状態）
            Given 投稿から時間が経過している "Spark" がある
            When その "Spark" の残り寿命が "冷却閾値（3分）" を下回る
            Then その "Spark" は「灰色文字（Ash Gray）」へと変化する
            And その "Spark" の「枠線」と「発光」は消失する（border-0 / shadow-none）
            And 「残り時間」の表示も灰色になり、カウントダウンは継続する

    Rule: 寿命尽きたSparkは「煙」となって昇華する
        Example: 寿命超過による昇華 (Smoke Animation)
            Given "Timeline" 上に "Spark A" が表示されている
            When "Spark A" の経過時間が "種火の寿命" を超える（残り時間 00:00）
            Then "Spark A" は即座に消えるのではなく、「煙のアニメーション」を開始する
            And "Spark A" は「上空へ拡散」し、「ぼやけ」ながら透明になっていく
            And アニメーション終了後、"Spark A" はリストから削除され、Timelineが詰まる

    Rule: Sparkが一つもない場合は「静寂」を表現する
        Background:
            Given "Timeline" に表示できる有効な "Spark" が0件である

        Example: Empty Stateの表示 (The Silent Sky)
            Then 画面中央にアイコン等は表示せず、テキストのみを表示する
            And テキストの内容は「静かな夜空です。」とする
