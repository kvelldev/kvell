Feature: Add Fuel

    ユーザーが投稿（Spark）に対して「薪をくべる（共感）」アクションを行い、
    数値的な評価を気にすることなく、視覚的なフィードバックのみを得られるようにする。
    また、承認欲求や競争を煽らないよう、システムは徹底して数値を隠蔽する。

    Background: System Configuration
        Given システムの "データ反映許容時間（Eventual Consistency）" は "1秒" に設定されている
        And "菊池さん" は "UserHash_A" としてシステムに認識されている

    Rule: ユーザーは視覚的フィードバックを得るが、数値はAPIレベルを含めて一切確認できない
        Example: 薪をくべた際の正常なフィードバックとデータ隠蔽
            Given タイムラインに "UserHash_B（他人）" の投稿である "Spark_X" が表示されている
            And "UserHash_A" は "Spark_X" にまだ薪をくべていない
            When "菊池さん" が "Spark_X" に薪をくべる
            Then 画面上に "着火エフェクト（パーティクル）" が表示される
            And 端末が振動に対応している場合、"微弱な振動" を発生させる
            But 画面上のどこにも "燃料のカウント数" は表示されない
            And ブラウザの開発者ツール等で確認できる "Spark_X" のAPIレスポンス等にも "燃料数" は含まれていない
            And "Spark_X" の投稿者に対して "通知" は送信されない

    Rule: 内部的な燃料カウントは「1ユーザーにつき1Sparkあたり1回」のみ加算される
        Example: 初回の薪くべ（カウント対象）
            Given タイムラインに "Spark_Y" が表示されている
            And "Spark_Y" の現在の燃料(Fuel)は "10" である
            And "UserHash_A" は "Spark_Y" にまだ薪をくべていない
            When "菊池さん" が "Spark_Y" に薪をくべる
            Then データベース上の "Spark_Y" の燃料(Fuel)は "データ反映許容時間" 以内に "11" に更新される

        Example: 2回目以降の薪くべ（連打・重複アクションのカウント除外）
            Given タイムラインに "Spark_Z" が表示されている
            And "Spark_Z" の現在の燃料(Fuel)は "20" である
            And "UserHash_A" は既に "Spark_Z" に薪をくべ済みである
            When "菊池さん" が "Spark_Z" に薪をくべる（連打する）
            Then 画面上に "着火エフェクト（パーティクル）" が表示される
            But データベース上の "Spark_Z" の燃料(Fuel)は "20" のままである
        # 解説: UXとしてエフェクトは出るが、カウントはIdempotent（冪等）に処理される

    Rule: 自分の投稿への薪くべは、体験としては可能だが集計からは除外される
        Example: 自作自演の防止（ステルス制御）
            Given タイムラインに "UserHash_A（自分）" の投稿である "Spark_My" が表示されている
            And "Spark_My" の現在の燃料(Fuel)は "0" である
            When "菊池さん" が "Spark_My" に薪をくべる
            Then 画面上に "着火エフェクト（パーティクル）" が表示される
            But データベース上の "Spark_My" の燃料(Fuel)は "0" のままである
        # 解説: ユーザーには「自分の投稿だ」と気付かせないようUIは反応するが、システムはカウントしない

    Rule: ハプティックフィードバック非対応端末ではエラーにならずログを出力する
        Example: iOS等での振動API非対応時の挙動
            Given "菊池さん" の端末は "Vibration API" に非対応である
            When "菊池さん" が他人の投稿に薪をくべる
            Then 画面上に "着火エフェクト（パーティクル）" が表示される
            But 端末は振動しない
            And アプリケーションログに "Haptic feedback not supported" 等のメッセージが出力される
