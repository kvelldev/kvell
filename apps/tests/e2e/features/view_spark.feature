Feature: Timeline上のSparkフローと鎮火(Decay)演出
    As a 安心したい菊池さん（B層）
    I want to 自分の投稿が炎のように昇り、夜空に溶けていく様子を見たい
    So that 「言葉が燃料になって消え去った」という物理的な納得感を得て、ログが残らない安心感を感じたい

    Background: System Configuration (SSOT)
        # 画面・表示に関する設定値
        Given システムの "フェードアウト境界線" は "画面上部20%の位置" に設定されている
        And システムの "自動スクロール判定エリア" は "画面最下部から50px以内" に設定されている
        # ライフサイクルに関する設定値
        And システムの "種火の寿命(TTL)" は "10分" に設定されている

    Rule: SparkはTimelineを下から上へフローする
        Background:
            Given ユーザーは "Timeline" を閲覧している

        Example: 最新のSparkを受信した際の自動スクロール
            Given ユーザーのスクロール位置が "自動スクロール判定エリア" 内にある
            When 新しい "Spark" が投稿される
            Then "Timeline" は自動的にスクロールされ、最新の "Spark" が表示された状態を維持する

        Example: 過去のSpark閲覧時のスクロール位置固定
            Given ユーザーのスクロール位置が "自動スクロール判定エリア" の外（上部の古いSpark）にある
            When 新しい "Spark" が投稿される
            Then 新しい "Spark" はDOMの最下部に追加される
            But 画面のスクロール位置は変更されず、ユーザーが見ている古い "Spark" が表示され続ける

    Rule: 古いSparkは、時間と場所によって「鎮火(Decay)」して見える
        Background:
            Given 複数の "Spark" が存在し、"Timeline" が画面高さを超えている

        Example: フェードアウト境界での視覚的な消失
            Given ある "Spark" が "フェードアウト境界線" を跨ぐ位置にある
            When 画面を確認する
            Then その "Spark" の上部は、マスク処理により背景に溶け込んでいる

        Example: 古いSparkへの視覚的ノイズ付与
            Given ユーザーはスクロールして "フェードアウト境界線" より上にある古い "Spark" を表示した
            When その "Spark" の残り寿命が "種火の寿命(TTL)" に近づいている
            Then その "Spark" は「半透明（Opacity低下）」または「ぼかし（Blur）」が適用され、「鎮火(Decay)」しつつあることが示される

    Rule: 寿命尽きたSparkはTimelineから消滅する
        Example: TTL超過によるDOM削除
            Given "種火の寿命(TTL)" 前に投稿された "Spark A" が表示されている
            When "Spark A" の経過時間が "種火の寿命(TTL)" を超える
            Then "Spark A" は "Timeline"（DOM）から完全に削除される
            And ユーザーの画面上から "Spark A" が消滅する
