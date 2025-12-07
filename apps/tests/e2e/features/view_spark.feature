Feature: Timeline上のSparkフローと色温度による熱量表現
    As a 安心したい菊池さん（B層）
    I want to 自分の言葉が「熱」を持って生まれ、やがて「灰」になって冷め、闇に溶けていく様子を見たい
    So that 「燃焼」という物理的な納得感を得つつ、ログが残らない安心感を感じたい

    Background: System Configuration (SSOT)
        # 画面・表示に関する設定値
        Given システムの "フェードアウト境界" は "画面上部20%の位置" に設定されている
        And システムの "自動スクロール判定エリア" は "画面最下部から50px以内" に設定されている
        # ライフサイクルに関する設定値
        And システムの "種火の寿命" は "10分" に設定されている

    Rule: Sparkは「熱」を持って生まれ、時間経過で「灰」になる
        Background:
            Given ユーザーは "Timeline" を閲覧している

        Example: 発生直後のSpark（高温状態）
            When 新しい "Spark" が投稿される（残り寿命 100%〜30%）
            Then その "Spark" の文字色は「白（Smoke White）」で表示される
            And その "Spark" は「オレンジ色の光（Ember Glow）」を帯びている

        Example: 消滅寸前のSpark（灰化状態）
            Given 投稿から時間が経過している "Spark" がある
            When その "Spark" の残り寿命が "30%未満" になる
            Then その "Spark" の文字色は徐々に「灰色（Ash Gray）」へと変化する
            And "Spark" の「オレンジ色の光」は消失する

    Rule: SparkはTimelineを下から上へフローし、上空へ消える
        Background:
            Given 複数の "Spark" が存在し、"Timeline" が画面高さを超えている

        Example: 最新Spark受信時の自動スクロール
            Given ユーザーのスクロール位置が "自動スクロール判定エリア" 内にある
            When 新しい "Spark" が投稿される
            Then "Timeline" は自動的にスクロールされ、最新の "Spark" が表示された状態を維持する

        Example: フェードアウト境界での視覚的な消失
            Given ある "Spark" が画面上部へスクロールアウトしていく
            When その "Spark" が "フェードアウト境界" に入る
            Then その "Spark" は不透明度を維持したまま、マスク処理によって背景に溶け込むように見えなくなる

    Rule: 寿命尽きたSparkは物理的に崩れ落ちる
        Example: 寿命超過による完全消滅
            Given "Timeline" 上（または一覧）に "Spark A" が表示されている
            When "Spark A" の経過時間が "種火の寿命" を超える
            Then "Spark A" は画面上から跡形もなく消滅する

    Rule: ユーザーは見えなくなったSparkを一覧で探せる
        Example: もっと見るボタンによる一覧表示
            Given "Timeline" には表示しきれない（または流れていった）生存中の "Spark" が存在する
            When ユーザーが "もっと見る" ボタンを押下する
            Then 現在生存している全ての "Spark" が一覧表示される
            And ここでも "Spark" は残り寿命に応じた「白〜灰」の色変化で表示される
