| 状態 | トリガー / 条件 | WS挙動 (Spark) | REST挙動 (Bonfire) | Toast挙動 | Timeline挙動 |
| - | - | - | - | - | - |
| 通常 | Active | 接続維持。<br>流れてくるSparkをリアルタイム描画。 | 基本はSWR任せ(revalidateOnFocus: true,<br>revalidateOnReconnect: true)。<br>wsにて昇格イベント受信時は明示的に取りに行く | なし | 快適。タイムラインが流れる |
| タブ移動(Background) | visibilitychange-> hidden | 切断猶予。<br>タブ復帰時のsocket破棄判断に使うため、時刻を記録する。 | SWR任せ | なし | なし |
| タブ復帰(Short Sleep) | hidden 継続時間が60秒未満 | なし。<br>接続は生きている前提。 | SWR任せ | なし | 何事もなかったかのよう |
| タブ復帰(Long Sleep) | hidden 継続時間が60秒以上 | 強制再接続。<br>既存Socketを破棄し、connect() を実行。(Zombie対策) | SWR任せ | なし | 何事もなかったかのよう |
| 切断確定 | Backgroundで60秒経過 | なし(jsがフリーズされてるので何も出来ない)。<br>サーバー側からconnectionが破棄される。 | SWR任せ | なし | なし |
| 完全オフライン | offline event。<br>機内モード・LANケーブル抜く・Devtoolsでの切断等、OSレベルの切断 | wsライブラリの自動再接続ロジックに従う。 | SWR任せ | Toast表示。<br>「ネットワーク接続を待機しています...」 | ネットワーク復帰で自動再接続されることがわかる |
| 電波悪化 | onLineだがwsが切断されている | 指数バックオフ+Jitterによる再試行(最大3回) | SWR任せ | Toast表示。<br>「Reconnectiong...1/3」<br>瞬断でtoastが出るのを防ぐため、ws切断状態が2s続いた場合のみ表示する。 | 再接続試行中であることがわかる |
| 完全死 | サーバーダウン orリトライ上限 | 停止 | 停止 | Toast表示Connection Error(赤いToast) | 使えない |
