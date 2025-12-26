## アノテーションコメント

TODO: 

## コマンド

### 起動
Docker
`cd ~/ws/kvell && docker-compose up -d`

FastAPI
`cd ~/ws/kvell/apps/api && PYTHONPATH=src uv run uvicorn app.main:app --port 8000 --reload`


### Dev

PBIを取得
```shell
gh issue view 31 --json title,body,url > PBI.json
```

diffを取得
```shell
git diff ${対象ディレクトリ} > diff.txt
```

変更されたファイルの中身をすべて取得
```shell
{ git diff HEAD --name-only --diff-filter=d apps/web/src; git ls-files --others --exclude-standard apps/web/src; } | sort | uniq | xargs -I{} cat "{}" > diff.txt
```

対象ディレクトリの実装ファイルをすべて取得
```shell
find ${対象ディレクトリ} -type f \( -name "*.ts" -o -name "*.js" -o -name "*.json" -o -name "*.py" \) | xargs -I{} cat "{}" > files.txt
```

コードレビュー
```md
添付インセプションデッキのPJをやってます。Agentic AIにコーディングさせて、diff.txtの結果を得ました。
添付のアーキテクチャ指示書等を参考にコードレビューをお願いします。
```

他人として投稿(焚き火化動作確認)
```shell
curl -s -X POST http://localhost:8000/api/sparks -H "Content-Type: application/json" -H "X-Forwarded-For: 10.0.0.6" -d '{"content": "ユーザーH: おやすみなさい https://sakurazaka46.com/images/14/0ca/76962b5f60d141f0a28b8e62f7abf-02.jpg"}'
```


## TODO

- 勢い表示の実装(B/Eで計算して返す必要がある) -> 当面は消しといても良いかも。MVPじゃなさそう。
- 未読数の実装
- B/E側でのspark->bonfire昇格時に、元のsparkをws配信しないロジックが入ってなさそう。sparkに薪くべ->昇格時に、一旦F/E側でそのsparkが消えはするんだけど、リロードするともう一度timelineに入ってくる。: 実装済み
- headerのshareボタン効いてなさそう
- timelineのws、フォーカス外すと切れるので再接続ロジックを入れる: 実装済み
  - 接続が切れるとすぐに「サーバーに接続できません」となるので、ローカルに持ってるsparkは表示し続ける。接続切れはトースト等工夫した方が良い
- bonfireのサンプルカードはリストの末尾に常においておく: 実装済み
- spark投稿の改善。
  - 一定時間経過で消える旨記載
  - モーダルじゃないほうが良いかも?モバイルで投稿しづらい
  - Shift+Enterで送信?
- ws仕様まとめ。
  - チャネルはsparks:postedとsparks:update
  - updateは昇格時(spark->kingling, spark->bonfire)のみブロードキャスト
  - bonfireへの薪くべはws配信しない。
  - sparkはF/E側でdecayAtになったらDOMからクリーンナップ。
  - bonfireはdecayAtになってもリロードするまで消えない。
    - bonfireは薪くべ&レスによる延命があるため、このイベントをws配信してるとトラフィックが死ぬため。
    - そもそもUX的にもbonfire生成はある程度リアルタイムがいいけど、消滅はいつでもいい
    - decay直前にRESTで最新のdecayAtを取りに行くとかも考えたが、通信失敗時のフォールバックが大変なので採用せず。
    - bonfire詳細に入ったら更新される(RESTで取るため。けどこれfastapiのdocsにエンドポイント見当たらないな。)んだよね...?ここは要確認。
- 焚き火化閾値の調整



## React

勉強用。

### 原理原則

**UI=f(State)**。

- stateを作るのがuseState()。f()はtsxのこと。Stateが更新されるとf()が実行される。これを**再描画**と呼ぶ。
- 副作用とは、UI描画以外のすべての処理（通信、DOM変更、タイマー、State更新など）のこと。
- useEffect()は、f()による描画が終わった後に実行される「副作用の予約」。どのタイミングで実行するかは、第二引数で決まる。

```tsx
const Component = () => {
  const [data, setData] = useState(null); // State

  // 副作用の予約（描画が終わったら通信して、Stateを更新しろ）
  useEffect(() => {
    fetch('/api').then(res => setData(res)); 
  }, []);

  return <div>{data}</div>; // UI = f(State)
};
```

### useEffect

```ts
useEffect(callback(), [監視対象])
```

- 監視対象の変更を検知すると、callback()を実行する。
- 監視対象が空の場合はコンポーネントの生成時に一度だけ実行する。

### useState

```ts
const [sparks, setSparks] = useState<型>(初期値);

setSparks(1) // にするとsparks=1になる
setSparks(callback( return 1 ) ) // とすると同じくspark=1になる
setSparks(callback((arg) => {})) // とするとargには最新のsparkが渡る(Reactが暗黙的に渡す)。

```
- setXX()はuseStateで作成したState(今回はsparks)を更新するための関数。
- setXX(値)とすることもできるし、setXX(() => {return})とすることもできる。
