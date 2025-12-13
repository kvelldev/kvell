Feature: Spark Lifecycle & Promotion Logic
    ユーザーの熱量に応じて種火(Spark)の生存時間を延長し、条件を満たしたものを焚き火(Bonfire)へ昇格させる。

    Background: System Configuration
        Given システムの"レスによる焚き火延長時間"は"3時間"に設定されている
        And システムの"薪による焚き火延長時間"は"10分"に設定されている


    # Genearation
    Rule: 焚き火に昇格した種火は焚き火エリアに現れる
        Example: リアルタイムでの焚き火出現
            Given ユーザーが"メイン画面"を開いている
            When "Spark A"が"焚き火昇格条件"を満たし"Bonfire A"へと昇格した
            Then "Bonfire A"が"焚き火エリア"に現れる

        # Burn
    Rule: 焚き火はアクションがある限り燃え続ける
        Example: 焚き火状態でさらに薪がくべられた場合
            Given "Bonfire B"が存在する
            When 新たなユーザーが薪をくべた
            Then "Bonfire B"の有効期限(decayAt)は "decayAt" + "薪による焚き火延長時間"に再設定される
        Example: 消えかけの焚き火にレスがあった場合
            Given "Bonfire C"が存在する
            And "Bonfire C"の残り寿命が"レスによる焚き火延長時間"よりも短い
            When "Bonfire C"にレスがあった
            Then "Bonfire C"の有効期限(decayAt)は"現在時刻" + "レスによる焚き火延長時間"に再設定される
        Example: 十分に燃えている焚き火にレスがあった場合
            Given "Bonfire D"が存在する
            And "Bonfire D"の残り寿命が"レスによる焚き火延長時間"よりも長い
            When "Bonfire D" にレスがあった
            Then "Bonfire D"の有効期限(decayAt)は"decayAt"のままである

        # Decay
    Rule: 寿命が尽きた焚き火は鎮火し、ヘッダーから去る
        Example: 時間経過による鎮火
            Given "Bonfire E" が "焚き火エリア" に表示されている
            When "Bonfire E" の有効期限(decayAt)を経過した
            Then "Bonfire E" は "焚き火エリア" から消失する
